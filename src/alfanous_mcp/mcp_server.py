#!/usr/bin/env python
# coding: utf-8

"""
Alfanous MCP Server

An MCP (Model Context Protocol) server that exposes the Alfanous Quranic
search engine as a set of tools and resources, enabling AI assistants to
search, explore, and retrieve information from the Holy Qur'an.

Usage:
    Run as a stdio server (default for MCP clients):
        python -m alfanous_mcp.mcp_server

    Or via the installed console script:
        alfanous-mcp

    Run as an HTTP server (for testing/development):
        python -m alfanous_mcp.mcp_server --transport streamable-http
"""

import json
import logging
from typing import Optional, Any

from mcp.server.fastmcp import FastMCP

import alfanous.api as alfanous_api
from alfanous import paths as PATHS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="alfanous",
    instructions=(
        "Alfanous is a search engine for the Holy Qur'an. "
        "Use the search_quran tool to find Quranic verses by keyword or phrase. "
        "Use search_translations to search within Quranic translation texts in "
        "languages such as English, French, Urdu, and more. "
        "Use get_quran_info to retrieve metadata such as chapter names, "
        "available translations, and recitations. "
        "Use suggest_query to get auto-completion suggestions while typing a query. "
        "Queries support Arabic script, Buckwalter transliteration, field filters, "
        "boolean operators, phrase search, wildcards, fuzzy matching, and more. "
        "Read the quran://ai-rules resource for a complete guide on how to "
        "translate natural-language requests into Alfanous query syntax."
    ),
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_serializable(obj: Any) -> Any:
    """Recursively convert non-JSON-serializable objects to serializable types."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(i) for i in obj]
    # dict_keys / dict_values / dict_items and similar iterables
    try:
        iter(obj)
        if not isinstance(obj, (str, bytes)):
            return [_make_serializable(i) for i in obj]
    except TypeError:
        pass
    return obj


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    title="Search the Qur'an",
    description=(
        "Search for verses in the Holy Qur'an. "
        "The query supports Arabic text, Buckwalter transliteration, boolean "
        "operators (AND / OR / NOT), phrase search (\"…\"), wildcards (* and ?), "
        "field-specific searches (e.g. sura:2 aya:255), fuzzy matching, synonyms, "
        "antonyms, and root-level derivations. "
        "Returns a paginated list of matching verses with metadata."
    ),
)
def search_quran(
    query: str,
    unit: str = "aya",
    page: int = 1,
    perpage: int = 10,
    sortedby: str = "relevance",
    fuzzy: bool = False,
    view: str = "normal",
    highlight: str = "bold",
    translation: Optional[str] = None,
    facets: Optional[str] = None,
    field_filter: Optional[str] = None,
) -> dict:
    """Search for verses in the Holy Qur'an.

    Args:
        query: Search query in Arabic or Buckwalter transliteration.
        unit: Search unit — one of "aya" (verse), "word", or "translation".
        page: Page number for pagination (starts at 1).
        perpage: Number of results per page (1–100).
        sortedby: Sort order — one of "relevance", "score", "mushaf",
            "tanzil", or "ayalength".
        fuzzy: Enable fuzzy (approximate) matching.
        view: Result detail level — one of "minimal", "normal", "full",
            "statistic", "linguistic", or "custom".
        highlight: Highlight style for matched terms — one of "bold",
            "css", "html", or "bbcode".
        translation: Translation identifier to include in results.
        facets: Comma-separated list of fields to aggregate as facets.
        field_filter: Field filter expression (e.g. "sura_number:2").

    Returns:
        Dictionary with search results including matched verses, pagination
        info, and optional facets.
    """
    flags: dict = {
        "action": "search",
        "query": query,
        "unit": unit,
        "page": page,
        "range": perpage,
        "sortedby": sortedby,
        "fuzzy": fuzzy,
        "view": view,
        "highlight": highlight,
    }
    if translation is not None:
        flags["translation"] = translation
    if facets is not None:
        flags["facets"] = facets
    if field_filter is not None:
        flags["filter"] = field_filter

    result = alfanous_api.do(flags)
    return _make_serializable(result)


@mcp.tool(
    title="Search Qur'an Translations",
    description=(
        "Search within Quranic translation texts (e.g. English, French, Urdu). "
        "Use this tool when the query is in a non-Arabic language or when the "
        "user wants to find verses by their translated meaning. "
        "Optionally specify a translation identifier (see get_quran_info with "
        "category='translations' for available options). "
        "Returns a paginated list of matching translation snippets with verse metadata."
    ),
)
def search_translations(
    query: str,
    translation: Optional[str] = None,
    page: int = 1,
    perpage: int = 10,
    sortedby: str = "relevance",
    fuzzy: bool = False,
    highlight: str = "bold",
    facets: Optional[str] = None,
    field_filter: Optional[str] = None,
) -> dict:
    """Search within Quranic translation texts.

    Args:
        query: Search query in any language (e.g. English, French, Urdu).
        translation: Translation identifier to search in (e.g. "en.pickthall").
            Use get_quran_info(category='translations') to list available IDs.
            When omitted, all indexed translations are searched.
        page: Page number for pagination (starts at 1).
        perpage: Number of results per page (1–100).
        sortedby: Sort order — one of "relevance", "score", "mushaf",
            "tanzil", or "ayalength".
        fuzzy: Enable fuzzy (approximate) matching.
        highlight: Highlight style for matched terms — one of "bold",
            "css", "html", or "bbcode".
        facets: Comma-separated list of fields to aggregate as facets.
        field_filter: Field filter expression (e.g. "sura_number:2").

    Returns:
        Dictionary with search results including matched translation snippets,
        pagination info, and optional facets.
    """
    flags: dict = {
        "action": "search",
        "query": query,
        "unit": "translation",
        "page": page,
        "range": perpage,
        "sortedby": sortedby,
        "fuzzy": fuzzy,
        "highlight": highlight,
    }
    if translation is not None:
        flags["translation"] = translation
    if facets is not None:
        flags["facets"] = facets
    if field_filter is not None:
        flags["filter"] = field_filter

    result = alfanous_api.do(flags)
    return _make_serializable(result)


@mcp.tool(
    title="Get Qur'an Metadata",
    description=(
        "Retrieve metadata about the Qur'an index and the Alfanous API. "
        "Available categories: 'chapters', 'surates', 'translations', "
        "'recitations', 'defaults', 'domains', 'fields', 'flags', "
        "'help_messages', 'hints', 'information', 'errors', "
        "'ai_query_translation_rules', or 'all' for everything at once."
    ),
)
def get_quran_info(category: str = "all") -> dict:
    """Retrieve metadata about the Qur'an index and the Alfanous API.

    Args:
        category: The category of information to retrieve.
            - "chapters" / "surates": Chapter (surah) names and numbers.
            - "translations": Available translation identifiers.
            - "recitations": Available recitation identifiers.
            - "defaults": Default values for search parameters.
            - "domains": Valid values for each parameter.
            - "fields": Available search fields.
            - "flags": All supported API flags/parameters.
            - "help_messages": Human-readable help for each parameter.
            - "hints": Search tips and query examples.
            - "information": General API metadata.
            - "errors": Error codes and messages.
            - "ai_query_translation_rules": Guide for translating natural
              language into Alfanous query syntax.
            - "all": Return all of the above at once.

    Returns:
        Dictionary with the requested metadata.
    """
    result = alfanous_api.get_info(category)
    return _make_serializable(result)


@mcp.tool(
    title="Suggest Query Completions",
    description=(
        "Get auto-completion suggestions for a partial Quranic search query. "
        "Useful for helping users refine their queries or correct spelling."
    ),
)
def suggest_query(query: str, unit: str = "aya") -> dict:
    """Get search suggestions for a partial query.

    Args:
        query: Partial query string to get suggestions for.
        unit: Search unit — one of "aya" (verse), "word", or "translation".

    Returns:
        Dictionary with suggested completions.
    """
    flags = {
        "action": "suggest",
        "query": query,
        "unit": unit,
    }
    result = alfanous_api.do(flags)
    return _make_serializable(result)


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource(
    uri="quran://ai-rules",
    name="AI Query Translation Rules",
    description=(
        "Complete guide for translating natural-language questions about the "
        "Qur'an into Alfanous query syntax. Covers all operators, field names, "
        "Arabic-specific features, and practical examples."
    ),
    mime_type="text/plain",
)
def get_ai_rules() -> str:
    """Return the AI query translation rules as plain text."""
    try:
        with open(PATHS.AI_QUERY_TRANSLATION_RULES_FILE, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        logger.warning("Could not read AI rules file: %s", exc)
        return (
            "AI query translation rules file not found. "
            "Please ensure the Alfanous package is properly installed."
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the alfanous-mcp console script."""
    import sys
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
