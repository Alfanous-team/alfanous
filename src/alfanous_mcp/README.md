# Alfanous MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that
exposes the **Alfanous Quranic search engine** as a set of tools and resources
for AI assistants, enabling them to search, explore, and retrieve information
from the Holy Qur'an.

## Features

- **Search Quranic verses** with full support for Arabic text, Buckwalter
  transliteration, boolean operators, phrase search, wildcards, fuzzy matching,
  field filters, and facets.
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
   pip install alfanous3
   # or from source:
   pip install pyparsing whoosh
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
      "command": "python",
      "args": ["-m", "alfanous_mcp.mcp_server"]
    }
  }
}
```

## Tools

### `search_quran`

Search for verses in the Holy Qur'an.

| Parameter   | Type    | Default       | Description |
|-------------|---------|---------------|-------------|
| `query`     | string  | *(required)*  | Arabic text or Buckwalter transliteration |
| `unit`      | string  | `"aya"`       | `"aya"`, `"word"`, or `"translation"` |
| `page`      | int     | `1`           | Page number |
| `perpage`   | int     | `10`          | Results per page (1–100) |
| `sortedby`  | string  | `"relevance"` | `"relevance"`, `"score"`, `"mushaf"`, `"tanzil"`, `"ayalength"` |
| `fuzzy`     | bool    | `false`       | Enable approximate matching |
| `view`      | string  | `"normal"`    | `"minimal"`, `"normal"`, `"full"`, `"statistic"`, `"linguistic"` |
| `highlight` | string  | `"bold"`      | `"bold"`, `"css"`, `"html"`, `"bbcode"` |
| `translation` | string | `null`       | Translation identifier |
| `facets`    | string  | `null`        | Comma-separated facet fields |
| `filter`    | string  | `null`        | Field filter expression |

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
| Fuzzy | `الله~` | Approximate match |

## License

LGPL v3 or later – see the root `LICENSE` file.
