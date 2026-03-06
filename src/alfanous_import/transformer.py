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

# Translation IDs whose text is embedded into the main QSE index as named fields.
# Keys are the translation zip IDs; values are the source field names used in
# fields.json (the `name` attribute that maps to a `search_name` in the schema).
_NESTED_TRANSLATIONS = {
    "en.transliteration": "en_transliteration",
    "ar.jalalayn": "ar_jalalayn",
}


def _load_nested_translations(translations_store_path):
    """Return a ``{gid: {field_name: text}}`` mapping loaded from translation zips.

    Only translations listed in :data:`_NESTED_TRANSLATIONS` and whose zip file
    exists under *translations_store_path* are loaded.  Missing zips are skipped
    with a warning rather than raising an error so that a partial translations
    store still produces a usable index.
    """
    from alfanous_import.zekr_model_reader.main import TranslationModel

    result = {}  # {gid: {field_name: text}}
    for trans_id, field_name in _NESTED_TRANSLATIONS.items():
        zip_path = os.path.join(translations_store_path, f"{trans_id}.trans.zip")
        if not os.path.exists(zip_path):
            logging.warning("Nested translation zip not found, skipping: %s", zip_path)
            continue
        try:
            tm = TranslationModel(zip_path)
            props = tm.translation_properties()
            lines = tm.translation_lines(props)
            if len(lines) != QURAN_TOTAL_VERSES:
                logging.warning(
                    "Translation %s has %d lines (expected %d), skipping",
                    trans_id, len(lines), QURAN_TOTAL_VERSES,
                )
                continue
            for i, text in enumerate(lines):
                gid = i + 1
                if gid not in result:
                    result[gid] = {}
                result[gid][field_name] = text
            logging.info("Loaded nested translation: %s (%d verses)", trans_id, len(lines))
        except (OSError, ValueError, AssertionError) as exc:
            logging.warning("Failed to load translation %s: %s", trans_id, exc)
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

        # Optionally embed translation text from zip files into each aya document.
        nested = {}
        if translations_store_path and tablename == "aya":
            nested = _load_nested_translations(translations_store_path)

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
            # Merge nested translation fields when available
            if nested:
                gid = line.get("gid")
                if gid is not None:
                    for field_name, text in nested.get(gid, {}).items():
                        if field_name in fields_mapping:
                            for search_name in fields_mapping[field_name]:
                                doc[search_name] = text
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
