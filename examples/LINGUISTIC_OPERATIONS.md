# Linguistic Operations in Alfanous API

This document describes the new linguistic operations feature added to the Alfanous API.

## Overview

The Alfanous API now supports linguistic operations on Arabic text through a new `linguistic` action. This feature provides two main operations:

1. **Vocalize (تشكيل)**: Add diacritical marks (tashkeel) to Arabic text
2. **Derive (اشتقاق)**: Find roots and derivations of Arabic words

## Usage

### Using the `linguistic()` Function

The simplest way to use linguistic operations is through the `alfanous.linguistic()` function:

```python
import alfanous.api as api

# Vocalize text (add diacritics)
result = api.linguistic('الحمد لله', operation='vocalize')
print(result['linguistic']['vocalized'])  # الْحَمْدُ لِلَّهِ

# Find root and derivations
result = api.linguistic('الحمد', operation='derive')
word_info = result['linguistic']['words'][0]
print(f"Root: {word_info['root']}")  # Root: حمد
print(f"Lemma: {word_info['lemma']}")  # Lemma: حمد
```

### Using the `do()` Function

You can also use the low-level `do()` API:

```python
import alfanous.api as api

result = api.do({
    "action": "linguistic",
    "query": "الحمد لله",
    "operation": "vocalize"  # or "derive"
})
```

## API Reference

### `alfanous.linguistic(text, operation='vocalize')`

Perform linguistic operations on Arabic text.

**Parameters:**
- `text` (str): Arabic text to process
- `operation` (str): Operation to perform. Options:
  - `'vocalize'`: Add diacritical marks (default)
  - `'derive'`: Find roots and derivations

**Returns:**
- Dictionary with the following structure for `vocalize`:
  ```python
  {
      'error': {'code': 0, 'msg': 'success'},
      'linguistic': {
          'text': 'الحمد',
          'vocalized': 'الْحَمْدُ',
          'operation': 'vocalize'
      }
  }
  ```

- Dictionary with the following structure for `derive`:
  ```python
  {
      'error': {'code': 0, 'msg': 'success'},
      'linguistic': {
          'text': 'الحمد',
          'operation': 'derive',
          'words': [
              {
                  'word': 'الحمد',
                  'lemma': 'حمد',
                  'root': 'حمد',
                  'lemma_derivations': ['والحمد', 'يحمدوا', ...],
                  'root_derivations': ['الحميد', 'حميد', ...]
              }
          ]
      }
  }
  ```

## Examples

### Vocalization

Add diacritical marks to Arabic text:

```python
import alfanous.api as api

# Simple word
result = api.linguistic('الحمد', 'vocalize')
print(result['linguistic']['vocalized'])
# Output: الْحَمْدُ

# Complete phrase
result = api.linguistic('بسم الله الرحمن الرحيم', 'vocalize')
print(result['linguistic']['vocalized'])
# Output: بِسْمِ اللَّهَ الرَّحْمَنَ الرَّحِيمِ
```

### Derivation

Find roots and related words:

```python
import alfanous.api as api

result = api.linguistic('الحمد', 'derive')
word_info = result['linguistic']['words'][0]

print(f"Word: {word_info['word']}")
print(f"Lemma: {word_info['lemma']}")
print(f"Root: {word_info['root']}")
print(f"Lemma derivations: {word_info['lemma_derivations'][:5]}")
print(f"Root derivations: {word_info['root_derivations'][:5]}")

# Output:
# Word: الحمد
# Lemma: حمد
# Root: حمد
# Lemma derivations: ['بحمده', 'والحمد', 'يحمدوا', 'أحمد', 'الحمد']
# Root derivations: ['الحميد', 'حميدا', 'محمودا', 'حميد', 'الحامدون']
```

### Multiple Words

Process multiple words at once:

```python
import alfanous.api as api

result = api.linguistic('الحمد لله', 'derive')

for word_info in result['linguistic']['words']:
    print(f"\nWord: {word_info['word']}")
    print(f"  Root: {word_info['root']}")
    print(f"  Lemma: {word_info['lemma']}")
```

## Data Sources

The linguistic operations use pre-computed data from:

- **vocalizations.json**: Maps unvocalized words to their vocalized forms
- **derivations.json**: Contains word roots, lemmas, and derivation relationships

These files are located in `src/alfanous/resources/` and are automatically loaded when the API initializes.

## Running the Example

A complete example script is provided in `examples/linguistic_operations.py`:

```bash
cd alfanous
python3 examples/linguistic_operations.py
```

## Implementation Details

The linguistic operations are implemented in `src/alfanous/outputs.py` as part of the `Raw` class:

1. The `_linguistic()` method handles both vocalize and derive operations
2. Vocalization uses dictionary lookup from `vocalization_dict`
3. Derivation uses the `derivedict` data structure with helper functions from `alfanous.misc`
4. Results are limited to 20 derivations per word to keep response sizes manageable

## Testing

Tests for linguistic operations are in `src/tests/test_linguistic.py`. Run them with:

```bash
pytest src/tests/test_linguistic.py -v
```
