#!/usr/bin/env python3
"""
Script to add translation data to aya.json
This adds translation fields to the main index data file
"""

import json
import zipfile
import os
import re

def load_translation(zip_path):
    """Load translation text from a .trans.zip file"""
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Get translation properties
        with z.open('translation.properties') as f:
            props_content = f.read().decode('utf-8')
            props = {}
            for line in props_content.split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    props[key.strip()] = value.strip()
        
        # Get translation text
        txt_file = props.get('file', None)
        if not txt_file:
            # Try to find .txt file
            txt_files = [name for name in z.namelist() if name.endswith('.txt')]
            if txt_files:
                txt_file = txt_files[0]
            else:
                raise ValueError(f"No text file found in {zip_path}")
        
        with z.open(txt_file) as f:
            content = f.read().decode('utf-8')
            # lineDelimiter in properties is the string '\n', we need actual newline
            lines = content.split('\n')
            # Filter out empty lines
            lines = [line.strip() for line in lines if line.strip()]
            
    return lines, props

def get_field_name(filename):
    """Extract field name from filename: en.shakir.trans.zip -> translation_en_shakir"""
    # Remove .trans.zip extension
    name = filename.replace('.trans.zip', '')
    # Replace dots with underscores and prefix with 'translation_'
    field_name = 'translation_' + name.replace('.', '_')
    return field_name

def main():
    # Paths
    aya_json_path = 'src/alfanous/resources/aya.json'
    translations_dir = 'store/Translations/'
    
    # Load aya.json
    print("Loading aya.json...")
    with open(aya_json_path, 'r', encoding='utf-8') as f:
        aya_data = json.load(f)
    
    print(f"Loaded {len(aya_data)} verses")
    
    # Find all translation files
    trans_files = [f for f in os.listdir(translations_dir) if f.endswith('.trans.zip')]
    print(f"\nFound {len(trans_files)} translation files:")
    for tf in trans_files:
        print(f"  - {tf}")
    
    # Process each translation
    for trans_file in trans_files:
        trans_path = os.path.join(translations_dir, trans_file)
        field_name = get_field_name(trans_file)
        
        print(f"\nProcessing {trans_file} -> {field_name}")
        
        try:
            lines, props = load_translation(trans_path)
            
            if len(lines) != 6236:
                print(f"  WARNING: Expected 6236 verses but got {len(lines)}")
                continue
            
            # Add translation to each verse
            for i, verse in enumerate(aya_data):
                verse[field_name] = lines[i]
            
            print(f"  ✓ Added {len(lines)} translation verses")
            print(f"  Translation info: {props.get('name', 'N/A')} ({props.get('language', 'N/A')})")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Save updated aya.json
    backup_path = aya_json_path + '.backup'
    print(f"\nCreating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(aya_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saving updated aya.json...")
    with open(aya_json_path, 'w', encoding='utf-8') as f:
        json.dump(aya_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Successfully updated aya.json with {len(trans_files)} translations")
    print(f"New fields: {', '.join([get_field_name(tf) for tf in trans_files])}")

if __name__ == '__main__':
    main()
