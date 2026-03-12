#!/usr/bin/env python3
# coding: utf-8

"""
AI Response Formatting Utilities
==================================

Provides helper functions for rendering AI-generated text as HTML:

* ``render_links``   – Convert bare URLs in text to clickable ``<a>`` tags.
* ``render_aya_tags`` – Wrap Quranic aya references (e.g. ``[2:255]``) in
  a styled ``<span>`` so they can be styled identically to the main aya
  element in the aya-search results view.
* ``format_ai_response`` – Apply both transformations in one call.

These utilities are used by the ``ask-ai`` endpoints so that:
  1. Any link the AI includes in its response is rendered as a clickable
     anchor tag in the front-end UI.
  2. Any aya the AI suggests is wrapped in ``<span class="search-result-aya">``
     so CSS rules that style the main aya display in search results also apply
     to AI-suggested ayas automatically.
"""

import re

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# Matches http:// and https:// URLs that are not already inside an HTML tag.
# Stops at whitespace and a small set of forbidden characters to avoid
# swallowing trailing punctuation that is part of the surrounding sentence.
_URL_PATTERN = re.compile(
    r'(?<!["\'=>])(https?://[^\s<>"\'`{}\[\]\\^|]+)',
    re.IGNORECASE,
)

# Matches Quranic aya references in the shorthand form [sura:verse], e.g.
# [2:255], [1:1], [114:6].  Both Arabic-indic and ASCII digits are supported.
_AYA_REF_PATTERN = re.compile(
    r"\[([0-9\u0660-\u0669]{1,3}):([0-9\u0660-\u0669]{1,3})\]"
)

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def render_links(text: str) -> str:
    """Convert bare URLs in *text* to HTML anchor tags.

    URLs that are already wrapped inside an HTML tag attribute (e.g.
    ``href="…"``) are not double-wrapped because the regex anchors on the
    absence of a preceding quote character.

    Args:
        text: Plain or partially-HTML text that may contain bare URLs.

    Returns:
        Text with every bare URL replaced by
        ``<a href="URL" target="_blank" rel="noopener noreferrer">URL</a>``.

    Example::

        >>> render_links("Visit https://alfanous.org for more.")
        'Visit <a href="https://alfanous.org" target="_blank" rel="noopener noreferrer">https://alfanous.org</a> for more.'
    """
    return _URL_PATTERN.sub(
        r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',
        text,
    )


def render_aya_tags(text: str) -> str:
    """Wrap Quranic aya shorthand references in a styled HTML ``<span>``.

    Recognises the notation ``[sura:verse]`` (e.g. ``[2:255]``) and replaces
    it with::

        <span class="search-result-aya" data-sura="2" data-verse="255">[2:255]</span>

    The CSS class ``search-result-aya`` matches the class used for the main
    aya display in the aya-search results view, so front-end styling is
    automatically shared.

    Args:
        text: Text that may contain ``[sura:verse]`` references.

    Returns:
        Text with every ``[sura:verse]`` wrapped in the styled span.

    Example::

        >>> render_aya_tags("See [2:255] and [1:1].")
        'See <span class="search-result-aya" data-sura="2" data-verse="255">[2:255]</span> and <span class="search-result-aya" data-sura="1" data-verse="1">[1:1]</span>.'
    """
    return _AYA_REF_PATTERN.sub(
        r'<span class="search-result-aya" data-sura="\1" data-verse="\2">[\1:\2]</span>',
        text,
    )


def format_ai_response(text: str) -> str:
    """Apply all AI response formatting in a single call.

    Runs :func:`render_links` and then :func:`render_aya_tags` on *text*.
    Links are processed first so that any URL that happens to contain a
    bracket-digit sequence (unlikely but possible) is already inside an
    anchor tag and will not be double-processed by the aya pattern.

    Args:
        text: Raw AI response text.

    Returns:
        Formatted HTML string with clickable links and styled aya references.

    Example::

        >>> format_ai_response("See [2:255] at https://alfanous.org")
        'See <span class="search-result-aya" data-sura="2" data-verse="255">[2:255]</span> at <a href="https://alfanous.org" target="_blank" rel="noopener noreferrer">https://alfanous.org</a>'
    """
    text = render_links(text)
    text = render_aya_tags(text)
    return text
