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
        "Alfanous is a search engine for the Holy Qur'an.\n\n"

        "TOOL OVERVIEW\n"
        "-------------\n"
        "• search_quran — find verses by Arabic keyword, phrase, or Buckwalter "
        "transliteration. Supports boolean operators (AND/OR/NOT), wildcards, "
        "fuzzy matching, and field filters.\n"
        "  Example: query='رحمة AND مغفرة'  or  query='\"بسم الله\"'  or  "
        "query='rHmn' (Buckwalter).\n\n"

        "• search_translations — search translated verse text in non-Arabic "
        "languages (English, French, Urdu, etc.).\n"
        "  Example: query='mercy', translation='en.pickthall'  or  "
        "query='miséricorde', translation='fr.hamidullah'.\n\n"

        "• search_quran_by_themes — filter verses by thematic classification "
        "(chapter, topic, subtopic).\n"
        "  Example: topic='Prayer'  or  chapter='Stories of Prophets', "
        "subtopic='Prophet Ibrahim'.\n\n"

        "• search_quran_by_stats — filter verses by numeric attributes such as "
        "word count or verse count in a sura.\n"
        "  Example: words_in_verse='[5 TO 10]'  or  "
        "sortedby='ayalength', reverse=True (longest verses first).\n\n"

        "• search_quran_by_position — retrieve verses from a specific location "
        "such as a juz, hizb, page, sura, or verse number.\n"
        "  Example: juz='1'  or  sura_number='2', verse_number='255'  or  "
        "page='[1 TO 3]'.\n\n"

        "• search_by_word_linguistics — search word occurrences by morphological "
        "properties: root, part of speech, gender, number, person, voice, aspect, "
        "derivation, form, and more.\n"
        "  Example: root='رحم'  or  pos='فعل', voice='PASS'  or  "
        "aspect='PERF', number='P'.\n\n"

        "• get_quran_info — retrieve metadata such as chapter names, translations, "
        "recitations, and AI query rules.\n"
        "  Example: category='translations'  or  category='chapters'  or  "
        "category='ai_query_translation_rules'.\n\n"

        "• suggest_query — get auto-completion suggestions for a partial query.\n"
        "  Example: query='رحم' returns completions starting with that prefix.\n\n"

        "• correct_query — fix spelling mistakes before searching.\n"
        "  Example: query='الرخمن' → corrected to 'الرحمن'.\n\n"

        "• list_field_values — enumerate all unique indexed values for a field.\n"
        "  Example: field='pos' (all POS tags), field='trans_id' (all translation "
        "IDs), field='voice' (ACT / PASS).\n\n"

        "• get_word_children_schema — return the full schema and query syntax "
        "guide for word-level morphological data.\n\n"

        "QUERY SYNTAX SUMMARY\n"
        "--------------------\n"
        "Queries support Arabic script, Buckwalter transliteration, field filters "
        "(e.g. sura_id:2 aya_id:255), boolean operators (AND / OR / NOT), phrase "
        "search (\"…\"), wildcards (* and ?), fuzzy matching (~), and more.\n"
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
        "field-specific searches (e.g. sura_id:2 aya_id:255), fuzzy matching, "
        "synonyms, antonyms, and root-level derivations. "
        "Returns a paginated list of matching verses with metadata.\n\n"
        "EXAMPLES\n"
        "  Single Arabic keyword:       query='الرحمة'\n"
        "  Buckwalter transliteration:  query='rHmn'\n"
        "  Exact phrase:                query='\"بسم الله الرحمن الرحيم\"'\n"
        "  Boolean AND:                 query='رحمة AND مغفرة'\n"
        "  Boolean OR:                  query='رحمن OR رحيم'\n"
        "  Boolean NOT:                 query='صلاة NOT زكاة'\n"
        "  Wildcard prefix:             query='رحم*'\n"
        "  Single-char wildcard:        query='رح?ة'\n"
        "  Specific verse (Ayat al-Kursi): query='sura_id:2 aya_id:255'\n"
        "  Verses from Sura Al-Fatiha:  query='*', field_filter='sura_id:1'\n"
        "  Fuzzy matching:              query='الرحمان', fuzzy=True\n"
        "  Root-level derivations:      query='>>رحم' (expands to all root-رحم forms)\n"
        "  Longest verses first:        sortedby='ayalength', reverse=True\n"
        "  With English translation:    query='الإخلاص', translation='en.sahih'\n"
        "  Revelation order:            query='توحيد', sortedby='tanzil'"
    ),
)
def search_quran(
    query: str,
    unit: str = "aya",
    page: int = 1,
    perpage: int = 10,
    sortedby: str = "relevance",
    reverse: bool = False,
    fuzzy: bool = False,
    fuzzy_maxdist: int = 1,
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
        sortedby: Sort order — one of:
            - "relevance" / "score": rank by BM25 relevance (highest score
              first by default; use reverse=True for lowest score first).
            - "mushaf": traditional Qur'an order (sura then verse number).
            - "tanzil": revelation chronology order.
            - "ayalength": verse length in words (shortest first by default;
              use reverse=True for longest first).
        reverse: Reverse the sort direction (default False). When True the
            lowest/earliest value is returned first — e.g. shortest verse
            for "ayalength", or least-relevant result for "score".
        fuzzy: Enable fuzzy (approximate) matching. Combines exact search
            on aya_ with normalised/stemmed search on aya and Levenshtein
            distance matching on aya_ac.
        fuzzy_maxdist: Maximum Levenshtein edit distance for fuzzy term
            matching (default 1, only used when fuzzy=True).
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
        "perpage": perpage,
        "sortedby": sortedby,
        "reverse": reverse,
        "fuzzy": fuzzy,
        "fuzzy_maxdist": fuzzy_maxdist,
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
        "Returns a paginated list of matching translation snippets with verse metadata.\n\n"
        "EXAMPLES\n"
        "  Search all translations:     query='mercy'\n"
        "  Specific English translation: query='compassion', translation='en.pickthall'\n"
        "  Sahih International:         query='forgiveness', translation='en.sahih'\n"
        "  French translation:          query='miséricorde', translation='fr.hamidullah'\n"
        "  Urdu translation:            query='رحمت', translation='ur.jalandhry'\n"
        "  Exact phrase in English:     query='\"the most merciful\"'\n"
        "  With sura filter:            query='prayer', field_filter='sura_id:2'\n"
        "  Sorted by Qur'an order:      query='paradise', sortedby='mushaf'"
    ),
)
def search_translations(
    query: str,
    translation: Optional[str] = None,
    page: int = 1,
    perpage: int = 10,
    sortedby: str = "relevance",
    reverse: bool = False,
    fuzzy: bool = False,
    fuzzy_maxdist: int = 1,
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
        sortedby: Sort order — one of:
            - "relevance" / "score": rank by BM25 relevance (highest score
              first by default; use reverse=True for lowest score first).
            - "mushaf": traditional Qur'an order (sura then verse number).
            - "tanzil": revelation chronology order.
            - "ayalength": verse length in words (shortest first by default).
        reverse: Reverse the sort direction (default False). When True the
            lowest/earliest value is returned first.
        fuzzy: Enable fuzzy (approximate) matching. Combines exact search
            on aya_ with normalised/stemmed search on aya and Levenshtein
            distance matching on aya_ac.
        fuzzy_maxdist: Maximum Levenshtein edit distance for fuzzy term
            matching (default 1, only used when fuzzy=True).
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
        "perpage": perpage,
        "sortedby": sortedby,
        "reverse": reverse,
        "fuzzy": fuzzy,
        "fuzzy_maxdist": fuzzy_maxdist,
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
        "'ai_query_translation_rules', or 'all' for everything at once.\n\n"
        "EXAMPLES\n"
        "  List all chapter names:            category='chapters'\n"
        "  List all translation identifiers:  category='translations'\n"
        "    → returns IDs like 'en.sahih', 'en.pickthall', 'fr.hamidullah'\n"
        "  List available recitations:        category='recitations'\n"
        "  View default parameter values:     category='defaults'\n"
        "  View all valid parameter values:   category='domains'\n"
        "  List searchable index fields:      category='fields'\n"
        "  Get search tips and hints:         category='hints'\n"
        "  Get AI query translation guide:    category='ai_query_translation_rules'\n"
        "  Get everything at once:            category='all'"
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
    title="Search Qur'an by Themes",
    description=(
        "Search for Quranic verses by thematic classification. "
        "Filter by chapter (broad thematic division), topic (subject area), "
        "and/or subtopic within the Qur'an's thematic index. "
        "An optional free-text query can further narrow results. "
        "Use this tool when looking for verses on a specific theme or subject matter.\n\n"
        "EXAMPLES\n"
        "  Verses on prayer:                topic='Prayer'\n"
        "  Verses on a specific subtopic:   topic='Prayer', subtopic='Salah'\n"
        "  Broad thematic chapter:          chapter='Stories of Prophets'\n"
        "  Narrow to one prophet:           chapter='Stories of Prophets', "
        "subtopic='Prophet Ibrahim'\n"
        "  Theme + keyword filter:          chapter='Afterlife', query='جنة'\n"
        "  All available topics:            use list_field_values(field='topic') "
        "to discover valid topic names\n"
        "  Paginate results:                topic='Belief', page=2, perpage=20"
    ),
)
def search_quran_by_themes(
    query: str = "",
    chapter: Optional[str] = None,
    topic: Optional[str] = None,
    subtopic: Optional[str] = None,
    page: int = 1,
    perpage: int = 10,
    sortedby: str = "relevance",
    reverse: bool = False,
    view: str = "normal",
    highlight: str = "bold",
    facets: Optional[str] = None,
) -> dict:
    """Search for Quranic verses by thematic classification.

    Args:
        query: Optional free-text search query in Arabic or Buckwalter
            transliteration to further narrow results within the theme.
        chapter: Broad thematic chapter/division to filter by
            (maps to the 'chapter' field).
        topic: Topic or subject area to filter by (maps to the 'topic' field).
        subtopic: Subtopic to filter by (maps to the 'subtopic' field).
        page: Page number for pagination (starts at 1).
        perpage: Number of results per page (1–100).
        sortedby: Sort order — one of:
            - "relevance" / "score": rank by BM25 relevance (highest score
              first by default; use reverse=True for lowest score first).
            - "mushaf": traditional Qur'an order (sura then verse number).
            - "tanzil": revelation chronology order.
            - "ayalength": verse length in words (shortest first by default).
        reverse: Reverse the sort direction (default False). When True the
            lowest/earliest value is returned first.
        view: Result detail level — one of "minimal", "normal", "full",
            "statistic", "linguistic", or "custom".
        highlight: Highlight style for matched terms — one of "bold",
            "css", "html", or "bbcode".
        facets: Comma-separated list of fields to aggregate as facets.

    Returns:
        Dictionary with search results including matched verses, pagination
        info, and optional facets.
    """
    parts = []
    if query:
        parts.append(query)
    if chapter is not None:
        parts.append(f"chapter:{chapter}")
    if topic is not None:
        parts.append(f"topic:{topic}")
    if subtopic is not None:
        parts.append(f"subtopic:{subtopic}")

    combined_query = " ".join(parts) if parts else "*"

    flags: dict = {
        "action": "search",
        "query": combined_query,
        "unit": "aya",
        "page": page,
        "perpage": perpage,
        "sortedby": sortedby,
        "reverse": reverse,
        "view": view,
        "highlight": highlight,
    }
    if facets is not None:
        flags["facets"] = facets

    result = alfanous_api.do(flags)
    return _make_serializable(result)


@mcp.tool(
    title="Search Qur'an by Statistics",
    description=(
        "Search for Quranic verses by statistical attributes. "
        "Filter by the number of words in a verse, the number of words or "
        "verses in a sura, or other numeric statistical fields. "
        "Accepts exact values or Whoosh range expressions (e.g. '[5 TO 10]'). "
        "Use this tool for statistical or linguistic analysis of the Qur'an.\n\n"
        "EXAMPLES\n"
        "  Verses with exactly 4 words:     words_in_verse='4'\n"
        "  Verses with 5 to 10 words:       words_in_verse='[5 TO 10]'\n"
        "  Shortest verses first:           words_in_verse='[1 TO 100]', "
        "sortedby='ayalength'\n"
        "  Longest verses first:            sortedby='ayalength', reverse=True\n"
        "  Suras with more than 200 verses: verses_in_sura='[200 TO 300]'\n"
        "  Suras with exactly 7 verses:     verses_in_sura='7'\n"
        "  Verses in a large juz:           verses_to_juz='[150 TO 200]'\n"
        "  Combine with a text query:       query='الله', words_in_verse='[3 TO 6]'"
    ),
)
def search_quran_by_stats(
    query: str = "",
    words_in_verse: Optional[str] = None,
    words_in_sura: Optional[str] = None,
    verses_in_sura: Optional[str] = None,
    verses_to_juz: Optional[str] = None,
    suras_to_juz: Optional[str] = None,
    verses_to_hizb: Optional[str] = None,
    suras_to_hizb: Optional[str] = None,
    suras_to_ruku: Optional[str] = None,
    page: int = 1,
    perpage: int = 10,
    sortedby: str = "relevance",
    reverse: bool = False,
    view: str = "normal",
    highlight: str = "bold",
    facets: Optional[str] = None,
) -> dict:
    """Search for Quranic verses by statistical attributes.

    Args:
        query: Optional free-text search query in Arabic or Buckwalter
            transliteration to further narrow results.
        words_in_verse: Filter by number of words in the verse (field: a_w).
            Accepts an exact integer or a Whoosh range expression such as
            '[5 TO 10]'.
        words_in_sura: Filter by total word count of the sura (field: s_w).
        verses_in_sura: Filter by total verse count of the sura (field: s_a).
        verses_to_juz: Filter by cumulative verse count up to the verse's
            juz (field: a_g).
        suras_to_juz: Filter by cumulative sura count up to the verse's
            juz (field: s_g).
        verses_to_hizb: Filter by cumulative verse count up to the verse's
            hizb (field: a_l).
        suras_to_hizb: Filter by cumulative sura count up to the verse's
            hizb (field: s_l).
        suras_to_ruku: Filter by cumulative sura count up to the verse's
            ruku (field: s_r).
        page: Page number for pagination (starts at 1).
        perpage: Number of results per page (1–100).
        sortedby: Sort order — one of:
            - "relevance" / "score": rank by BM25 relevance (highest score
              first by default; use reverse=True for lowest score first).
            - "mushaf": traditional Qur'an order (sura then verse number).
            - "tanzil": revelation chronology order.
            - "ayalength": verse length in words (shortest first by default;
              use reverse=True for longest first).
        reverse: Reverse the sort direction (default False). When True the
            lowest/earliest value is returned first — e.g. set
            sortedby="ayalength" with reverse=True to get the longest verses.
        view: Result detail level — one of "minimal", "normal", "full",
            "statistic", "linguistic", or "custom".
        highlight: Highlight style for matched terms — one of "bold",
            "css", "html", or "bbcode".
        facets: Comma-separated list of fields to aggregate as facets.

    Returns:
        Dictionary with search results including matched verses, pagination
        info, and optional facets.
    """
    stat_filters = {
        "a_w": words_in_verse,
        "s_w": words_in_sura,
        "s_a": verses_in_sura,
        "a_g": verses_to_juz,
        "s_g": suras_to_juz,
        "a_l": verses_to_hizb,
        "s_l": suras_to_hizb,
        "s_r": suras_to_ruku,
    }

    parts = []
    if query:
        parts.append(query)
    for field, value in stat_filters.items():
        if value is not None:
            parts.append(f"{field}:{value}")

    combined_query = " ".join(parts) if parts else "*"

    flags: dict = {
        "action": "search",
        "query": combined_query,
        "unit": "aya",
        "page": page,
        "perpage": perpage,
        "sortedby": sortedby,
        "reverse": reverse,
        "view": view,
        "highlight": highlight,
    }
    if facets is not None:
        flags["facets"] = facets

    result = alfanous_api.do(flags)
    return _make_serializable(result)


@mcp.tool(
    title="Search Qur'an by Position",
    description=(
        "Search for Quranic verses by their structural position. "
        "Filter by sura (chapter) number, verse number, juz (part), "
        "hizb, ruku, or page. "
        "Accepts exact values or Whoosh range expressions (e.g. '[2 TO 5]'). "
        "Use this tool to retrieve verses from a specific location or range "
        "within the Qur'an's structural divisions.\n\n"
        "EXAMPLES\n"
        "  A single verse (Ayat al-Kursi):  sura_number='2', verse_number='255'\n"
        "  All verses of Sura Al-Fatiha:    sura_number='1'\n"
        "  Suras 2 through 4:               sura_number='[2 TO 4]'\n"
        "  All verses in the first juz:     juz='1'\n"
        "  First three juz:                 juz='[1 TO 3]'\n"
        "  Verses on a specific mushaf page: page='50'\n"
        "  Pages 1 to 5 of the mushaf:      page='[1 TO 5]'\n"
        "  Verse by global ID:              global_id='1' (Al-Fatiha:1)\n"
        "  Verses 1–7 of Sura Al-Baqarah:  sura_number='2', verse_number='[1 TO 7]'\n"
        "  Keyword within a sura range:     query='رحمة', sura_number='[1 TO 10]'\n"
        "  Reverse (last verse first):      sura_number='114', reverse=True"
    ),
)
def search_quran_by_position(
    query: str = "",
    sura_number: Optional[str] = None,
    verse_number: Optional[str] = None,
    global_id: Optional[str] = None,
    juz: Optional[str] = None,
    hizb: Optional[str] = None,
    ruku: Optional[str] = None,
    rub: Optional[str] = None,
    page: Optional[str] = None,
    page_int: int = 1,
    perpage: int = 10,
    sortedby: str = "mushaf",
    reverse: bool = False,
    view: str = "normal",
    highlight: str = "bold",
    facets: Optional[str] = None,
) -> dict:
    """Search for Quranic verses by structural position.

    Args:
        query: Optional free-text search query in Arabic or Buckwalter
            transliteration to further narrow results.
        sura_number: Sura (chapter) number (1–114) to filter by
            (field: sura_id). Accepts an exact integer or a Whoosh range
            expression such as '[2 TO 5]'.
        verse_number: Verse number within its sura (1–286) to filter by
            (field: aya_id).
        global_id: Global verse ID across the entire Qur'an (1–6236)
            (field: gid).
        juz: Juz (part) number (1–30) to filter by (field: juz).
        hizb: Hizb number to filter by (field: hizb).
        ruku: Ruku number to filter by (field: ruk).
        rub: Rub (quarter) number to filter by (field: rub).
        page: Mushaf page number to filter by (field: page).
        page_int: Page number for pagination (starts at 1).
        perpage: Number of results per page (1–100).
        sortedby: Sort order — one of:
            - "mushaf": traditional Qur'an order — sura then verse number
              (default for positional queries).
            - "tanzil": revelation chronology order.
            - "relevance" / "score": rank by BM25 relevance.
            - "ayalength": verse length in words.
        reverse: Reverse the sort direction (default False). For example,
            sortedby="mushaf" with reverse=True returns verses in
            reverse Qur'an order (last verse first).
        view: Result detail level — one of "minimal", "normal", "full",
            "statistic", "linguistic", or "custom".
        highlight: Highlight style for matched terms — one of "bold",
            "css", "html", or "bbcode".
        facets: Comma-separated list of fields to aggregate as facets.

    Returns:
        Dictionary with search results including matched verses, pagination
        info, and optional facets.
    """
    position_filters = {
        "sura_id": sura_number,
        "aya_id": verse_number,
        "gid": global_id,
        "juz": juz,
        "hizb": hizb,
        "ruk": ruku,
        "rub": rub,
        "page": page,
    }

    parts = []
    if query:
        parts.append(query)
    for field, value in position_filters.items():
        if value is not None:
            parts.append(f"{field}:{value}")

    combined_query = " ".join(parts) if parts else "*"

    flags: dict = {
        "action": "search",
        "query": combined_query,
        "unit": "aya",
        "page": page_int,
        "perpage": perpage,
        "sortedby": sortedby,
        "reverse": reverse,
        "view": view,
        "highlight": highlight,
    }
    if facets is not None:
        flags["facets"] = facets

    result = alfanous_api.do(flags)
    return _make_serializable(result)


@mcp.tool(
    title="Suggest Query Completions",
    description=(
        "Get auto-completion suggestions for a partial Quranic search query. "
        "Useful for helping users refine their queries or correct spelling.\n\n"
        "EXAMPLES\n"
        "  Suggest completions for 'رحم':   query='رحم'\n"
        "    → may return 'رحمة', 'رحمن', 'رحيم', …\n"
        "  Suggest completions for 'Allh':  query='Allh', unit='aya' "
        "(Buckwalter prefix)\n"
        "  Suggest word-index completions:  query='رحم', unit='word'\n"
        "  Suggest translation completions: query='merc', unit='translation'"
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


@mcp.tool(
    title="Correct Query Spelling",
    description=(
        "Correct spelling mistakes in a Quranic search query. "
        "Uses the Whoosh query corrector to replace unknown terms with the "
        "closest matching terms found in the index vocabulary. "
        "Returns the original query alongside the best corrected version. "
        "When the query is already valid the corrected string is identical to "
        "the original. Useful as a pre-processing step before calling "
        "search_quran.\n\n"
        "EXAMPLES\n"
        "  Misspelled Arabic:   query='الرخمن'  → corrected: 'الرحمن'\n"
        "  Misspelled Buckwalter: query='rHmAn'  → corrected to nearest term\n"
        "  Already correct:     query='الرحمن'  → corrected equals original\n"
        "  Multi-term query:    query='رحمة مغفره' → corrects each term\n"
        "  Typical workflow:    1) correct_query('الرخمن')  "
        "2) search_quran(corrected_term)"
    ),
)
def correct_query(query: str, unit: str = "aya") -> dict:
    """Correct spelling mistakes in a Quranic search query.

    Args:
        query: Query string to correct.
        unit: Search unit — one of "aya" (verse), "word", or "translation".
              Only "aya" is currently supported; other units return None.

    Returns:
        Dictionary with 'correct_query' containing 'original' and 'corrected'
        query strings, plus the standard error envelope.
    """
    result = alfanous_api.correct_query(query=query, unit=unit)
    return _make_serializable(result)


@mcp.tool(
    title="Search Qur'an Words by Linguistics",
    description=(
        "Search Quranic word occurrences by their morphological and linguistic "
        "properties. Each word token in the Qur'an is indexed with its part of "
        "speech, grammatical type, Arabic root, lemma, gender, number, person, "
        "verb aspect, voice, nominal state, derivation, and more. "
        "Use this tool for linguistic analysis — e.g. find all nouns derived "
        "from a specific root, all verbs in the passive voice, or all words "
        "with a particular part of speech. "
        "An optional free-text query can also search the vocalized or "
        "unvocalized word form directly.\n\n"
        "EXAMPLES\n"
        "  All words from root رحم:             root='رحم'\n"
        "  All verb occurrences:                pos='فعل'\n"
        "  All passive verbs:                   pos='فعل', voice='PASS'\n"
        "  Passive verbs from root كتب:         root='كتب', voice='PASS'\n"
        "  Perfect-tense verbs:                 aspect='PERF'\n"
        "  Imperfect (present/future) verbs:    aspect='IMPF'\n"
        "  Imperative verbs:                    aspect='IMPV'\n"
        "  Form-II verbs:                       pos='فعل', form='(II)'\n"
        "  Plural nouns:                        word_type='Nouns', number='P'\n"
        "  Feminine dual nouns:                 word_type='Nouns', gender='F', number='D'\n"
        "  Active participles from root عمل:    root='عمل', derivation='ACT PCPL'\n"
        "  Verbal nouns (masdar):               derivation='VN'\n"
        "  Specific vocalized form:             query='الرَّحْمَنِ'\n"
        "  Unvocalized form (any diacritics):   query='الرحمن' (searches normalized)\n"
        "  Words with lemma رَحِيم:             lemma='رَحِيم'\n"
        "  Third-person masculine singular:     person='3', gender='M', number='S'"
    ),
)
def search_by_word_linguistics(
    query: str = "",
    pos: Optional[str] = None,
    word_type: Optional[str] = None,
    root: Optional[str] = None,
    lemma: Optional[str] = None,
    gender: Optional[str] = None,
    number: Optional[str] = None,
    person: Optional[str] = None,
    voice: Optional[str] = None,
    state: Optional[str] = None,
    derivation: Optional[str] = None,
    aspect: Optional[str] = None,
    form: Optional[str] = None,
    page: int = 1,
    perpage: int = 10,
    sortedby: str = "mushaf",
    reverse: bool = False,
    highlight: str = "bold",
) -> dict:
    """Search Quranic word occurrences by morphological/linguistic properties.

    Args:
        query: Optional free-text query searching the vocalized word form and
            the unvocalized normalized form (Arabic or Buckwalter).
        pos: Part of speech in Arabic script (e.g. "اسم" for Noun, "فعل" for
            Verb, "حرف" for Particle, "صفة" for Adjective, "ضمير" for Pronoun).
        word_type: Grammatical type category (e.g. "Nouns", "Verbs",
            "Particles", "Pronouns").
        root: Root in Arabic script (e.g. "رحم", "كتب", "عبد").
        lemma: Lemma in Arabic script (e.g. "رَحِيم", "كِتَاب").
        gender: Grammatical gender — "M" (masculine) or "F" (feminine).
        number: Grammatical number — "S" (singular), "D" (dual), or "P" (plural).
        person: Grammatical person — "1", "2", or "3".
        voice: Verb voice — "ACT" (active) or "PASS" (passive).
        state: Nominal state in Arabic script (e.g. "نكرة" for indefinite).
        derivation: Derivation type — "ACT PCPL" (active participle),
            "PASS PCPL" (passive participle), or "VN" (verbal noun).
        aspect: Verb aspect — "PERF" (perfect), "IMPF" (imperfect), or
            "IMPV" (imperative).
        form: Verb form in Roman numerals — one of "(I)" through "(XII)".
        page: Page number for pagination (starts at 1).
        perpage: Number of results per page (1–25).
        sortedby: Sort order — one of:
            - "mushaf": traditional Qur'an order — sura then verse number
              (default for word searches).
            - "relevance" / "score": rank by BM25 relevance.
            - "tanzil": revelation chronology order.
            - "ayalength": verse length in words.
        reverse: Reverse the sort direction (default False). When True the
            lowest/earliest value is returned first — e.g. sortedby="mushaf"
            with reverse=True returns occurrences from the last verse first.
        highlight: Highlight style for matched word text — one of "bold",
            "css", "html", or "bbcode".

    Returns:
        Dictionary with word search results including matched word occurrences
        with their full linguistic annotation and pagination info.
    """
    # Build field-specific query parts
    linguistic_filters = {
        "pos":        pos,
        "type":       word_type,
        "root":       root,
        "lemma":      lemma,
        "gender":     gender,
        "number":     number,
        "person":     person,
        "voice":      voice,
        "state":      state,
        "derivation": derivation,
        "aspect":     aspect,
        "form":       form,
    }

    parts = []
    if query:
        parts.append(query)
    for field, value in linguistic_filters.items():
        if value is not None:
            # Quote multi-word values so the parser treats them as a phrase.
            safe_value = f'"{value}"' if " " in value else value
            parts.append(f"{field}:{safe_value}")

    combined_query = " ".join(parts) if parts else "*"

    flags: dict = {
        "action":   "search",
        "query":    combined_query,
        "unit":     "word",
        "page":     page,
        "perpage":  perpage,
        "sortedby": sortedby,
        "reverse":  reverse,
        "highlight": highlight,
    }

    result = alfanous_api.do(flags)
    return _make_serializable(result)


# ---------------------------------------------------------------------------
# Word children schema documentation tool
# ---------------------------------------------------------------------------

#: Complete documentation for the word children schema and search syntax.
_WORD_CHILDREN_SCHEMA_DOC = """\
Quranic Word Children — Schema and Search Guide
================================================

Every word token in the Qur'an is indexed as a "word child" document nested
under its parent aya (verse) document.  Word children carry ``kind="word"``
and can be searched with ``unit="word"`` in the API or via the
``search_by_word_linguistics`` MCP tool.

INDEXED FIELDS (searchable with field:value syntax)
----------------------------------------------------
| Field        | Type    | Description                                      |
|--------------|---------|--------------------------------------------------|
| word         | TEXT    | Vocalized (fully diacritised) Arabic word form   |
| normalized   | TEXT    | Unvocalized / lightly normalised Arabic form     |
| pos          | ID      | Part of speech in Arabic script                  |
|              |         |   اسم = Noun, فعل = Verb, حرف = Particle,        |
|              |         |   صفة = Adjective, ضمير = Pronoun                 |
| type         | ID      | Broad grammatical type (Nouns, Verbs, Particles, |
|              |         |   Pronouns, Adjectives, etc.)                    |
| root         | ID      | Consonantal root in Arabic (e.g. رحم, كتب, عبد) |
| arabicroot   | ID      | Alternative Arabic root form                     |
| lemma        | ID      | Lemma in Arabic script (e.g. رَحِيم, كِتَاب)     |
| arabiclemma  | ID      | Alternative Arabic lemma form                    |
| gender       | ID      | Grammatical gender: M (masculine), F (feminine)  |
| number       | ID      | Grammatical number: S (singular), D (dual),      |
|              |         |   P (plural)                                     |
| person       | ID      | Grammatical person: 1, 2, 3                      |
| form         | ID      | Verb form in Roman numerals: (I)–(XII)           |
| voice        | ID      | Verb voice: ACT (active), PASS (passive)         |
| state        | ID      | Nominal state in Arabic (نكرة = indefinite, etc.)|
| englishstate | ID      | Nominal state in English ("Definite state",      |
|              |         |   "Indefinite state")                            |
| derivation   | ID      | Derivation type: ACT PCPL, PASS PCPL, VN         |
| aspect       | ID      | Verb aspect: PERF, IMPF, IMPV                    |
| mood         | ID      | Verb mood in Arabic script                       |
| englishmood  | ID      | Verb mood in English ("Indicative mood",         |
|              |         |   "Subjunctive mood", "Jussive mood")            |
| case         | ID      | Grammatical case in Arabic script                |

STORED-ONLY FIELDS (returned in results but not searchable)
-----------------------------------------------------------
| Field        | Description                                              |
|--------------|----------------------------------------------------------|
| spelled      | Fully normalised and spelled-out Arabic form             |
| englishpos   | Part of speech in English (e.g. "N", "V", "P", "ADJ")  |
| englishcase  | Grammatical case in English (NOM, ACC, GEN)              |
| prefix       | Cliticised prefixes separated by semicolons              |
| suffix       | Cliticised suffixes separated by semicolons              |
| special      | Special morphological note in Arabic                     |

IDENTIFIER FIELDS (for locating the word in the Qur'an)
-------------------------------------------------------
| Field        | Description                                              |
|--------------|----------------------------------------------------------|
| word_id      | Sequential word position within the aya (1-based)        |
| aya_id       | Verse number within the surah                            |
| sura_id      | Surah (chapter) number                                   |
| gid          | Global aya ID of the parent verse (1–6236)               |

PARENT-CHILD NESTING
--------------------
Word children are grouped under parent aya documents using Whoosh's block
nesting.  A ``NestedParent`` query can retrieve the parent aya of any
matching word child:

    from whoosh.query import NestedParent, Term, And
    child_q  = And([Term("kind", "word"), Term("root", "رحم")])
    parent_q = NestedParent(Term("kind", "aya"), child_q)

SEARCH EXAMPLES
---------------
Find all verb occurrences:
    unit=word  query=pos:فعل

Find words with root رحم:
    unit=word  query=root:رحم

Find passive verbs derived from root كتب:
    unit=word  query=root:كتب AND voice:PASS

Find plural nouns:
    unit=word  query=type:Nouns AND number:P

Find active participles:
    unit=word  query=derivation:"ACT PCPL"

Find a specific word form (vocalized):
    unit=word  query=word:الرَّحْمَنِ

Find unvocalized form across all diacritisations:
    unit=word  query=normalized:الرحمن

MCP TOOL
--------
Use ``search_by_word_linguistics`` to search word children with named
parameters (pos, root, lemma, gender, number, voice, etc.) without needing
to compose raw query strings.

QUERY SYNTAX EXTENSIONS
------------------------
Two Quranic parser plugins operate at the *aya* search level (unit="aya")
but internally expand to word children for their match sets:

  {root,type}      Tuple query — finds ayas containing words with the
                   specified root and type (e.g. {رحم,اسم} = noun from رحم).

  >word / >>word   Derivation query — expands a word to lemma-level (>)
                   or root-level (>>) derivations before searching the aya
                   index (e.g. >>مالك finds all root-ملك occurrences).

Both now query the live word-children index when available.
"""


@mcp.tool(
    title="Get Word Children Schema",
    description=(
        "Return detailed documentation about the Quranic word children schema "
        "and how to search word-level morphological data. "
        "Covers all indexed fields (part of speech, root, lemma, gender, number, "
        "person, voice, aspect, derivation, and more), parent-child nesting logic, "
        "query syntax examples, and the relationship between word children and the "
        "aya-level tuple/derivation query plugins.\n\n"
        "WHEN TO USE\n"
        "  Call this tool before using search_by_word_linguistics for the first "
        "time to understand all available fields, accepted values, and query "
        "syntax. Also useful when constructing advanced raw queries with "
        "unit='word'.\n\n"
        "EXAMPLES OF WHAT IT DOCUMENTS\n"
        "  • All 25+ indexed fields with their types and accepted values\n"
        "  • How to compose raw word queries: pos:فعل AND voice:PASS\n"
        "  • Tuple plugin syntax: {رحم,اسم} → nouns from root رحم (unit='aya')\n"
        "  • Derivation plugin: >>مالك → all root-ملك occurrences (unit='aya')\n"
        "  • Parent-child nesting for retrieving parent verses of matching words"
    ),
)
def get_word_children_schema() -> dict:
    """Return documentation for the Quranic word children schema.

    Returns:
        Dictionary with:
        - ``schema``: Full schema documentation as plain text.
        - ``fields``: Structured field catalogue as a list of dicts.
        - ``examples``: A list of query example dicts.
    """
    fields = [
        # Indexed text / ID fields
        {"name": "word",         "type": "TEXT",    "searchable": True,
         "description": "Vocalized Arabic word form"},
        {"name": "normalized",   "type": "TEXT",    "searchable": True,
         "description": "Unvocalized normalised Arabic form"},
        {"name": "pos",          "type": "ID",      "searchable": True,
         "description": "Part of speech (Arabic): اسم Noun, فعل Verb, حرف Particle"},
        {"name": "type",         "type": "ID",      "searchable": True,
         "description": "Broad grammatical type (Nouns, Verbs, Particles, …)"},
        {"name": "root",         "type": "ID",      "searchable": True,
         "description": "Arabic consonantal root (e.g. رحم, كتب)"},
        {"name": "arabicroot",   "type": "ID",      "searchable": True,
         "description": "Alternative Arabic root form"},
        {"name": "lemma",        "type": "ID",      "searchable": True,
         "description": "Arabic lemma"},
        {"name": "arabiclemma",  "type": "ID",      "searchable": True,
         "description": "Alternative Arabic lemma form"},
        {"name": "gender",       "type": "ID",      "searchable": True,
         "description": "Grammatical gender: M or F"},
        {"name": "number",       "type": "ID",      "searchable": True,
         "description": "Grammatical number: S, D, or P"},
        {"name": "person",       "type": "ID",      "searchable": True,
         "description": "Grammatical person: 1, 2, or 3"},
        {"name": "form",         "type": "ID",      "searchable": True,
         "description": "Verb form (I)–(XII)"},
        {"name": "voice",        "type": "ID",      "searchable": True,
         "description": "Verb voice: ACT or PASS"},
        {"name": "state",        "type": "ID",      "searchable": True,
         "description": "Nominal state (Arabic)"},
        {"name": "derivation",   "type": "ID",      "searchable": True,
         "description": "Derivation type: ACT PCPL, PASS PCPL, or VN"},
        {"name": "aspect",       "type": "ID",      "searchable": True,
         "description": "Verb aspect: PERF, IMPF, or IMPV"},
        {"name": "mood",         "type": "ID",      "searchable": True,
         "description": "Verb mood (Arabic)"},
        {"name": "case",         "type": "ID",      "searchable": True,
         "description": "Grammatical case (Arabic)"},
        # Stored-only fields
        {"name": "spelled",      "type": "STORED",  "searchable": False,
         "description": "Fully normalised spelled-out Arabic form"},
        {"name": "englishpos",   "type": "STORED",  "searchable": False,
         "description": "Part of speech in English"},
        {"name": "englishmood",  "type": "ID",      "searchable": True,
         "description": "Verb mood in English (e.g. 'Indicative mood', 'Jussive mood', 'Subjunctive mood')"},
        {"name": "englishcase",  "type": "STORED",  "searchable": False,
         "description": "Grammatical case in English (NOM, ACC, GEN)"},
        {"name": "englishstate", "type": "ID",      "searchable": True,
         "description": "Nominal state in English (e.g. 'Definite state', 'Indefinite state')"},
        {"name": "prefix",       "type": "KEYWORD", "searchable": False,
         "description": "Cliticised prefixes (semicolon-separated)"},
        {"name": "suffix",       "type": "KEYWORD", "searchable": False,
         "description": "Cliticised suffixes (semicolon-separated)"},
        {"name": "special",      "type": "STORED",  "searchable": False,
         "description": "Special morphological note (Arabic)"},
        # Identifier fields
        {"name": "word_id",      "type": "NUMERIC", "searchable": True,
         "description": "Word position within the aya (1-based)"},
        {"name": "aya_id",       "type": "NUMERIC", "searchable": True,
         "description": "Verse number within the surah"},
        {"name": "sura_id",      "type": "NUMERIC", "searchable": True,
         "description": "Surah (chapter) number"},
        {"name": "gid",          "type": "NUMERIC", "searchable": True,
         "description": "Global aya ID of the parent verse (1–6236)"},
    ]

    examples = [
        {"description": "Find all verb occurrences",
         "unit": "word", "query": "pos:فعل"},
        {"description": "Find words with root رحم",
         "unit": "word", "query": "root:رحم"},
        {"description": "Find passive verbs from root كتب",
         "unit": "word", "query": "root:كتب AND voice:PASS"},
        {"description": "Find plural nouns",
         "unit": "word", "query": "type:Nouns AND number:P"},
        {"description": "Find active participles",
         "unit": "word", "query": 'derivation:"ACT PCPL"'},
        {"description": "Find a specific vocalized word form",
         "unit": "word", "query": "word:الرَّحْمَنِ"},
        {"description": "Find all diacritisations of an unvocalized form",
         "unit": "word", "query": "normalized:الرحمن"},
        {"description": "Find ayas with nouns from root رحم (tuple plugin)",
         "unit": "aya",  "query": "{رحم,اسم}"},
        {"description": "Find ayas with root-level derivations of مالك",
         "unit": "aya",  "query": ">>مالك"},
    ]

    return {
        "schema": _WORD_CHILDREN_SCHEMA_DOC,
        "fields": fields,
        "examples": examples,
    }


# ---------------------------------------------------------------------------
# List indexed field values tool
# ---------------------------------------------------------------------------

#: Word annotation fields whose values can be discovered via list_field_values.
_WORD_ANNOTATION_FIELDS = [
    {"field": "pos",        "description": "Part of speech in Arabic script (e.g. اسم Noun, فعل Verb, حرف Particle, صفة Adjective, ضمير Pronoun)"},
    {"field": "type",       "description": "Broad grammatical type in English (e.g. Nouns, Verbs, Particles, Pronouns)"},
    {"field": "root",       "description": "Arabic consonantal root (e.g. رحم, كتب, عبد)"},
    {"field": "lemma",      "description": "Arabic lemma (vocalized citation form)"},
    {"field": "gender",     "description": "Grammatical gender — M (masculine) or F (feminine)"},
    {"field": "number",     "description": "Grammatical number — S (singular), D (dual), or P (plural)"},
    {"field": "person",     "description": "Grammatical person — 1, 2, or 3"},
    {"field": "voice",      "description": "Verb voice — ACT (active) or PASS (passive)"},
    {"field": "aspect",     "description": "Verb aspect — PERF (perfect), IMPF (imperfect), or IMPV (imperative)"},
    {"field": "form",       "description": "Verb form in Roman numerals — (I) through (XII)"},
    {"field": "derivation", "description": "Derivation type — ACT PCPL (active participle), PASS PCPL (passive participle), or VN (verbal noun)"},
    {"field": "state",      "description": "Nominal state in Arabic script (e.g. نكرة indefinite)"},
    {"field": "mood",       "description": "Verb mood in Arabic script"},
    {"field": "case",       "description": "Grammatical case in Arabic script"},
    # Translation-related fields
    {"field": "trans_id",   "description": "Translation identifier (e.g. 'en.sahih', 'fr.hamidullah', 'ar.jalalayn'). Use list_field_values('trans_id') to enumerate all available translations."},
    {"field": "trans_lang", "description": "Translation language code (e.g. 'en', 'fr', 'ar', 'id', 'ja')"},
]


@mcp.tool(
    title="List Indexed Field Values",
    description=(
        "Return every unique value indexed for a given field. "
        "Use this to discover available word annotation categories "
        "(part of speech, grammatical gender, number, verb aspect, voice, "
        "derivation, etc.) before calling search_by_word_linguistics, or to "
        "see the available translation identifiers before calling "
        "search_translations. "
        "Call with field='pos' for all part-of-speech tags, field='gender' "
        "for all gender values, field='trans_id' for all translation IDs, "
        "and so on. "
        "The tool also returns a catalogue of well-known word-annotation "
        "fields and translation-related fields as a convenience reference.\n\n"
        "EXAMPLES\n"
        "  All part-of-speech tags:           field='pos'\n"
        "    → returns e.g. 'اسم', 'فعل', 'حرف', 'صفة', 'ضمير'\n"
        "  All grammatical gender values:     field='gender'\n"
        "    → returns 'M', 'F'\n"
        "  All grammatical number values:     field='number'\n"
        "    → returns 'S', 'D', 'P'\n"
        "  All verb aspect values:            field='aspect'\n"
        "    → returns 'PERF', 'IMPF', 'IMPV'\n"
        "  All verb voice values:             field='voice'\n"
        "    → returns 'ACT', 'PASS'\n"
        "  All derivation types:              field='derivation'\n"
        "    → returns 'ACT PCPL', 'PASS PCPL', 'VN'\n"
        "  All verb forms:                    field='form'\n"
        "    → returns '(I)', '(II)', …, '(XII)'\n"
        "  All translation identifiers:       field='trans_id'\n"
        "    → returns e.g. 'en.sahih', 'en.pickthall', 'fr.hamidullah'\n"
        "  All translation language codes:    field='trans_lang'\n"
        "    → returns e.g. 'en', 'fr', 'ar', 'ur', 'id'"
    ),
)
def list_field_values(field: str) -> dict:
    """Return all unique indexed values for a given Quranic index field.

    Useful for discovering the complete set of possible values for categorical
    word-annotation fields (e.g. ``pos``, ``gender``, ``number``, ``aspect``,
    ``voice``, ``derivation``) or translation metadata fields (e.g.
    ``trans_id``, ``trans_lang``) before composing a search query.

    Args:
        field: The indexed field name to query.  Well-known word annotation
            fields include ``pos``, ``type``, ``root``, ``lemma``,
            ``gender``, ``number``, ``person``, ``voice``, ``aspect``,
            ``form``, ``derivation``, ``state``, ``mood``, and ``case``.
            Translation-related fields include ``trans_id`` and
            ``trans_lang``.  Use ``get_quran_info('translations')`` for the
            full translation catalogue including author names.

    Returns:
        Dictionary with:
        - ``field``: the queried field name
        - ``values``: sorted list of unique values in the index
        - ``count``: number of distinct values returned
        - ``word_annotation_fields``: catalogue of well-known word annotation
          fields with descriptions (always returned for reference)
        - ``error``: (only present on failure) human-readable error message
    """
    result = alfanous_api.list_values(field)
    serializable = _make_serializable(result)

    # Attach the field catalogue so the caller has a built-in reference.
    serializable["word_annotation_fields"] = _WORD_ANNOTATION_FIELDS
    return serializable


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
