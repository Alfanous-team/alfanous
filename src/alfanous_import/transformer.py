#!/usr/bin/env python
import json
import logging
import os.path


from whoosh import fields
from whoosh.fields import Schema
from whoosh.filedb.filestore import FileStorage

from alfanous import text_processing


logging.basicConfig(level=logging.INFO)


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

            params = {k: getattr(text_processing, v) if k == 'analyzer' else v
                      for k, v in line.items()
                      if k in ['analyzer', 'stored',  'unique']
                      and v
                      }
            kwargs[search_name] = getattr(fields, type)(**params)

        return Schema(**kwargs)

    def transfer(self, ix, tablename="aya"):
        data_file = open(f"{self.resource_path}{tablename}.json")
        data_list = json.load(data_file)

        logging.info(f"writing documents in index (total: {len(data_list)}) ....")
        writer = ix.writer()

        cpt = 0

        fields_mapping = {f["name"]: f["search_name"] for f in self.get_fields(tablename)}

        for line in data_list:
            writer.add_document(
                **{fields_mapping[k]: v for k, v in line.items() if k in fields_mapping}
            )
            cpt += 1
            if not cpt % 1559:
                logging.info(f" - milestone:  {cpt} ( {cpt * 100 / len(data_list)}% )")

        logging.info("done.")
        writer.commit()

    def build_docindex(self, schema, tablename="aya"):
        assert schema, "schema is empty"
        ix = FileStorage(self.index_path).create_index(schema)
        self.transfer(ix, tablename)
        return "OK"


if __name__ == "__main__":
    T = Transformer(index_path="../../indexes/main/", resource_path="../alfanous/resources/")
