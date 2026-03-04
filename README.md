[![Tests](https://github.com/Alfanous-team/alfanous/workflows/tests/badge.svg)](https://github.com/Alfanous-team/alfanous/actions)

<!-- mcp-name: io.github.Alfanous-team/alfanous -->

# Alfanous API

**Alfanous** is a Quranic search engine API that provides simple and advanced search capabilities for the Holy Qur'an. It enables developers to build applications that search through Quranic text in Arabic, with support for Buckwalter transliteration, advanced query syntax, and rich metadata.

## Features

* **Powerful Search**: Search Quranic verses with simple queries or advanced Boolean logic
* **Arabic Support**: Full support for Arabic text and Buckwalter transliteration
* **Rich Metadata**: Access verse information, translations, recitations, and linguistic data
* **Flexible API**: Use as a Python library or RESTful web service
* **Faceted Search**: Aggregate results by Sura, Juz, topics, and more
* **Multiple Output Formats**: Customize output with different views and highlight styles

## Quickstart

### Installation

Install from PyPI using pip:

```sh
$ pip install alfanous3
```

### Basic Usage

#### Python Library

```python
>>> from alfanous import api

# Simple search for a word
>>> api.search(u"الله")

# Advanced search with options
>>> api.do({"action": "search", "query": u"الله", "page": 1, "perpage": 10})

# Search using Buckwalter transliteration
>>> api.do({"action": "search", "query": u"Allh"})

# Get suggestions
>>> api.do({"action": "suggest", "query": u"الح"})

# Get metadata information
>>> api.do({"action": "show", "query": "translations"})
```

#### Web Service

You can also use the public web service:

* Search: http://alfanous.org/api/search?query=الله
* With transliteration: http://alfanous.org/api/search?query=Allh

Or run your own web service locally (see [alfanous_webapi](src/alfanous_webapi/README.md)).

#### Quick Examples

Search for phrases:

```python
>>> api.search(u'"الحمد لله"')
```

Boolean search (AND, OR, NOT):

```python
>>> api.search(u'الصلاة + الزكاة')    # AND
>>> api.search(u'الصلاة | الزكاة')    # OR
>>> api.search(u'الصلاة - الزكاة')    # NOT
```

Fielded search:

```python
>>> api.search(u'سورة:يس')           # Search in Sura Yasin
>>> api.search(u'سجدة:نعم')          # Search verses with sajda
```

Wildcard search:

```python
>>> api.search(u'*نبي*')             # Words containing "نبي"
```

Faceted search (aggregate by fields):

```python
>>> api.do({
...     "action": "search",
...     "query": u"الله",
...     "facets": "sura_id,juz"
... })
```

## Documentation

### API Reference

#### Core Functions

* `api.search(query, **options)` - Search Quran verses
* `api.do(params)` - Unified interface for all actions (search, suggest, show)
* `api.get_info(category)` - Get metadata information

#### Search Parameters

Common parameters for `api.do()` with `action="search"`:

* `query` (str): Search query (required)
* `unit` (str): Search unit - "aya", "word", or "translation" (default: "aya")
* `page` (int): Page number (default: 1)
* `perpage` (int): Results per page, 1-100 (default: 10)
* `sortedby` (str): Sort order - "score", "mushaf", "tanzil", "subject" (default: "score")
* `view` (str): Output view - "minimal", "normal", "full", "statistic", "linguistic" (default: "normal")
* `highlight` (str): Highlight style - "css", "html", "bold", "bbcode" (default: "css")
* `script` (str): Text script - "standard" or "uthmani" (default: "standard")
* `vocalized` (bool): Include Arabic vocalization (default: True)
* `translation` (str): Translation ID to include
* `recitation` (str): Recitation ID to include (1-30, default: "1")
* `fuzzy` (bool): Enable fuzzy search (default: False)
* `facets` (str): Comma-separated list of fields for faceted search
* `filter` (dict): Filter results by field values

For a complete list of parameters and options, see the [detailed documentation](#advanced-features).

### Advanced Features

#### Query Syntax

Alfanous supports advanced query syntax:

* **Phrases**: Use quotes - `"الحمد لله"`
* **Boolean AND**: Use `+` - `الصلاة + الزكاة`
* **Boolean OR**: Use `|` - `الصلاة | الزكاة`
* **Boolean NOT**: Use `-` - `الصلاة - الزكاة`
* **Wildcards**: Use `*` for multiple chars, `?` for single char - `*نبي*`, `نعم؟`
* **Fielded Search**: Use field name - `سورة:يس`, `سجدة:نعم`
* **Ranges**: Use `[X الى Y]` - `رقم_السورة:[1 الى 5]`
* **Partial Vocalization**: Search with some diacritics - `آية_:'مَن'`
* **Root/Lemma**: Use `>>` for root, `>` for lemma - `>>مالك`, `>مالك`
* **Tuples**: Use `{root,type}` - `{قول،اسم}`

#### Faceted Search

Faceted search allows you to aggregate search results by fields:

```python
>>> result = api.do({
...     "action": "search",
...     "query": u"الله",
...     "facets": "sura_id,juz,chapter"
... })
>>> print(result["search"]["facets"])
```

Available facet fields:

* `sura_id` - Sura (chapter) number (1-114)
* `juz` - Juz (part) number (1-30)
* `hizb` - Hizb (section) number
* `chapter` - Main topic/chapter
* `topic` - Subtopic
* `sura_type` - Meccan/Medinan classification

#### Filtering Results

Filter search results by field values:

```python
>>> api.do({
...     "action": "search",
...     "query": u"الله",
...     "filter": {"sura_id": "2"}  # Only from Sura Al-Baqarah
... })
```

#### Search Fields

Available fields for fielded search:

* `سورة` (sura) - Sura name
* `رقم_السورة` (sura_id) - Sura number
* `رقم_الآية` (aya_id) - Verse number
* `جزء` (juz) - Juz number
* `حزب` (hizb) - Hizb number
* `صفحة` (page) - Page number in Mushaf
* `سجدة` (sajda) - Has prostration
* `موضوع` (subject) - Subject/theme
* `فصل` (chapter) - Chapter
* `باب` (subtopic) - Subtopic
* `نوع_السورة` (sura_type) - Sura type (Meccan/Medinan)

For the complete field list, call:

```python
>>> api.do({"action": "show", "query": "fields"})
```

#### Output Views

Different views provide different levels of detail:

* **minimal** - Basic verse text and identifier
* **normal** - Verse text with essential metadata
* **full** - All available information
* **statistic** - Include statistical information
* **linguistic** - Include linguistic analysis

Example:

```python
>>> api.do({
...     "action": "search",
...     "query": u"الله",
...     "view": "full",
...     "word_info": True,
...     "aya_theme_info": True
... })
```

#### Metadata Access

Get various metadata using the "show" action:

```python
# Get list of available translations
>>> api.do({"action": "show", "query": "translations"})

# Get list of recitations
>>> api.do({"action": "show", "query": "recitations"})

# Get Sura information
>>> api.do({"action": "show", "query": "surates"})

# Get search fields
>>> api.do({"action": "show", "query": "fields"})

# Get default values
>>> api.do({"action": "show", "query": "defaults"})
```

#### Adding New Translations

You can extend the local search index with additional Zekr-compatible `.trans.zip` translation files using `index_translations()`. This requires the `alfanous_import` package (included in the repository under `src/alfanous_import/`).

```python
import alfanous.api as alfanous

# Index all .trans.zip files found in a folder
count = alfanous.index_translations(source="/path/to/translations")
print(f"{count} translation(s) newly indexed")
```

The function:
- Iterates over every `*.trans.zip` file in `source`
- Skips translations that are already in the index (idempotent — safe to call repeatedly)
- Returns the **count** of newly indexed translations (`0` means nothing new was added)
- Automatically updates `configs/translations.json` so the new translations are immediately visible via `api.get_info("translations")` and searchable with `unit="translation"`

After indexing, search in the new translation:

```python
# Search in a newly indexed translation
result = alfanous.search(u"الرحمن", unit="translation", flags={"translation": "en.newt"})
```

See [`examples/index_translations_example.py`](examples/index_translations_example.py) for a complete walkthrough.

## Examples

The [examples/](examples/) directory contains example scripts demonstrating various features:

* **facet_search_examples.py** - Faceted search and filtering examples

See [examples/README.md](examples/README.md) for more information.

## Web Interface

Alfanous includes a FastAPI-based web service for RESTful access. See [alfanous_webapi/README.md](src/alfanous_webapi/README.md) for:

* Installation and setup
* API endpoints
* Request/response examples
* Interactive API documentation (Swagger UI)

Quick start:

```sh
$ pip install alfanous3 fastapi uvicorn
$ cd src/
$ uvicorn alfanous_webapi.web_api:app --reload
```

Then visit http://localhost:8000/docs for interactive documentation.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

* Setting up a development environment
* Building from source
* Running tests
* Submitting pull requests
* Code style guidelines

Quick development setup:

```sh
# Clone the repository
$ git clone https://github.com/Alfanous-team/alfanous.git
$ cd alfanous

# Install dependencies
$ pip install pyparsing whoosh pytest

# Build indexes (required for development)
$ make build

# Run tests
$ pytest -vv --rootdir=src/
```

## Support

* **GitHub Issues**: https://github.com/Alfanous-team/alfanous/issues
* **Mailing List**: alfanous@googlegroups.com
* **Website**: http://alfanous.org

## License

Alfanous is licensed under the **GNU Lesser General Public License v3 or later (LGPLv3+)**.

See [LICENSE](LICENSE) for details.

## Credits
* **Contributors**: See [AUTHORS.md](AUTHORS.md) and [THANKS.md](THANKS.md)

This project handles sacred religious text (the Holy Qur'an) - please treat the data and code with respect.

## Legacy

If you are looking for the legacy Alfanous code, you can find it under the `legacy` branch.
