#!/usr/bin/env python3
# coding: utf-8

"""
Test AI Query Translation Rules File
"""

import os
from alfanous import paths


def test_ai_rules_file_exists():
    """Test that the AI query translation rules file exists."""
    assert hasattr(paths, 'AI_QUERY_TRANSLATION_RULES_FILE'), \
        "AI_QUERY_TRANSLATION_RULES_FILE constant not found in paths module"
    
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    assert os.path.exists(rules_path), \
        f"AI rules file does not exist at {rules_path}"


def test_ai_rules_file_readable():
    """Test that the AI query translation rules file can be read."""
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert len(content) > 0, "AI rules file is empty"
    assert "AI RULES FOR TRANSLATING HUMAN LANGUAGE TO ALFANOUS QUERY SYNTAX" in content, \
        "AI rules file header not found"


def test_ai_rules_file_structure():
    """Test that the AI query translation rules file has expected structure."""
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key sections
    assert "TABLE OF CONTENTS" in content, "Table of contents not found"
    assert "BASIC OPERATORS" in content, "Basic operators section not found"
    assert "ADVANCED FEATURES" in content, "Advanced features section not found"
    assert "ARABIC-SPECIFIC FEATURES" in content, "Arabic-specific features section not found"
    assert "FIELD NAMES REFERENCE" in content, "Field names reference not found"
    assert "NATURAL LANGUAGE TRANSLATION PATTERNS" in content, \
        "Natural language translation patterns not found"
    assert "COMMON QUERY EXAMPLES" in content, "Common query examples not found"


def test_ai_rules_contains_operators():
    """Test that the AI rules file documents key operators."""
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for documented operators
    assert "AND OPERATOR" in content, "AND operator documentation not found"
    assert "OR OPERATOR" in content, "OR operator documentation not found"
    assert "NOT OPERATOR" in content, "NOT operator documentation not found"
    assert "PHRASE SEARCH" in content, "Phrase search documentation not found"
    assert "WILDCARDS" in content, "Wildcards documentation not found"


def test_ai_rules_contains_arabic_features():
    """Test that the AI rules file documents Arabic-specific features."""
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Arabic-specific features
    assert "SYNONYMS" in content, "Synonyms documentation not found"
    assert "ANTONYMS" in content, "Antonyms documentation not found"
    assert "DERIVATIONS" in content, "Derivations documentation not found"
    assert "ROOT-LEVEL DERIVATIONS" in content, "Root derivations documentation not found"
    assert "TASHKIL" in content or "diacritics" in content.lower(), \
        "Tashkil/diacritics documentation not found"


def test_ai_rules_contains_field_names():
    """Test that the AI rules file documents field names."""
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key field names (both Arabic and English)
    assert "sura" in content.lower() or "سورة" in content, \
        "Sura field documentation not found"
    assert "aya" in content.lower() or "آية" in content, \
        "Aya field documentation not found"


def test_ai_rules_contains_examples():
    """Test that the AI rules file contains practical examples."""
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for example queries with Arabic content
    # The file should contain actual query examples
    lines = content.split('\n')
    
    # Count lines that look like examples (contain "→" or "|")
    example_lines = [line for line in lines if "→" in line or 
                     ("|" in line and not line.startswith("=") and not line.startswith("-"))]
    
    assert len(example_lines) > 20, \
        f"Expected more than 20 example lines, found {len(example_lines)}"


if __name__ == "__main__":
    # Run tests
    test_ai_rules_file_exists()
    print("✓ AI rules file exists")
    
    test_ai_rules_file_readable()
    print("✓ AI rules file is readable")
    
    test_ai_rules_file_structure()
    print("✓ AI rules file has expected structure")
    
    test_ai_rules_contains_operators()
    print("✓ AI rules file documents operators")
    
    test_ai_rules_contains_arabic_features()
    print("✓ AI rules file documents Arabic features")
    
    test_ai_rules_contains_field_names()
    print("✓ AI rules file documents field names")
    
    test_ai_rules_contains_examples()
    print("✓ AI rules file contains examples")
    
    print("\nAll tests passed!")
