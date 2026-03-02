# Alfanous Examples

This directory contains example scripts demonstrating various features of the Alfanous API.

## AI Query Translation Rules Example

The `ai_query_translation_example.py` script demonstrates how to access and use the AI query translation rules file that helps translate natural language queries into Alfanous query syntax.

### Running the Example

```bash
# From the repository root
PYTHONPATH=src python3 examples/ai_query_translation_example.py
```

### What the Example Demonstrates

1. **Loading the AI rules file** - Access the rules from the resources directory
2. **Rules summary** - Display table of contents and file statistics
3. **Translation patterns** - Show examples of natural language to query syntax translation
4. **Integration guidance** - How AI systems can use the rules
5. **Practical usage** - Example code for implementing query translation

### AI Rules File Features

The rules file includes comprehensive documentation for:
- Basic operators (AND, OR, NOT, phrases)
- Advanced features (wildcards, field searches, ranges, boosting)
- Arabic-specific features (synonyms, antonyms, root derivations, tashkil)
- Field name reference (Arabic and English)
- Natural language translation patterns
- Common query examples
- Integration strategies for AI systems

The rules file is located at: `src/alfanous/resources/ai_query_translation_rules.txt`

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

## Index Translations Example

The `index_translations_example.py` script demonstrates how to extend the Alfanous
search index with additional Zekr-compatible `.trans.zip` translation files using
`alfanous.index_translations()`.

### Requirements

- `alfanous3` — `pip install alfanous3`
- `alfanous_import` — install from the repository: `pip install -e src/alfanous_import/`

### Running the Example

```bash
# From the repository root (uses store/Translations/ by default)
PYTHONPATH=src python3 examples/index_translations_example.py

# Or point at any folder containing .trans.zip files
PYTHONPATH=src python3 examples/index_translations_example.py /path/to/translations
```

### What the Example Demonstrates

1. **List current translations** — shows translations available before indexing
2. **Index new translations** — calls `alfanous.index_translations(source=...)` to index every `.trans.zip` in the given folder; already-indexed ones are skipped automatically
3. **Confirm the update** — lists available translations after indexing, highlighting newly added entries
4. **Sample search** — searches in one of the indexed translations to confirm it is searchable

### API Summary

```python
import alfanous.api as alfanous

# Index all .trans.zip files in a folder
count = alfanous.index_translations(source="/path/to/translations")
print(f"{count} translation(s) newly indexed")

# The new translations are immediately visible
translations = alfanous.get_info("translations")

# Search in a newly indexed translation
result = alfanous.search(u"الرحمن", unit="translation",
                         flags={"translation": "en.newt"})
```

`index_translations()` returns the count of **newly** indexed translations.
Calling it again on the same folder returns `0` — it is safe to call repeatedly.
