"""Tests for word sub-schema configuration.

These tests validate the schema changes that do NOT require a built index:
- word_standard and lemma are KEYWORD type in fields.json
- root, lemma, and type are marked facet_allowed in fields.json
- _WORD_ALL_INDEXED_FIELDS includes word_standard and lemma
- _WORD_FACET_FIELDS contains exactly {root, type}
"""

import json
import os
import pytest

from alfanous import paths as _paths

_STORE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(_paths.__file__), "..", "..", "store")
) + os.sep
_FIELDS_JSON = _STORE_PATH + "fields.json"


@pytest.fixture(scope="module")
def fields_by_name():
    with open(_FIELDS_JSON) as f:
        fields = json.load(f)
    return {fld["name"]: fld for fld in fields if fld.get("search_name")}


def test_word_standard_is_keyword(fields_by_name):
    """word_standard must be declared as KEYWORD in fields.json."""
    assert fields_by_name["word_standard"]["type"] == "KEYWORD", (
        "word_standard should be KEYWORD so it is searchable via MultifieldParser"
    )


def test_lemma_is_keyword(fields_by_name):
    """lemma must be declared as KEYWORD in fields.json."""
    assert fields_by_name["lemma"]["type"] == "KEYWORD", (
        "lemma should be KEYWORD in fields.json"
    )


def test_root_facet_allowed(fields_by_name):
    """root must have facet_allowed=true in fields.json."""
    assert fields_by_name["root"].get("facet_allowed") is True, (
        "root should have facet_allowed=true in fields.json"
    )


def test_lemma_facet_allowed(fields_by_name):
    """lemma must have facet_allowed=true in fields.json."""
    assert fields_by_name["lemma"].get("facet_allowed") is True, (
        "lemma should have facet_allowed=true in fields.json"
    )


def test_type_facet_allowed(fields_by_name):
    """type must have facet_allowed=true in fields.json."""
    assert fields_by_name["type"].get("facet_allowed") is True, (
        "type should have facet_allowed=true in fields.json"
    )


def test_word_standard_in_word_all_indexed_fields():
    """word_standard must be in _WORD_ALL_INDEXED_FIELDS."""
    from alfanous.outputs import _WORD_ALL_INDEXED_FIELDS
    assert "word_standard" in _WORD_ALL_INDEXED_FIELDS, (
        "word_standard must be in _WORD_ALL_INDEXED_FIELDS so the word "
        "MultifieldParser includes it as a default search field"
    )


def test_lemma_in_word_all_indexed_fields():
    """lemma must be in _WORD_ALL_INDEXED_FIELDS (not just a facet field)."""
    from alfanous.outputs import _WORD_ALL_INDEXED_FIELDS
    assert "lemma" in _WORD_ALL_INDEXED_FIELDS, (
        "lemma must be in _WORD_ALL_INDEXED_FIELDS so it is searchable via "
        "the word MultifieldParser"
    )


def test_word_facet_fields_set():
    """_WORD_FACET_FIELDS must contain exactly root and type (lemma removed)."""
    from alfanous.outputs import _WORD_FACET_FIELDS
    assert _WORD_FACET_FIELDS == frozenset({"root", "type"}), (
        "_WORD_FACET_FIELDS should be frozenset({'root', 'type'}); "
        "lemma belongs in _WORD_ALL_INDEXED_FIELDS instead"
    )


def test_schema_builder_lemma_keyword():
    """Transformer.build_schema must produce a KEYWORD field for lemma."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import KEYWORD
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["lemma"], KEYWORD), (
        "Transformer.build_schema must produce KEYWORD for lemma"
    )


def test_schema_builder_word_standard_keyword():
    """Transformer.build_schema must produce a KEYWORD field for word_standard."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import KEYWORD
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["word_standard"], KEYWORD), (
        "Transformer.build_schema must produce KEYWORD for word_standard"
    )
