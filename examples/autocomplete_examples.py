#!/usr/bin/env python3
"""
Autocomplete Examples for Alfanous API

This script demonstrates how to use the new autocomplete feature
to get keyword suggestions for phrases.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from alfanous import api

print("=" * 70)
print("Alfanous Autocomplete Examples")
print("=" * 70)

# Example 1: Basic autocomplete with a phrase
print("\n1. Basic autocomplete - completing a phrase")
print("-" * 70)
print("Query: 'الحمد ل'")
result = api.autocomplete("الحمد ل", limit=10)
print(f"Status: {result['error']['msg']}")
print(f"Suggestions ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'][:10], 1):
    print(f"  {i}. {suggestion}")

# Example 2: Autocomplete with single word
print("\n2. Single word autocomplete")
print("-" * 70)
print("Query: 'رسول'")
result = api.autocomplete("رسول", limit=10)
print(f"Suggestions ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'], 1):
    print(f"  {i}. {suggestion}")

# Example 3: Autocomplete with different limits
print("\n3. Custom limit - getting top 5 suggestions")
print("-" * 70)
print("Query: 'بسم الله'")
result = api.autocomplete("بسم الله", limit=5)
print(f"Suggestions ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'], 1):
    print(f"  {i}. {suggestion}")

# Example 4: Using do() method directly with flags
print("\n4. Using api.do() method directly")
print("-" * 70)
print("Query: 'ال'")
result = api.do({
    "action": "autocomplete",
    "query": "ال",
    "unit": "aya",
    "limit": 8
})
print(f"Suggestions ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'], 1):
    print(f"  {i}. {suggestion}")

# Example 5: Autocomplete for common Quranic phrases
print("\n5. Autocomplete for common Quranic phrase beginning")
print("-" * 70)
print("Query: 'يا أيها الذين آم'")
result = api.autocomplete("يا أيها الذين آم", limit=10)
print(f"Suggestions ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'], 1):
    print(f"  {i}. {suggestion}")

# Example 6: Empty query handling
print("\n6. Empty query handling")
print("-" * 70)
print("Query: ''")
result = api.autocomplete("", limit=10)
print(f"Suggestions: {result['autocomplete']}")
print(f"Count: {len(result['autocomplete'])}")

print("\n" + "=" * 70)
print("Examples completed successfully!")
print("=" * 70)
print("\nNotes:")
print("- The autocomplete feature accepts phrases (multiple words)")
print("- It returns the top N relevant keywords based on the last word prefix")
print("- Default limit is 10 keywords, but can be customized")
print("- Works with Arabic text")
print("=" * 70)
