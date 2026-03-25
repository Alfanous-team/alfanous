<!-- mcp-name: io.github.Alfanous-team/alfanous -->

# Alfanous MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that
exposes the **Alfanous Quranic search engine** as a set of tools and resources
for AI assistants, enabling them to search, explore, and retrieve information
from the Holy Qur'an.

## Features

- **Search Quranic verses** with full support for Arabic text, Buckwalter
  transliteration, boolean operators, phrase search, wildcards, fuzzy matching,
  field filters, and facets.
- **Search translations** across many languages (English, French, Urdu, and more).
- **Retrieve metadata** – chapter names, available translations, recitations,
  search field descriptions, and API defaults.
- **Query auto-completion** – get suggestions while typing a search query.
- **AI query-translation guide** as an MCP resource (`quran://ai-rules`) that
  helps AI assistants convert natural-language questions into Alfanous query
  syntax.

## Installation

### Prerequisites

1. Install the **Alfanous** core library and build the indexes:

   ```bash
   pip install alfanous3 pystemmer
   # or from source:
   pip install pyparsing whoosh pystemmer
   cd /path/to/alfanous && make build
   ```

2. Install the **MCP** Python SDK:

   ```bash
   pip install mcp
   ```

## Running the Server

### stdio transport (default – works with Claude Desktop and most MCP clients)

```bash
python -m alfanous_mcp.mcp_server
```

### Streamable-HTTP transport (for testing/development)

```bash
python -m alfanous_mcp.mcp_server --transport streamable-http
```

## Configuring Claude Desktop

Add the following to your `claude_desktop_config.json`:

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
        "search_by_word_linguistics"
      ]
    }
  }
}
```

## Tools

### `search_quran`

Search for verses in the Holy Qur'an.

| Parameter        | Type    | Default       | Description |
|------------------|---------|---------------|-------------|
| `query`          | string  | *(required)*  | Arabic text or Buckwalter transliteration |
| `unit`           | string  | `"aya"`       | `"aya"`, `"word"`, or `"translation"` |
| `page`           | int     | `1`           | Page number |
| `perpage`        | int     | `10`          | Results per page (1–100) |
| `sortedby`       | string  | `"relevance"` | `"relevance"`, `"score"`, `"mushaf"`, `"tanzil"`, `"ayalength"` |
| `fuzzy`          | bool    | `false`       | Enable fuzzy search (see [Fuzzy Search](#fuzzy-search)) |
| `fuzzy_maxdist`  | int     | `1`           | Levenshtein edit distance — `1`, `2`, or `3` (only used when `fuzzy=true`) |
| `derivation_level`| int/str | `0`          | Morphological breadth — `0`/`"word"` (exact), `1`/`"stem"`, `2`/`"lemma"`, `3`/`"root"` (see [Derivation-Level Search](#derivation-level-search)) |
| `view`           | string  | `"normal"`    | `"minimal"`, `"normal"`, `"full"`, `"statistic"`, `"linguistic"` |
| `highlight`      | string  | `"bold"`      | `"bold"`, `"css"`, `"html"`, `"bbcode"` |
| `translation`    | string  | `null`        | Translation identifier to include alongside each verse |
| `facets`         | string  | `null`        | Comma-separated facet fields |
| `field_filter`   | string  | `null`        | Field filter expression (e.g. `"sura_number:2"`) |

### `search_translations`

Search within Quranic translation texts (English, French, Urdu, etc.).

| Parameter      | Type    | Default       | Description |
|----------------|---------|---------------|-------------|
| `query`        | string  | *(required)*  | Query in any language |
| `translation`  | string  | `null`        | Translation ID (e.g. `"en.pickthall"`); omit to search all |
| `page`         | int     | `1`           | Page number |
| `perpage`      | int     | `10`          | Results per page (1–100) |
| `sortedby`     | string  | `"relevance"` | `"relevance"`, `"score"`, `"mushaf"`, `"tanzil"`, `"ayalength"` |
| `fuzzy`        | bool    | `false`       | Enable fuzzy search (see [Fuzzy Search](#fuzzy-search)) |
| `fuzzy_maxdist`| int     | `1`           | Levenshtein edit distance — `1`, `2`, or `3` (only used when `fuzzy=true`) |
| `highlight`    | string  | `"bold"`      | `"bold"`, `"css"`, `"html"`, `"bbcode"` |
| `facets`       | string  | `null`        | Comma-separated facet fields |
| `field_filter` | string  | `null`        | Field filter expression |

### `get_quran_info`

Retrieve Qur'an metadata.

| `category` value | Description |
|------------------|-------------|
| `"chapters"` / `"surates"` | Chapter names and numbers |
| `"translations"` | Available translation identifiers |
| `"recitations"` | Available recitation identifiers |
| `"defaults"` | Default search parameter values |
| `"domains"` | Valid values for each parameter |
| `"fields"` | Available search fields |
| `"flags"` | All supported API flags |
| `"help_messages"` | Human-readable help for parameters |
| `"hints"` | Search tips and examples |
| `"ai_query_translation_rules"` | Full query-syntax guide for AI |
| `"all"` | Everything at once |

### `suggest_query`

Get auto-completion suggestions for a partial query.

| Parameter | Type   | Default  | Description |
|-----------|--------|----------|-------------|
| `query`   | string | *(required)* | Partial search string |
| `unit`    | string | `"aya"`  | `"aya"`, `"word"`, or `"translation"` |

## Derivation-Level Search

Control how broadly the search expands morphologically using the `derivation_level` parameter of `search_quran` (or `unit="word"`).

| Level | Value | Index field | How it works |
|-------|-------|-------------|--------------|
| 0 | `"word"` | `aya` | Exact match only (default) |
| 1 | `"stem"` | `aya_stem` | Corpus-derived stem indexed with Snowball Arabic stemmer; also adds the normalized token as fallback |
| 2 | `"lemma"` | `aya_lemma` | Corpus lemma — all inflections of the same lexeme |
| 3 | `"root"` | `aya_root` | Trilateral root — all words from the same Arabic root |

```
# Stem-level: رحيم → Snowball stem → matches رحمة، الرحيم، يرحم، …
search_quran(query="رحيم", derivation_level=1)

# Lemma-level: all words sharing the lemma of رَحِيمٌ
search_quran(query="رحيم", derivation_level="lemma")

# Root-level: all words from root رحم
search_quran(query="رحم", derivation_level=3)
```

Derivation syntax can also be embedded directly in the query string:

| Pattern | Field searched | Example |
|---------|---------------|---------|
| `>word` | `aya_stem` | `>رحيم` |
| `>>word` | `aya_lemma` | `>>رحيم` |
| `>>>word` | `aya_root` | `>>>رحم` |

## Word Search (`unit="word"`)

When `unit="word"` the engine searches individual word child documents, each carrying full morphological annotation. The `derivation_level` parameter works here too:

| Level | Field searched | Description |
|-------|---------------|-------------|
| 0 | `word`, `normalized` | Exact word match |
| 1 | `word_stem` | Corpus stem (QStandardAnalyzer) + Snowball fallback |
| 2 | `word_lemma` | Normalized lemma (QStandardAnalyzer) |
| 3 | `root` | Exact root value |

```
# Find all word-level matches for "الله"
search_quran(query="الله", unit="word")

# All words sharing the lemma of رحيم
search_quran(query="رحيم", unit="word", derivation_level=2)

# All words from root رحم
search_quran(query="رحم", unit="word", derivation_level=3)
```

For morphological filtering use the `search_by_word_linguistics` action:

```
# All nouns from root قول
do({"action": "search_by_word_linguistics", "root": "قول", "type": "أسماء"})

# All active-voice past-tense verbs from root كتب
do({"action": "search_by_word_linguistics", "root": "كتب", "pos": "V",
    "voice": "مبني للمعلوم", "aspect": "فعل ماضي"})
```

## Fuzzy Search

When `fuzzy=true` the engine uses three complementary strategies simultaneously:

| # | Strategy | Field | Description |
|---|----------|-------|-------------|
| 1 | **Exact** | `aya_` | Fully-vocalized Quranic text — precise, statistical matching |
| 2 | **Normalised / stemmed** | `aya` | Text indexed with stop-word removal, synonym expansion (index time), and Arabic stemming via [Snowball / pystemmer](https://snowballstem.org/). Handles morphological variants (كَتَبَ / كِتَاب / مَكْتُوب). |
| 3 | **Levenshtein distance** | `aya_ac` | Finds indexed terms within `fuzzy_maxdist` edit operations of each query term. Handles typos and minor spelling variants. |

Results from all three strategies are OR-combined, so the result set is always
a superset of the exact-only results.

### Choosing `fuzzy_maxdist`

| Value | Typical use |
|-------|-------------|
| `1` *(default)* | Single-character typos (insertion / deletion / substitution) |
| `2` | Longer words or noisier input |
| `3` | Maximum tolerance — recall increases significantly |

**Example** (via an AI assistant prompt):

> "Search for verses about رحمن with fuzzy matching and edit distance 1"
>
> → `search_quran(query="رحمن", fuzzy=True, fuzzy_maxdist=1)`

## Resources

### `quran://ai-rules`

A plain-text guide that teaches AI assistants how to translate natural-language
questions about the Qur'an into Alfanous query syntax.  Covers all operators,
field names, Arabic-specific features (synonyms, antonyms, root derivations),
and over 100 practical examples.

## Query Syntax Quick Reference

| Pattern | Example | Meaning |
|---------|---------|---------|
| Arabic word | `الله` | Verses containing "الله" |
| Buckwalter | `Allh` | Same, using transliteration |
| AND | `الله رحمة` | Both words present |
| OR | `الله OR رحمن` | Either word |
| NOT | `الله NOT عذاب` | First without second |
| Phrase | `"بسم الله"` | Exact phrase |
| Wildcard | `رحم*` | Words starting with رحم |
| Field filter | `sura_number:2` | Surah 2 only |
| Stem derivation | `>رحيم` | `aya_stem` (Snowball-stemmed corpus stem) |
| Lemma derivation | `>>رحيم` | `aya_lemma` (all inflections of same lexeme) |
| Root derivation | `>>>ملك` | `aya_root` (all words from same root) |
| Fuzzy | `fuzzy=true` parameter | Broad approximate match |

## License

LGPL v3 or later – see the root `LICENSE` file.
