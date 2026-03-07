"""Tests to validate consistency of chapter/topic/subtopic fields in aya.json."""

import json
import os

_AYA_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "store", "aya.json"
)


def _load_aya_data():
    with open(_AYA_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_aya_json_total_count():
    data = _load_aya_data()
    assert len(data) == 6236


def test_chapter_topic_subtopic_no_trailing_spaces():
    """chapter, topic, and subtopic fields must not have leading/trailing whitespace."""
    data = _load_aya_data()
    violations = []
    for a in data:
        for field in ("chapter", "topic", "subtopic"):
            value = a.get(field, "")
            if value and value != value.strip():
                violations.append((a["gid"], field, repr(value)))
    assert not violations, f"Fields with leading/trailing spaces: {violations[:10]}"


def test_all_ayas_have_chapter():
    """Every aya must have a non-empty chapter field."""
    data = _load_aya_data()
    missing = [a["gid"] for a in data if not a.get("chapter")]
    assert not missing, f"{len(missing)} ayas still have empty chapter: first gids={missing[:10]}"
