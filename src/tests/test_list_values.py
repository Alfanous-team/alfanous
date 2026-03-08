#!/usr/bin/env python3
# coding: utf-8

"""
Tests for the ``list_values`` action exposed on the ``do`` API.
"""

import pytest
from alfanous.api import do, list_values
from alfanous.outputs import Raw


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _engine_ok():
    """Return True if the QSE index is available."""
    from alfanous.outputs import Raw
    return Raw().QSE.OK


# ---------------------------------------------------------------------------
# Tests that work without the index (error-path / contract tests)
# ---------------------------------------------------------------------------

class TestListValuesContract:
    """Validate the shape of list_values responses without needing the index."""

    def test_missing_field_returns_error(self):
        """Calling list_values without a field parameter returns an error."""
        result = do({"action": "list_values"})
        assert "list_values" in result
        lv = result["list_values"]
        assert lv["field"] is None
        assert lv["values"] == []
        assert lv["count"] == 0
        assert "error" in lv

    def test_empty_field_returns_error(self):
        """Calling list_values with an empty string field returns an error."""
        result = do({"action": "list_values", "field": ""})
        assert "list_values" in result
        lv = result["list_values"]
        assert "error" in lv

    def test_response_always_has_list_values_key(self):
        """The top-level key is always 'list_values'."""
        result = do({"action": "list_values", "field": "pos"})
        assert "list_values" in result

    def test_response_always_has_error_key(self):
        """The top-level key 'error' (standard envelope) is present."""
        result = do({"action": "list_values", "field": "pos"})
        assert "error" in result

    def test_raw_list_values_no_field(self):
        """Raw._list_values returns an error dict when no field is given."""
        raw = Raw()
        result = raw._list_values({})
        assert "list_values" in result
        assert result["list_values"]["field"] is None
        assert "error" in result["list_values"]


# ---------------------------------------------------------------------------
# Tests that require the index
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _engine_ok(), reason="Requires built Whoosh index")
class TestListValuesWithIndex:

    def test_known_categorical_field_pos(self):
        """list_values for 'pos' (part-of-speech) returns a non-empty list."""
        result = list_values("pos")
        lv = result["list_values"]
        assert lv["field"] == "pos"
        assert isinstance(lv["values"], list)
        assert lv["count"] > 0
        assert lv["count"] == len(lv["values"])
        # Sanity: all values are non-empty strings
        for v in lv["values"]:
            assert isinstance(v, str) and v

    def test_known_categorical_field_gender(self):
        """list_values for 'gender' returns expected morphological categories."""
        result = list_values("gender")
        lv = result["list_values"]
        assert lv["count"] > 0
        assert lv["field"] == "gender"

    def test_known_categorical_field_number(self):
        """list_values for 'number' returns singular/plural/dual values."""
        result = list_values("number")
        lv = result["list_values"]
        assert lv["count"] > 0

    def test_values_are_sorted(self):
        """Returned values list is sorted."""
        result = list_values("pos")
        lv = result["list_values"]
        assert lv["values"] == sorted(lv["values"])

    def test_unknown_field_returns_empty_list(self):
        """Querying a non-existent field returns an empty values list (not an error)."""
        result = list_values("__nonexistent_field__")
        lv = result["list_values"]
        assert lv["field"] == "__nonexistent_field__"
        assert lv["values"] == []
        assert lv["count"] == 0
        # No 'error' key for an unknown field – the engine just returns nothing
        assert "error" not in lv

    def test_do_action_dispatches_correctly(self):
        """do({'action': 'list_values', 'field': 'gender'}) is routed correctly."""
        result = do({"action": "list_values", "field": "gender"})
        assert "list_values" in result
        assert result["list_values"]["field"] == "gender"

    def test_api_helper_matches_do(self):
        """list_values() convenience wrapper produces the same result as do()."""
        via_helper = list_values("pos")
        via_do = do({"action": "list_values", "field": "pos"})
        assert via_helper["list_values"] == via_do["list_values"]


if __name__ == "__main__":
    # Quick smoke-test
    r = do({"action": "list_values"})
    print("No field →", r)

    r = do({"action": "list_values", "field": "pos"})
    print("pos →", r["list_values"]["count"], "values")
