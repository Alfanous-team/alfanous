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
* `fuzzy` (bool): Enable fuzzy search — searches both `aya_` (exact) and `aya` (normalised/stemmed) fields, plus Levenshtein distance matching (default: False). See [Exact Search vs Fuzzy Search](#exact-search-vs-fuzzy-search).
* `fuzzy_maxdist` (int): Maximum Levenshtein edit distance for fuzzy term matching — `1`, `2`, or `3` (default: `1`, only used when `fuzzy=True`).
* `facets` (str): Comma-separated list of fields for faceted search
* `filter` (dict): Filter results by field values

For a complete list of parameters and options, see the [detailed documentation](#advanced-features).

### Advanced Features

#### Exact Search vs Fuzzy Search

Alfanous provides two complementary search modes that control which index fields are queried.

##### Exact Search (default — `fuzzy=False`)

When fuzzy search is **off** (the default), queries run against the **`aya_`** field, which stores the fully-vocalized Quranic text with diacritical marks (tashkeel) preserved. This mode is designed for precise, statistical matching:

* Diacritics in the query are significant — `مَلِكِ` and `مَالِكِ` are treated as different words.
* No stop-word removal, synonym expansion, or stemming is applied to the query.
* Ideal when you need exact phrase matches, reproducible result counts, or statistical analysis.

```python
# Default exact search — only the vocalized aya_ field is used
>>> api.search(u"الله")
>>> api.search(u"الله", fuzzy=False)

# Phrase match with full diacritics
>>> api.search(u'"الْحَمْدُ لِلَّهِ"')
```

##### Fuzzy Search (`fuzzy=True`)

When fuzzy search is **on**, queries run against **both** the `aya_` field (exact matches) **and** the `aya` field (a separate index built for broad, forgiving search). At index time the `aya` field is processed through a richer pipeline:

1. **Normalisation** — shaped letters, tatweel, hamza variants and common spelling errors are unified.
2. **Stop-word removal** — high-frequency function words (e.g. مِنْ، فِي، مَا) are filtered out so they do not dilute result relevance.
3. **Synonym expansion** — each token is stored together with its synonyms, so a query for one word automatically matches equivalent words.
4. **Arabic stemming** — words are reduced to their stem using the [Snowball Arabic stemmer](https://snowballstem.org/) (via `pystemmer`), so different morphological forms of the same root match each other.

No heavy operations are performed on the query string at search time; all the linguistic enrichment lives in the index.

Additionally, for each Arabic term in the query, a **Levenshtein distance** search is performed against the `aya_ac` field (unvocalized, non-stemmed). This catches spelling variants and typos within a configurable edit-distance budget controlled by `fuzzy_maxdist`.

```python
# Fuzzy search — aya_ (exact) + aya (normalised/stemmed) + Levenshtein distance on aya_ac
>>> api.search(u"الكتاب", fuzzy=True)

# Increase edit distance to 2 to tolerate more spelling variation
>>> api.search(u"الكتاب", fuzzy=True, fuzzy_maxdist=2)

# Via the unified interface
>>> api.do({
...     "action": "search",
...     "query": u"مؤمن",
...     "fuzzy": True,
...     "fuzzy_maxdist": 1,
...     "page": 1,
...     "perpage": 10
... })
```

| `fuzzy_maxdist` | Behaviour |
|---|---|
| `1` (default) | Catches single-character insertions, deletions, or substitutions |
| `2` | Broader tolerance — useful for longer words or noisy input |
| `3` | Maximum supported — use with care as recall increases significantly |

Fuzzy mode is particularly useful when:

* The user does not know the exact vocalized form of a word.
* You want morphologically related words to appear in the same result set (e.g. searching *كتب* also surfaces *كتاب*, *كاتب*, *مكتوب*).
* You want synonym-aware retrieval without writing explicit OR queries.

> **Note:** `pystemmer` must be installed for stemming to take effect (`pip install pystemmer`). If the package is absent the stem filter degrades silently to a no-op, leaving normalisation and stop-word removal still active.

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

## MCP Server

Alfanous ships an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that lets AI assistants (Claude, Copilot, etc.) search and explore the Qur'an directly. See [alfanous_mcp/README.md](src/alfanous_mcp/README.md) for the full reference.

Quick start:

```sh
$ pip install alfanous3-mcp
$ python -m alfanous_mcp.mcp_server        # stdio – works with Claude Desktop
```

To connect Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "alfanous": {
      "command": "python",
      "args": ["-m", "alfanous_mcp.mcp_server"]
    }
  }
}
```

The server is also published to the [GitHub MCP Registry](https://github.com/mcp/io.github.Alfanous-team/alfanous) — you can install it with a single click from there.

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
$ pip install pyparsing whoosh pystemmer pytest

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
