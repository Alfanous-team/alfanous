[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/alfanous-team-alfanous-badge.png)](https://mseep.ai/app/alfanous-team-alfanous)

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

# Correct a query
>>> api.correct_query(u"الكتاب")

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
* `api.do(params)` - Unified interface for all actions (search, suggest, show, list_values, correct_query)
* `api.correct_query(query, unit, flags)` - Get a spelling-corrected version of a query
* `api.get_info(category)` - Get metadata information

The underlying `Raw` output engine is exposed as `Engine` in `alfanous.api` (and re-exported from `alfanous` directly). Use it as a context manager to ensure index resources are properly released:

```python
from alfanous.api import Engine
# or equivalently:
# from alfanous import Engine

with Engine() as engine:
    result = engine.do({"action": "search", "query": u"الله"})
```

#### Search Parameters

Common parameters for `api.do()` with `action="search"`:

* `query` (str): Search query (required)
* `unit` (str): Search unit - "aya", "word", or "translation" (default: "aya")
* `page` (int): Page number (default: 1)
* `perpage` (int): Results per page, 1-100 (default: 10)
* `sortedby` (str): Sort order - "score", "relevance", "mushaf", "tanzil", "ayalength" (default: "score")
* `reverse` (bool): Reverse the sort order (default: False)
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

#### List Field Values

`list_values` returns every unique indexed value for a given field. Use it to discover the full vocabulary of searchable fields — for example, all available translation identifiers, part-of-speech tags, or root words — before composing a query.

```python
# Get all unique root values in the index
>>> api.do({"action": "list_values", "field": "root"})
# Returns: {"list_values": {"field": "root", "values": [...], "count": N}}

# Discover all indexed translation IDs
>>> api.do({"action": "list_values", "field": "trans_id"})

# Discover all part-of-speech categories for word search
>>> api.do({"action": "list_values", "field": "pos"})

# Retrieve all indexed lemmas on demand (replaces the former show/lemmas)
>>> api.do({"action": "list_values", "field": "lemma"})
```

**Parameters:**

* `field` (str): The name of the indexed field whose unique values you want (required).

**Return value:**

A dictionary with a `list_values` key containing:

* `field` — the requested field name.
* `values` — sorted list of unique non-empty indexed values.
* `count` — length of the `values` list.

#### Query Correction

`correct_query()` uses Whoosh's built-in spell-checker to compare each term in the query against the index vocabulary and replace unknown terms with the closest known alternative.  When the query is already valid (all terms appear in the index) the `corrected` value in the response is identical to the original input.

```python
# Correct a query via the dedicated function
>>> api.correct_query(u"الكتاب")
# Returns:
# {"correct_query": {"original": "الكتاب", "corrected": "الكتاب"}, "error": ...}

# Correct a misspelled / out-of-vocabulary term
>>> api.correct_query(u"الكتب")
# Returns:
# {"correct_query": {"original": "الكتب", "corrected": "الكتاب"}, "error": ...}

# Via the unified interface
>>> api.do({"action": "correct_query", "query": u"الكتب", "unit": "aya"})
```

**Parameters:**

* `query` (str): The raw query string to correct (required).
* `unit` (str): Search unit — currently only `"aya"` is supported; other units return `None` (default: `"aya"`).
* `flags` (dict): Optional dictionary of additional flags.

**Return value:**

A dictionary with a `correct_query` key containing:

* `original` — the input query string as provided.
* `corrected` — the corrected query string; identical to `original` when no correction is needed.

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
* **Derivation (stem)**: Use `>` - `>رحيم` (searches `aya_stem` — corpus-derived stem)
* **Derivation (lemma)**: Use `>>` - `>>رحيم` (searches `aya_lemma` — all inflections of the same lexeme)
* **Derivation (root)**: Use `>>>` - `>>>ملك` (searches `aya_root` — all words from the same root)
* **Tuples**: Use `{root,type}` - `{قول،اسم}`

#### Derivation-Level Search

Control how broadly the search expands morphologically using the `derivation_level` parameter:

| Level | Value | Index field | Description |
|---|---|---|---|
| 0 | `"word"` | `aya` | Exact match only (default) |
| 1 | `"stem"` | `aya_stem` | Corpus-derived stem — words sharing the same morphological stem |
| 2 | `"lemma"` | `aya_lemma` | Corpus lemma — all inflections of the same lexeme |
| 3 | `"root"` | `aya_root` | Trilateral root — all words from the same root |

Each derivation field is pre-indexed at build time so queries run against a compact, pre-computed representation rather than expanding at search time.

```python
# Level 0 — exact match
>>> api.do({"action": "search", "query": "رَحِيمٌ"})

# Level 1 — stem (corpus-derived stem)
>>> api.do({"action": "search", "query": "رحيم", "derivation_level": 1})

# Level 2 — all words sharing the same lemma (e.g. all forms of رَحِيمٌ)
>>> api.do({"action": "search", "query": "رحيم", "derivation_level": 2})

# Level 3 — all words from root رحم (رحمة، رحمن، رحيم، يرحم، …)
>>> api.do({"action": "search", "query": "رحيم", "derivation_level": 3})

# String aliases are also accepted
>>> api.do({"action": "search", "query": "كتب", "derivation_level": "root"})
```

The derivation syntax `>word`, `>>word`, `>>>word` maps to levels 1, 2, 3 respectively and can be embedded directly in queries:

```python
# Stem-level derivation in a query expression
>>> api.do({"action": "search", "query": ">رحيم"})

# Root-level: all words from root ملك
>>> api.do({"action": "search", "query": ">>>ملك"})

# Combined with field filters
>>> api.do({"action": "search", "query": ">>الله AND سورة:الإخلاص"})
```

#### Word Search (`unit="word"`)

When `unit="word"` the engine searches word-level child documents instead of verse-level parent documents. Each word child carries its full morphological annotation — part-of-speech, lemma, stem, root, pattern, gender, number, person, voice, mood, derivation level, and more.

```python
# Search all words matching "الله" at word level
>>> api.do({"action": "search", "query": "الله", "unit": "word"})

# Derivation levels also apply to word search:
# Level 1 — search word_stem (corpus-derived stem)
>>> api.do({"action": "search", "query": "رحيم", "unit": "word", "derivation_level": 1})

# Level 2 — search word_lemma (normalized lemma)
>>> api.do({"action": "search", "query": "رحيم", "unit": "word", "derivation_level": 2})

# Level 3 — search root (exact root value, e.g. "رحم")
>>> api.do({"action": "search", "query": "رحم", "unit": "word", "derivation_level": 3})
```

##### Morphological Filtering (`search_by_word_linguistics`)

Filter words by any combination of morphological properties using the `search_by_word_linguistics` action:

```python
# Find all nouns from root قول
>>> api.do({
...     "action": "search_by_word_linguistics",
...     "root": "قول",
...     "type": "أسماء"       # Arabic POS category name
... })

# Find all active-voice past-tense verbs from root كتب
>>> api.do({
...     "action": "search_by_word_linguistics",
...     "root": "كتب",
...     "pos": "V",
...     "voice": "مبني للمعلوم",
...     "aspect": "فعل ماضي"
... })

# Find all proper nouns
>>> api.do({
...     "action": "search_by_word_linguistics",
...     "pos": "PN"
... })
```

Available morphological filter fields include: `pos`, `type`, `root`, `lemma`, `stem`, `pattern`, `gender`, `number`, `person`, `voice`, `mood`, `state`, `case`, `form`, `aspect`, `derivation`, `special`, `prefix`, `suffix`, `segments`.



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

Word-level fields (use with `unit="word"`):

* `englishstate` - Nominal state in English (e.g. "Definite state", "Indefinite state")
* `englishmood` - Verb mood in English (e.g. "Indicative mood", "Subjunctive mood", "Jussive mood")

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

> **Note:** Lemmas are no longer exposed via `show`. Use `api.do({"action": "list_values", "field": "lemma"})` to retrieve them on demand.

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
      "type": "stdio",
      "command": "python",
      "args": ["-m", "alfanous_mcp.mcp_server"],
      "tools": [
        "search_quran",
        "search_translations",
        "get_quran_info",
        "search_quran_by_themes",
        "search_quran_by_stats",
        "search_quran_by_position",
        "suggest_query",
        "correct_query",
        "search_by_word_linguistics",
        "list_field_values"
      ]
    }
  }
}
```

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
