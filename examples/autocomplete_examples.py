#!/usr/bin/env python3
"""
Autocomplete Examples for Alfanous API

This script demonstrates how to use the autocomplete feature
to get phrase suggestions that actually exist in the Quran.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from alfanous import api

print("=" * 70)
print("Alfanous Autocomplete Examples")
print("=" * 70)

# Example 1: Basic autocomplete with a partial phrase
print("\n1. Basic autocomplete - completing a partial phrase")
print("-" * 70)
print("Query: 'الحمد ل' (partial last word)")
result = api.autocomplete("الحمد ل", limit=10)
print(f"Status: {result['error']['msg']}")
print(f"Actual Quran phrases starting with query ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'][:10], 1):
    print(f"  {i}. {suggestion}")

# Example 2: Autocomplete with complete phrase
print("\n2. Autocomplete with complete phrase")
print("-" * 70)
print("Query: 'الحمد لله'")
result = api.autocomplete("الحمد لله", limit=5)
print(f"Actual Quran phrases ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'], 1):
    print(f"  {i}. {suggestion}")

# Example 3: Autocomplete with partial word in longer phrase
print("\n3. Longer phrase with partial last word")
print("-" * 70)
print("Query: 'بسم الله الر'")
result = api.autocomplete("بسم الله الر", limit=5)
print(f"Actual Quran phrases ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'], 1):
    print(f"  {i}. {suggestion}")

# Example 4: Using do() method directly with flags
print("\n4. Using api.do() method directly")
print("-" * 70)
print("Query: 'رب'")
result = api.do({
    "action": "autocomplete",
    "query": "رب",
    "unit": "aya",
    "limit": 8
})
print(f"Actual Quran phrases ({len(result['autocomplete'])}):")
for i, suggestion in enumerate(result['autocomplete'], 1):
    print(f"  {i}. {suggestion}")

# Example 5: Autocomplete for common Quranic phrases
print("\n5. Autocomplete for common Quranic phrase beginning")
print("-" * 70)
print("Query: 'يا أيها الذين آم'")
result = api.autocomplete("يا أيها الذين آم", limit=5)
print(f"Actual Quran phrases ({len(result['autocomplete'])}):")
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
print("- Returns actual phrases that exist in the Quran text")
print("- Supports partial word completion (e.g., 'الحمد ل' → 'الحمد لله ...')")
print("- Default limit is 10 suggestions, but can be customized")
print("- Works with Arabic text")
print("=" * 70)
