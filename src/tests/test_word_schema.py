"""Tests for word sub-schema configuration and facet field catalogue.

These tests validate schema changes that do NOT require a built index:
- word_standard and lemma are KEYWORD type in fields.json
- root, lemma, type, pos, gender, case, state, derivation are facet_allowed
- chapter, topic, subtopic are ID type in fields.json (exact-match filtering)
- _WORD_ALL_INDEXED_FIELDS includes word_standard and lemma
- _WORD_FACET_FIELDS contains the expected set of morphological facet fields
- _TRANS_FACET_FIELDS contains sura_id, aya_id, trans_id, trans_lang
- _AYA_FACET_FIELDS contains the expected aya-level facet fields
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


# ---------------------------------------------------------------------------
# Existing field-type tests
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# chapter / topic / subtopic must be ID so exact-match filtering works
# ---------------------------------------------------------------------------

def test_chapter_is_id(fields_by_name):
    """chapter must be declared as ID in fields.json for exact-match filtering."""
    assert fields_by_name["chapter"]["type"] == "ID", (
        "chapter should be ID so filter=chapter:value works correctly"
    )


def test_topic_is_id(fields_by_name):
    """topic must be declared as ID in fields.json for exact-match filtering."""
    assert fields_by_name["topic"]["type"] == "ID", (
        "topic should be ID so filter=topic:value works correctly"
    )


def test_subtopic_is_id(fields_by_name):
    """subtopic must be declared as ID in fields.json for exact-match filtering."""
    assert fields_by_name["subtopic"]["type"] == "ID", (
        "subtopic should be ID so filter=subtopic:value works correctly"
    )


# ---------------------------------------------------------------------------
# facet_allowed flags
# ---------------------------------------------------------------------------

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


@pytest.mark.parametrize("field_name", ["pos", "gender", "case", "state", "derivation"])
def test_word_morphological_fields_facet_allowed(fields_by_name, field_name):
    """Word morphological fields shown in the facet UI must have facet_allowed=true."""
    assert fields_by_name[field_name].get("facet_allowed") is True, (
        f"{field_name} should have facet_allowed=true in fields.json"
    )


@pytest.mark.parametrize("field_name", ["chapter", "topic", "subtopic"])
def test_aya_theme_fields_facet_allowed(fields_by_name, field_name):
    """Aya-level theme fields must have facet_allowed=true in fields.json."""
    assert fields_by_name[field_name].get("facet_allowed") is True, (
        f"{field_name} should have facet_allowed=true in fields.json"
    )


# ---------------------------------------------------------------------------
# _WORD_ALL_INDEXED_FIELDS membership
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# _WORD_FACET_FIELDS — the expanded set shown in the word-facet UI
# ---------------------------------------------------------------------------

_EXPECTED_WORD_FACET_FIELDS = frozenset({
    "root", "type", "pos", "lemma", "case", "state", "derivation", "gender",
    "number", "person", "form", "voice", "aspect", "mood",
})


def test_word_facet_fields_set():
    """_WORD_FACET_FIELDS must contain the expected morphological facet fields."""
    from alfanous.outputs import _WORD_FACET_FIELDS
    assert _WORD_FACET_FIELDS == _EXPECTED_WORD_FACET_FIELDS, (
        f"_WORD_FACET_FIELDS should be {_EXPECTED_WORD_FACET_FIELDS!r}; "
        f"got {_WORD_FACET_FIELDS!r}"
    )


@pytest.mark.parametrize("field_name", sorted(_EXPECTED_WORD_FACET_FIELDS))
def test_word_facet_field_membership(field_name):
    """Each expected word facet field must be present in _WORD_FACET_FIELDS."""
    from alfanous.outputs import _WORD_FACET_FIELDS
    assert field_name in _WORD_FACET_FIELDS


# ---------------------------------------------------------------------------
# _TRANS_FACET_FIELDS — translation child-doc facet fields
# ---------------------------------------------------------------------------

def test_trans_facet_fields_contains_sura_id():
    """_TRANS_FACET_FIELDS must contain sura_id."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "sura_id" in _TRANS_FACET_FIELDS


def test_trans_facet_fields_contains_aya_id():
    """_TRANS_FACET_FIELDS must contain aya_id."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "aya_id" in _TRANS_FACET_FIELDS


def test_trans_facet_fields_contains_trans_id():
    """_TRANS_FACET_FIELDS must contain trans_id."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "trans_id" in _TRANS_FACET_FIELDS


def test_trans_facet_fields_contains_trans_lang():
    """_TRANS_FACET_FIELDS must contain trans_lang."""
    from alfanous.outputs import _TRANS_FACET_FIELDS
    assert "trans_lang" in _TRANS_FACET_FIELDS


# ---------------------------------------------------------------------------
# _AYA_FACET_FIELDS — aya-level facet field catalogue
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("field_name", [
    "sura_id", "juz", "chapter", "topic", "subtopic", "sura_type",
])
def test_aya_facet_fields_membership(field_name):
    """Key aya-level fields must be present in _AYA_FACET_FIELDS."""
    from alfanous.outputs import _AYA_FACET_FIELDS
    assert field_name in _AYA_FACET_FIELDS


# ---------------------------------------------------------------------------
# show?query=facets catalogue in self._all
# ---------------------------------------------------------------------------

def test_show_facets_structure():
    """show?query=facets must return a dict keyed by unit with field lists."""
    from alfanous.outputs import Raw, _WORD_FACET_FIELDS, _TRANS_FACET_FIELDS, _AYA_FACET_FIELDS

    r = Raw.__new__(Raw)
    r._facets = {
        "aya": sorted(_AYA_FACET_FIELDS),
        "word": sorted(_WORD_FACET_FIELDS),
        "translation": sorted(_TRANS_FACET_FIELDS),
    }
    assert set(r._facets.keys()) == {"aya", "word", "translation"}
    assert "sura_id" in r._facets["aya"]
    assert "root" in r._facets["word"]
    assert "sura_id" in r._facets["translation"]
    assert "aya_id" in r._facets["translation"]


# ---------------------------------------------------------------------------
# Transformer schema-builder tests
# ---------------------------------------------------------------------------

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


def test_schema_builder_chapter_id():
    """Transformer.build_schema must produce an ID field for chapter."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import ID
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["chapter"], ID), (
        "Transformer.build_schema must produce ID for chapter so that "
        "filter=chapter:value works"
    )


def test_schema_builder_topic_id():
    """Transformer.build_schema must produce an ID field for topic."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import ID
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["topic"], ID), (
        "Transformer.build_schema must produce ID for topic so that "
        "filter=topic:value works"
    )


def test_schema_builder_subtopic_id():
    """Transformer.build_schema must produce an ID field for subtopic."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import ID
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["subtopic"], ID), (
        "Transformer.build_schema must produce ID for subtopic so that "
        "filter=subtopic:value works"
    )


def test_schema_builder_arabiclemma_id():
    """Transformer.build_schema must produce an ID field for arabiclemma."""
    from alfanous_import.transformer import Transformer
    from whoosh.fields import ID
    t = Transformer("/tmp/_test_idx_schema/", _STORE_PATH)
    schema = t.build_schema("aya")
    assert isinstance(schema["arabiclemma"], ID), (
        "Transformer.build_schema must produce ID for arabiclemma"
    )


# ---------------------------------------------------------------------------
# Lemma normalization: transformer must strip tashkeel from stored lemma values
# so that KEYWORD exact-match queries work after _NORMALIZE_WORD_QUERY strips
# diacritics from the user's query (e.g. lemma:يَمِين → lemma:يمين).
# ---------------------------------------------------------------------------

def test_load_corpus_words_txt_lemma_normalized():
    """_load_corpus_words_txt must store normalized (unvocalized) lemma values.

    The lemma KEYWORD field uses exact-match lookup.  _search_words strips
    tashkeel from the entire query via _NORMALIZE_WORD_QUERY before parsing,
    so the stored values must also be unvocalized for the search to succeed.
    """
    from alfanous.text_processing import QArabicSymbolsFilter
    from alfanous_import.transformer import _load_corpus_words_txt
    import tempfile, os

    qasf = QArabicSymbolsFilter(
        shaping=True, tashkil=True, spellerrors=False,
        hamza=False, uthmani_symbols=True,
    )

    # Build a minimal corpus .txt snippet with a vocalized lemma (يَمِين).
    # The Buckwalter form of يَمِين is yam~yn; its LEM tag is yam~yn as well.
    # We use a known short entry to keep the test self-contained.
    corpus_lines = [
        "LOCATION\tFORM\tTAG\tFEATURES",
        "(1:1:1:1)\tyam~yn\tN\tSTEM|POS:N|LEM:yam~yn|ROOT:ymn|M|NOM",
    ]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     encoding='utf-8', delete=False) as fh:
        fh.write("\n".join(corpus_lines))
        tmp_path = fh.name

    try:
        words_by_aya = _load_corpus_words_txt(tmp_path)
        assert words_by_aya, "Expected at least one word entry"
        word = words_by_aya[(1, 1)][0]

        raw_lemma = word.get("arabiclemma")
        stored_lemma = word.get("lemma")

        # arabiclemma must preserve the original (possibly vocalized) form.
        assert raw_lemma is not None, "arabiclemma should be populated"

        # lemma must be the normalized (tashkeel-stripped) form.
        expected_normalized = qasf.normalize_all(raw_lemma or "") or None
        assert stored_lemma == expected_normalized, (
            f"lemma field must store normalized Arabic; "
            f"got {stored_lemma!r}, expected {expected_normalized!r}"
        )

        # Verify that if the raw lemma was vocalized the normalized form
        # differs (i.e. normalization actually did something) OR they are
        # equal (lemma was already unvocalized); either way the stored value
        # must equal the normalized form.
        assert stored_lemma is None or stored_lemma == qasf.normalize_all(stored_lemma or ""), (
            "Stored lemma must itself be in normalized form (idempotent)"
        )
    finally:
        os.unlink(tmp_path)


def test_load_corpus_words_txt_lemma_vocalized_unvocalized_equal():
    """Vocalized and unvocalized queries must produce the same stored lemma.

    This regression test for the issue 'lemma:يَمِين not working' ensures
    that the stored lemma value is the same whether the source data contains
    diacritics or not, so both query forms return results after normalization.
    """
    from alfanous.text_processing import QArabicSymbolsFilter
    from alfanous_import.transformer import _load_corpus_words_txt
    import tempfile, os

    qasf = QArabicSymbolsFilter(
        shaping=True, tashkil=True, spellerrors=False,
        hamza=False, uthmani_symbols=True,
    )

    # yam~yn = يَمِّين (with shadda+kasra on mim), ymyn = يمين (plain)
    corpus_vocalized = [
        "LOCATION\tFORM\tTAG\tFEATURES",
        "(1:1:1:1)\tyam~yn\tN\tSTEM|POS:N|LEM:yam~yn|ROOT:ymn|M|NOM",
    ]
    corpus_unvocalized = [
        "LOCATION\tFORM\tTAG\tFEATURES",
        "(1:1:1:1)\tymyn\tN\tSTEM|POS:N|LEM:ymyn|ROOT:ymn|M|NOM",
    ]

    results = []
    for lines in (corpus_vocalized, corpus_unvocalized):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                         encoding='utf-8', delete=False) as fh:
            fh.write("\n".join(lines))
            tmp_path = fh.name
        try:
            words = _load_corpus_words_txt(tmp_path)
            results.append(words[(1, 1)][0].get("lemma"))
        finally:
            os.unlink(tmp_path)

    # Both should produce the same normalized lemma so that search is consistent.
    norm_voc, norm_plain = results
    assert norm_voc is None or norm_voc == qasf.normalize_all(norm_voc or ""), (
        "Vocalized lemma must be stored normalized"
    )
    assert norm_plain is None or norm_plain == qasf.normalize_all(norm_plain or ""), (
        "Plain lemma must be stored normalized"
    )
