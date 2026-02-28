#!/usr/bin/env python3
"""
Script to add translation field definitions to fields.json
"""

import json
import os

def main():
    fields_json_path = 'src/alfanous/resources/fields.json'
    
    # Load fields.json
    print("Loading fields.json...")
    with open(fields_json_path, 'r', encoding='utf-8') as f:
        fields = json.load(f)
    
    print(f"Loaded {len(fields)} field definitions")
    
    # Find max ID
    max_id = max(f.get('id', 0) for f in fields)
    print(f"Max field ID: {max_id}")
    
    # Define new translation fields
    new_fields = [
        {
            "id": max_id + 1,
            "name": "translation_en_shakir",
            "name_arabic": "ترجمة_شاكر",
            "table_name": "aya",
            "comment": "English translation by Mohammad Habib Shakir",
            "type": "TEXT",
            "stored": True,
            "is_spellchecked": None,
            "unique": None,
            "source": "tanzil.net",
            "search_name": "translation_en_shakir",
            "analyzer": None,
            "spelling": False,
            "field_boost": None
        },
        {
            "id": max_id + 2,
            "name": "translation_en_transliteration",
            "name_arabic": "ترجمة_صوتية",
            "table_name": "aya",
            "comment": "English transliteration of Quran text",
            "type": "TEXT",
            "stored": True,
            "is_spellchecked": None,
            "unique": None,
            "source": "tanzil.net",
            "search_name": "translation_en_transliteration",
            "analyzer": None,
            "spelling": False,
            "field_boost": None
        }
    ]
    
    print(f"\nAdding {len(new_fields)} new field definitions:")
    for field in new_fields:
        print(f"  - {field['name']} (ID: {field['id']})")
    
    # Add new fields
    fields.extend(new_fields)
    
    # Create backup
    backup_path = fields_json_path + '.backup'
    print(f"\nCreating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(json.load(open(fields_json_path, 'r', encoding='utf-8')), f, ensure_ascii=False, indent=2)
    
    # Save updated fields.json
    print(f"Saving updated fields.json...")
    with open(fields_json_path, 'w', encoding='utf-8') as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Successfully added {len(new_fields)} translation field definitions")
    print(f"Total fields: {len(fields)}")

if __name__ == '__main__':
    main()
