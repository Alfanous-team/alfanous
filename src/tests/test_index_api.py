"""Tests for alfanous.api.index_translations()."""

import json
import os
import shutil

import pytest

alfanous_import = pytest.importorskip(
    "alfanous_import",
    reason="alfanous_import package is not installed",
)

import alfanous.api as alfanous

# Path to the translation store shipped with the repository
_STORE_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "store", "Translations"
))

# Pick two well-known zip files that are present in the store
_SAMPLE_ZIPS = [
    os.path.join(_STORE_DIR, "en.shakir.trans.zip"),
    os.path.join(_STORE_DIR, "en.transliteration.trans.zip"),
]
_STORE_EXISTS = os.path.isdir(_STORE_DIR) and all(
    os.path.exists(z) for z in _SAMPLE_ZIPS
)


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


@pytest.fixture()
def translation_source_dir(tmp_path):
    """A temporary directory pre-populated with two sample translation zips."""
    src = str(tmp_path / "translations_src")
    os.makedirs(src)
    for zip_path in _SAMPLE_ZIPS:
        shutil.copy(zip_path, src)
    return src


@pytest.mark.skipif(not _STORE_EXISTS, reason="sample translation zips not found in store/Translations/")
def test_index_translations_indexes_all_zips(temp_index_dir, temp_translations_json, translation_source_dir):
    """index_translations() indexes every .trans.zip found in the source folder."""
    count = alfanous.index_translations(
        source=translation_source_dir,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    assert count == 2
    with open(temp_translations_json, encoding="utf-8") as f:
        data = json.load(f)
    assert "en.shakir" in data
    assert "en.transliteration" in data


@pytest.mark.skipif(not _STORE_EXISTS, reason="sample translation zips not found in store/Translations/")
def test_index_translations_skips_already_indexed(temp_index_dir, temp_translations_json, translation_source_dir):
    """index_translations() returns 0 when all translations are already indexed."""
    alfanous.index_translations(
        source=translation_source_dir,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    # Second call: nothing new to index
    count = alfanous.index_translations(
        source=translation_source_dir,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    assert count == 0


@pytest.mark.skipif(not _STORE_EXISTS, reason="sample translation zips not found in store/Translations/")
def test_index_translations_removes_stale_entry_when_count_zero(temp_index_dir, temp_translations_json, translation_source_dir):
    """index_translations() must update translations.json even when no new translations are indexed (count=0)."""
    # First call: index the translations
    alfanous.index_translations(
        source=translation_source_dir,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )

    # Manually inject a stale (non-indexed) entry into translations.json
    with open(temp_translations_json, encoding="utf-8") as f:
        data = json.load(f)
    data["xx.stale"] = "Stale-Translation"
    with open(temp_translations_json, "w", encoding="utf-8") as f:
        json.dump(data, f)

    # Second call: count=0 (all already indexed), but translations.json should still be cleaned up
    count = alfanous.index_translations(
        source=translation_source_dir,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    assert count == 0

    with open(temp_translations_json, encoding="utf-8") as f:
        data = json.load(f)

    assert "xx.stale" not in data, (
        "stale entry must be removed even when count=0 (no new translations indexed)"
    )
    assert "en.shakir" in data
    assert "en.transliteration" in data


@pytest.mark.skipif(not _STORE_EXISTS, reason="sample translation zips not found in store/Translations/")
def test_index_translations_updates_translations_json(temp_index_dir, temp_translations_json, translation_source_dir):
    """index_translations() updates translations.json with all indexed IDs."""
    alfanous.index_translations(
        source=translation_source_dir,
        _index_path=temp_index_dir,
        _translations_list_file=temp_translations_json,
    )
    with open(temp_translations_json, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 2


@pytest.mark.skipif(not _STORE_EXISTS, reason="sample translation zips not found in store/Translations/")
def test_update_translations_list_does_not_preserve_non_indexed(tmp_path):
    """update_translations_list() must not carry over non-indexed entries from a previous run."""
    from alfanous_import.updater import update_translations_list

    index_dir = str(tmp_path / "extend")
    translations_json = str(tmp_path / "translations.json")

    # Pre-populate translations.json with a stale, non-indexed entry
    with open(translations_json, "w", encoding="utf-8") as f:
        json.dump({"xx.stale": "Stale-Translation"}, f)

    # Index only two real translations
    src = str(tmp_path / "src")
    os.makedirs(src)
    for zip_path in _SAMPLE_ZIPS:
        shutil.copy(zip_path, src)

    alfanous.index_translations(
        source=src,
        _index_path=index_dir,
        _translations_list_file=translations_json,
    )

    with open(translations_json, encoding="utf-8") as f:
        data = json.load(f)

    # The stale entry must not survive
    assert "xx.stale" not in data, (
        "update_translations_list must not preserve non-indexed entries"
    )
    # The newly indexed entries must be present
    assert "en.shakir" in data
    assert "en.transliteration" in data
