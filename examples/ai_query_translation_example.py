#!/usr/bin/env python3
# coding: utf-8

"""
AI Query Translation Rules Usage Example
========================================

This example demonstrates how to access and use the AI query translation rules
file that contains patterns for translating natural language queries into
Alfanous query syntax.

The rules file is stored at: src/alfanous/resources/ai_query_translation_rules.txt
"""

import os
from alfanous import paths


def load_ai_rules():
    """
    Load the AI query translation rules from the resources directory.
    
    Returns:
        str: The content of the AI rules file
    """
    rules_path = paths.AI_QUERY_TRANSLATION_RULES_FILE
    
    if not os.path.exists(rules_path):
        print(f"ERROR: AI rules file not found at {rules_path}")
        return None
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content


def display_rules_summary(rules_content):
    """
    Display a summary of the AI rules content.
    
    Args:
        rules_content (str): The content of the rules file
    """
    if not rules_content:
        return
    
    lines = rules_content.split('\n')
    
    print("=" * 80)
    print("AI QUERY TRANSLATION RULES - SUMMARY")
    print("=" * 80)
    print()
    
    # Extract and display the table of contents
    in_toc = False
    toc_lines = []
    
    for line in lines:
        if "TABLE OF CONTENTS" in line:
            in_toc = True
            continue
        elif in_toc and line.startswith("==="):
            break
        elif in_toc and line.strip() and not line.startswith("="):
            toc_lines.append(line.strip())
    
    print("TABLE OF CONTENTS:")
    print("-" * 80)
    for toc_line in toc_lines:
        if toc_line:
            print(f"  {toc_line}")
    print()
    
    # Display file statistics
    print(f"Total lines: {len(lines)}")
    print(f"File size: {len(rules_content):,} characters")
    print()


def extract_examples(rules_content):
    """
    Extract and display example query translations from the rules.
    
    Args:
        rules_content (str): The content of the rules file
    """
    if not rules_content:
        return
    
    print("=" * 80)
    print("SAMPLE QUERY TRANSLATION EXAMPLES")
    print("=" * 80)
    print()
    
    lines = rules_content.split('\n')
    
    # Find the "Natural Language Translation Patterns" section
    in_examples = False
    example_count = 0
    max_examples = 15
    
    for i, line in enumerate(lines):
        if "6. NATURAL LANGUAGE TRANSLATION PATTERNS" in line:
            in_examples = True
            continue
        
        if in_examples and example_count < max_examples:
            # Look for pattern lines (contain both natural language and Alfanous query)
            if " | " in line and not line.startswith("-") and not line.startswith("="):
                parts = line.split("|")
                if len(parts) == 2:
                    natural = parts[0].strip()
                    query = parts[1].strip()
                    if natural and query and natural != "Natural Language" and natural != "Alfanous Query":
                        print(f"{example_count + 1}. Natural Language: {natural}")
                        print(f"   Alfanous Query:    {query}")
                        print()
                        example_count += 1
        
        if "7. COMMON QUERY EXAMPLES" in line:
            break
    
    print(f"(Showing {example_count} examples from the full rules file)")
    print()


def main():
    """Main function to demonstrate AI rules usage."""
    
    print()
    print("=" * 80)
    print("ALFANOUS AI QUERY TRANSLATION RULES - DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Load the rules file
    print("Loading AI query translation rules...")
    rules_content = load_ai_rules()
    
    if not rules_content:
        print("Failed to load rules file. Make sure Alfanous is properly installed.")
        return
    
    print("✓ Rules file loaded successfully!")
    print()
    
    # Display summary
    display_rules_summary(rules_content)
    
    # Extract and display examples
    extract_examples(rules_content)
    
    # Show how AI systems can use these rules
    print("=" * 80)
    print("HOW AI SYSTEMS CAN USE THESE RULES")
    print("=" * 80)
    print()
    print("1. Load the rules file using paths.AI_QUERY_TRANSLATION_RULES_FILE")
    print("2. Parse the rules to extract translation patterns")
    print("3. Match user's natural language query against the patterns")
    print("4. Generate appropriate Alfanous query syntax")
    print("5. Execute the query using the Alfanous API")
    print()
    print("Example workflow:")
    print('  User input:  "Find verses about patience in Sura Al-Baqarah"')
    print('  AI translates to: صبر + سورة:البقرة')
    print('  Execute: api.search("صبر + سورة:البقرة")')
    print()
    
    # Show practical integration example
    print("=" * 80)
    print("PRACTICAL INTEGRATION EXAMPLE")
    print("=" * 80)
    print()
    print("```python")
    print("from alfanous import api, paths")
    print("import os")
    print()
    print("# Load AI rules")
    print("with open(paths.AI_QUERY_TRANSLATION_RULES_FILE, 'r') as f:")
    print("    ai_rules = f.read()")
    print()
    print("# Your AI system uses the rules to translate:")
    print('# "Find verses about patience" → "صبر"')
    print()
    print("# Execute the translated query")
    print('results = api.search("صبر", page=1, perpage=5)')
    print()
    print("# Process results")
    print('if results["error"]["code"] == 0:')
    print('    print(f"Found {results[\'search\'][\'interval\'][\'total\']} results")')
    print("    for aya in results['search']['ayas']['results']:")
    print("        print(f'  Sura {aya[\"sura_name\"]}, Verse {aya[\"aya_id\"]}')")
    print("```")
    print()
    
    print("=" * 80)
    print("For complete documentation, view the full rules file at:")
    print(f"  {paths.AI_QUERY_TRANSLATION_RULES_FILE}")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
