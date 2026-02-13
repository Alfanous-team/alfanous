# Alfanous Examples

This directory contains example scripts demonstrating various features of the Alfanous API.

## Autocomplete Examples

The `autocomplete_examples.py` script demonstrates how to use the new autocomplete feature to get keyword suggestions for phrases.

### Running the Example

```bash
# From the repository root
PYTHONPATH=src python3 examples/autocomplete_examples.py
```

### What the Example Demonstrates

1. **Basic autocomplete** - Get keyword suggestions for a phrase
2. **Single word autocomplete** - Complete a single word prefix
3. **Custom limits** - Control the number of suggestions returned
4. **Using api.do()** - Use the low-level do() method for autocomplete
5. **Common Quranic phrases** - Autocomplete common Quranic expressions
6. **Empty query handling** - Handle edge cases gracefully

### Usage

```python
from alfanous import api

# Basic usage - returns top 10 suggestions
result = api.autocomplete("الحمد ل", limit=10)

# Using api.do() method
result = api.do({
    "action": "autocomplete",
    "query": "بسم الله",
    "unit": "aya",
    "limit": 10
})
```

### Features

- Accepts phrases (multiple words)
- Returns top N relevant keywords based on the last word prefix
- Default limit is 10 keywords, customizable via the `limit` parameter
- Works with both Arabic text and Buckwalter transliteration
- Gracefully handles empty queries

## Facet Search Examples

The `facet_search_examples.py` script demonstrates how to use the faceted search feature to get aggregated counts of search results grouped by various fields.

### Running the Example

```bash
# From the repository root
PYTHONPATH=src python3 examples/facet_search_examples.py
```

### What the Example Demonstrates

1. **Basic facet search** - Search for a term and get counts by Sura
2. **Multiple facets** - Request multiple facets in a single search
3. **Filter and facet** - Filter by a field and get facets for the filtered results
4. **Distribution analysis** - View how search results are distributed across Juz
5. **Using api.do()** - Use the low-level do() method with facets

### Available Facet Fields

- `sura_id` - Group by Sura (chapter) number (1-114)
- `juz` - Group by Juz (part) number (1-30)
- `chapter` - Group by main topic/chapter
- `topic` - Group by subtopic
- `sura_type` - Group by Meccan/Medinan classification

### Example Output Structure

```python
{
    "error": {"code": 0, "msg": "success"},
    "search": {
        "runtime": 0.12345,
        "interval": {...},
        "facets": {
            "sura_id": [
                {"value": 2, "count": 139},
                {"value": 4, "count": 122},
                ...
            ],
            "juz": [
                {"value": 5, "count": 6},
                {"value": 6, "count": 5},
                ...
            ]
        },
        "ayas": {...}
    }
}
```

## Adding New Examples

To add a new example:

1. Create a new Python script in this directory
2. Import the alfanous API: `from alfanous import api`
3. Add documentation and clear comments
4. Update this README with information about your example
