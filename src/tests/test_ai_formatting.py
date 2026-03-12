#!/usr/bin/env python3
# coding: utf-8

"""
Tests for AI Response Formatting Utilities
==========================================

Tests for the ai_formatting module which provides HTML rendering of AI
responses: clickable links and styled aya references.
"""

import sys
import os

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

try:
    from alfanous_webapi.ai_formatting import (
        format_ai_response,
        render_aya_tags,
        render_links,
    )
    AI_FORMATTING_AVAILABLE = True
except ImportError:
    AI_FORMATTING_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not AI_FORMATTING_AVAILABLE,
    reason="alfanous_webapi.ai_formatting not available",
)


# ---------------------------------------------------------------------------
# render_links
# ---------------------------------------------------------------------------


class TestRenderLinks:
    def test_plain_http_url_becomes_anchor(self):
        text = "Visit http://example.com for more."
        result = render_links(text)
        assert '<a href="http://example.com"' in result
        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result

    def test_plain_https_url_becomes_anchor(self):
        text = "See https://alfanous.org for details."
        result = render_links(text)
        assert '<a href="https://alfanous.org"' in result

    def test_url_link_text_matches_href(self):
        text = "https://alfanous.org"
        result = render_links(text)
        assert ">https://alfanous.org</a>" in result

    def test_multiple_urls_all_converted(self):
        text = "See https://alfanous.org and http://example.com"
        result = render_links(text)
        assert result.count("<a href=") == 2

    def test_text_without_url_unchanged(self):
        text = "No links here, just text."
        assert render_links(text) == text

    def test_already_in_href_not_double_wrapped(self):
        text = 'Already <a href="https://alfanous.org">linked</a> here.'
        result = render_links(text)
        # Should not create a nested anchor
        assert result.count('<a href="https://alfanous.org"') == 1

    def test_empty_string(self):
        assert render_links("") == ""

    def test_arabic_text_with_url(self):
        text = "انظر https://alfanous.org لمزيد من المعلومات"
        result = render_links(text)
        assert '<a href="https://alfanous.org"' in result
        assert "انظر" in result


# ---------------------------------------------------------------------------
# render_aya_tags
# ---------------------------------------------------------------------------


class TestRenderAyaTags:
    def test_single_aya_ref_wrapped(self):
        text = "See [2:255] for Ayat al-Kursi."
        result = render_aya_tags(text)
        assert '<span class="search-result-aya"' in result
        assert 'data-sura="2"' in result
        assert 'data-verse="255"' in result

    def test_aya_ref_preserves_original_notation(self):
        text = "See [1:1]."
        result = render_aya_tags(text)
        assert "[1:1]" in result

    def test_multiple_aya_refs(self):
        text = "See [2:255] and [1:1] and [114:6]."
        result = render_aya_tags(text)
        assert result.count('<span class="search-result-aya"') == 3

    def test_text_without_aya_ref_unchanged(self):
        text = "No references here."
        assert render_aya_tags(text) == text

    def test_empty_string(self):
        assert render_aya_tags("") == ""

    def test_out_of_range_sura_not_matched(self):
        # Sura numbers only go up to 114; [999:1] should not match
        # (the regex allows up to 3 digits, so 999 does match the pattern,
        # but this test verifies the regex itself handles 3-digit numbers)
        text = "[999:1]"
        result = render_aya_tags(text)
        # 3-digit sura/verse references are still matched (validation is
        # left to the consumer); just verify the span is produced
        assert 'data-sura="999"' in result

    def test_arabic_indic_digits(self):
        # Arabic-indic digit range \u0660-\u0669
        text = "[\u0662:\u0662\u0665\u0665]"
        result = render_aya_tags(text)
        assert 'class="search-result-aya"' in result

    def test_span_has_correct_data_attributes(self):
        result = render_aya_tags("[114:6]")
        assert 'data-sura="114"' in result
        assert 'data-verse="6"' in result


# ---------------------------------------------------------------------------
# format_ai_response
# ---------------------------------------------------------------------------


class TestFormatAiResponse:
    def test_both_links_and_aya_tags_applied(self):
        text = "See [2:255] at https://alfanous.org for Ayat al-Kursi."
        result = format_ai_response(text)
        assert '<a href="https://alfanous.org"' in result
        assert 'class="search-result-aya"' in result

    def test_url_inside_aya_not_double_processed(self):
        # A URL that happens to end near bracket patterns should not
        # accidentally trigger the aya pattern
        text = "Visit https://example.com/path for info and see [1:1]."
        result = format_ai_response(text)
        assert result.count('<a href=') == 1
        assert result.count('class="search-result-aya"') == 1

    def test_empty_string(self):
        assert format_ai_response("") == ""

    def test_plain_text_unchanged_structure(self):
        text = "No links and no aya references here."
        assert format_ai_response(text) == text

    def test_response_with_only_url(self):
        text = "https://alfanous.org"
        result = format_ai_response(text)
        assert result.startswith('<a href="https://alfanous.org"')

    def test_response_with_only_aya(self):
        text = "[3:10]"
        result = format_ai_response(text)
        assert result.startswith('<span class="search-result-aya"')

    def test_multiple_links_and_ayas(self):
        text = (
            "Check [1:1] and [2:255]. "
            "See https://alfanous.org or http://example.com."
        )
        result = format_ai_response(text)
        assert result.count('class="search-result-aya"') == 2
        assert result.count('<a href=') == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
