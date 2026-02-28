#!/usr/bin/env python
import json
import logging
import os.path
import zipfile


from whoosh import fields
from whoosh.fields import Schema
from whoosh.filedb.filestore import FileStorage

from alfanous import text_processing


logging.basicConfig(level=logging.INFO)


class Transformer:
    def __init__(self, index_path, resource_path, translations_path=None):
        if not (os.path.exists(index_path)):
            os.makedirs(index_path)

        self.index_path = index_path
        self.resource_path = resource_path
        self.translations_path = translations_path

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

    def load_translations(self):
        """Load translation files from the translations directory"""
        translations = {}
        
        if not self.translations_path or not os.path.exists(self.translations_path):
            logging.info("No translations path provided or path doesn't exist, skipping translations")
            return translations
        
        # Find all translation zip files
        trans_files = [f for f in os.listdir(self.translations_path) if f.endswith('.trans.zip')]
        
        for trans_file in trans_files:
            trans_path = os.path.join(self.translations_path, trans_file)
            
            try:
                # Extract field name: en.shakir.trans.zip -> translation_en_shakir
                field_name = 'translation_' + trans_file.replace('.trans.zip', '').replace('.', '_')
                
                # Load translation lines
                with zipfile.ZipFile(trans_path, 'r') as z:
                    # Find the text file
                    txt_files = [name for name in z.namelist() if name.endswith('.txt')]
                    if not txt_files:
                        logging.warning(f"No text file found in {trans_file}")
                        continue
                    
                    with z.open(txt_files[0]) as f:
                        content = f.read().decode('utf-8')
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        
                        if len(lines) != 6236:
                            logging.warning(f"Expected 6236 verses in {trans_file} but got {len(lines)}")
                            continue
                        
                        translations[field_name] = lines
                        logging.info(f"Loaded translation: {field_name} ({len(lines)} verses)")
                        
            except Exception as e:
                logging.error(f"Error loading {trans_file}: {e}")
        
        return translations

    def transfer(self, ix, tablename="aya"):
        data_file = open(f"{self.resource_path}{tablename}.json")
        data_list = json.load(data_file)

        # Load translations if processing aya table
        translations = {}
        if tablename == "aya":
            translations = self.load_translations()

        logging.info(f"writing documents in index (total: {len(data_list)}) ....")
        writer = ix.writer()

        cpt = 0

        fields_mapping = {f["name"]: f["search_name"] for f in self.get_fields(tablename)}

        for line in data_list:
            doc = {fields_mapping[k]: v for k, v in line.items() if k in fields_mapping}
            
            # Add translation fields dynamically
            if tablename == "aya" and translations:
                gid = line.get('gid')
                if gid and 1 <= gid <= 6236:
                    for field_name, lines in translations.items():
                        # Check if field is in schema
                        if field_name in ix.schema:
                            doc[field_name] = lines[gid - 1]  # gid is 1-indexed
            
            writer.add_document(**doc)
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
