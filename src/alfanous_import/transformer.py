#!/usr/bin/env python
import json
import logging
import os
import os.path


from whoosh import fields
from whoosh.fields import Schema
from whoosh.filedb.filestore import FileStorage

from alfanous import text_processing
from alfanous.constants import QURAN_TOTAL_VERSES


logging.basicConfig(level=logging.INFO)


def _load_all_translations(translations_store_path):
    """Return a mapping ``{trans_id: {"lines": [...], "lang": ..., "author": ...}}``
    for every ``.trans.zip`` found under *translations_store_path*.

    Each entry's ``"lines"`` list has exactly :data:`QURAN_TOTAL_VERSES` items,
    indexed from 0 (gid = index + 1).  Zips that cannot be parsed or have the
    wrong line count are skipped with a warning.
    """
    from alfanous_import.zekr_model_reader.main import TranslationModel

    result = {}
    if not os.path.isdir(translations_store_path):
        logging.warning("Translations store path not found, skipping: %s", translations_store_path)
        return result
    for filename in sorted(os.listdir(translations_store_path)):
        if not filename.endswith(".trans.zip"):
            continue
        zip_path = os.path.join(translations_store_path, filename)
        try:
            tm = TranslationModel(zip_path)
            props = tm.translation_properties()
            lines = tm.translation_lines(props)
            if len(lines) != QURAN_TOTAL_VERSES:
                logging.warning(
                    "Translation %s has %d lines (expected %d), skipping",
                    props.get("id", filename), len(lines), QURAN_TOTAL_VERSES,
                )
                continue
            trans_id = props["id"]
            result[trans_id] = {
                "lines": lines,
                "lang": props.get("language", ""),
                "author": props.get("name", ""),
            }
            logging.info("Loaded translation: %s (%d verses)", trans_id, len(lines))
        except (OSError, ValueError, AssertionError, KeyError) as exc:
            logging.warning("Failed to load translation %s: %s", filename, exc)
    return result


class Transformer:
    def __init__(self, index_path, resource_path):
        if not (os.path.exists(index_path)):
            os.makedirs(index_path)

        self.index_path = index_path
        self.resource_path = resource_path

    def print_to_json(self, d, filename):
        with  open(f"{self.resource_path}{filename}.generated.json", "w") as f:
            import json
            json.dump(d, f, indent=4, sort_keys=True, ensure_ascii=False)

        return "OK"

    def get_fields(self, tablename):
        field_file = open(f"{self.resource_path}fields.json")
        return [field for field in json.load(field_file) if field["table_name"] == tablename]

    def build_schema(self, tablename):
        """build schema from field table"""

        kwargs = {}
        for line in self.get_fields(tablename):
            search_name = line['search_name']
            assert search_name, "search name should not be null!"
            type = str(line['type']).upper() or "STORED"

            params = {
                      k: getattr(text_processing, v) if k == 'analyzer' else v
                      for k, v in line.items()
                      if k in ['analyzer', 'stored',  'unique', 'spelling']
                      and v
                      }
            kwargs[search_name] = getattr(fields, type)(**params)

        return Schema(**kwargs)

    def transfer(self, ix, tablename="aya", translations_store_path=None):
        data_file = open(f"{self.resource_path}{tablename}.json")
        data_list = json.load(data_file)

        logging.info(f"writing documents in index (total: {len(data_list)}) ....")
        writer = ix.writer()

        cpt = 0

        # Build a mapping from source field name → list of search field names.
        # A single source field (e.g. "standard") may feed multiple index fields
        # with different analyzers (e.g. aya, aya_ac, aya_fuzzy).
        from collections import defaultdict
        fields_mapping: dict = defaultdict(list)
        for f in self.get_fields(tablename):
            fields_mapping[f["name"]].append(f["search_name"])

        # Load all translation zips if a store path was provided.
        # translations: {trans_id: {"lines": [6236 texts], "lang": ..., "author": ...}}
        translations = {}
        if translations_store_path and tablename == "aya":
            translations = _load_all_translations(translations_store_path)

        for line in data_list:
            # Normalize chapter/topic/subtopic
            if tablename == "aya":
                line = {**line,
                        'chapter': line.get('chapter', '').strip(),
                        'topic': line.get('topic', '').strip(),
                        'subtopic': line.get('subtopic', '').strip()}
            doc = {}
            for k, v in line.items():
                if k in fields_mapping:
                    for search_name in fields_mapping[k]:
                        doc[search_name] = v

            if translations and tablename == "aya":
                # Write parent aya doc + child translation docs as a nested group.
                gid = line.get("gid")
                doc["kind"] = "aya"
                writer.start_group()
                writer.add_document(**doc)
                if gid is not None:
                    idx = gid - 1  # 0-based index into translation lines
                    for trans_id, tdata in translations.items():
                        writer.add_document(
                            kind="translation",
                            gid=gid,
                            trans_id=trans_id,
                            trans_lang=tdata["lang"],
                            trans_text=tdata["lines"][idx],
                            trans_author=tdata["author"],
                        )
                writer.end_group()
            else:
                writer.add_document(**doc)

            cpt += 1
            if not cpt % 1559:
                logging.info(f" - milestone:  {cpt} ( {cpt * 100 / len(data_list)}% )")

        logging.info("done.")
        writer.commit()

    def build_docindex(self, schema, tablename="aya", translations_store_path=None):
        assert schema, "schema is empty"
        ix = FileStorage(self.index_path).create_index(schema)
        self.transfer(ix, tablename, translations_store_path=translations_store_path)
        return "OK"


if __name__ == "__main__":
    T = Transformer(index_path="../../indexes/main/", resource_path="../alfanous/resources/")
