"""Tests for alfanous.api.index()."""

import json
import os
import tempfile

import pytest

alfanous_import = pytest.importorskip(
    "alfanous_import",
    reason="alfanous_import package is not installed",
)

import alfanous.api as alfanous

# Path to a known translation zip shipped with the repository
_STORE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "store", "Translations"
)
_SAMPLE_ZIP = os.path.join(_STORE_DIR, "en.shakir.trans.zip")


@pytest.fixture()
def temp_index_dir(tmp_path):
    """Provide a temporary directory for a fresh extend index."""
    return str(tmp_path / "extend")


@pytest.fixture()
def temp_translations_json(tmp_path):
    """Provide a temporary translations.json file."""
    path = str(tmp_path / "translations.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f)
    return path


@pytest.mark.skipif(
    not os.path.exists(_SAMPLE_ZIP),
    reason="store/Translations/en.shakir.trans.zip not found",
)
def test_index_returns_true_for_new_translation(temp_index_dir, temp_translations_json):
    """index() returns True when a translation is newly added."""
    result = alfanous.index(
        _SAMPLE_ZIP,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    assert result is True


@pytest.mark.skipif(
    not os.path.exists(_SAMPLE_ZIP),
    reason="store/Translations/en.shakir.trans.zip not found",
)
def test_index_returns_false_when_already_indexed(temp_index_dir, temp_translations_json):
    """index() returns False when the translation is already in the index."""
    # First call indexes it
    alfanous.index(
        _SAMPLE_ZIP,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    # Second call should detect it is already present
    result = alfanous.index(
        _SAMPLE_ZIP,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    assert result is False


@pytest.mark.skipif(
    not os.path.exists(_SAMPLE_ZIP),
    reason="store/Translations/en.shakir.trans.zip not found",
)
def test_index_updates_translations_json(temp_index_dir, temp_translations_json):
    """index() updates translations.json with the newly indexed translation ID."""
    alfanous.index(
        _SAMPLE_ZIP,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    with open(temp_translations_json, encoding="utf-8") as f:
        data = json.load(f)
    assert "en.shakir" in data
