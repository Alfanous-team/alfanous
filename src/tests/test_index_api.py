"""Tests for the QSE nested-document architecture."""

import os

import pytest

alfanous_import = pytest.importorskip(
    "alfanous_import",
    reason="alfanous_import package is not installed",
)

from alfanous.constants import QURAN_TOTAL_VERSES

# Path to the translation store shipped with the repository
_STORE_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "store", "Translations"
))
_STORE_EXISTS = os.path.isdir(_STORE_DIR)

_RESOURCES_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "store")
) + os.sep


@pytest.fixture(scope="module")
def nested_qse_index(tmp_path_factory):
    """Build a QSE index with all available translations nested as children.

    Scoped to the module so the (slow) build only runs once.
    """
    from alfanous_import.transformer import Transformer
    index_dir = str(tmp_path_factory.mktemp("nested_main"))
    t = Transformer(index_path=index_dir, resource_path=_RESOURCES_PATH)
    schema = t.build_schema("aya")
    t.build_docindex(schema, translations_store_path=_STORE_DIR)
    return index_dir


@pytest.mark.skipif(not _STORE_EXISTS, reason="translation store not found")
def test_nested_qse_schema_has_required_fields(nested_qse_index):
    """The combined QSE schema must contain both aya-parent and translation-child fields."""
    from whoosh.filedb.filestore import FileStorage
    ix = FileStorage(nested_qse_index).open_index()
    names = ix.schema.names()
    for f in ("aya", "aya_", "gid", "sura_id", "aya_id"):
        assert f in names, f"Parent field '{f}' missing from schema"
    for f in ("kind", "trans_id", "trans_lang", "trans_text", "trans_author"):
        assert f in names, f"Child field '{f}' missing from schema"
    ix.close()


@pytest.mark.skipif(not _STORE_EXISTS, reason="translation store not found")
def test_nested_qse_parent_count(nested_qse_index):
    """Parent aya count must equal QURAN_TOTAL_VERSES."""
    from whoosh.filedb.filestore import FileStorage
    from whoosh import query as wq
    ix = FileStorage(nested_qse_index).open_index()
    with ix.searcher() as s:
        parents = s.search(wq.Term("kind", "aya"), limit=QURAN_TOTAL_VERSES + 1)
        assert len(parents) == QURAN_TOTAL_VERSES
    ix.close()


@pytest.mark.skipif(not _STORE_EXISTS, reason="translation store not found")
def test_nested_qse_nested_parent_query(nested_qse_index):
    """NestedParent: searching text_en returns parent aya documents."""
    from whoosh.filedb.filestore import FileStorage
    from whoosh import query as wq
    from whoosh.qparser import QueryParser
    ix = FileStorage(nested_qse_index).open_index()
    with ix.searcher() as s:
        q = wq.NestedParent(
            wq.Term("kind", "aya"),
            QueryParser("text_en", ix.schema).parse("merciful"),
        )
        results = s.search(q, limit=10)
        assert len(results) > 0, "NestedParent query must return at least one aya"
        for r in results:
            assert r["kind"] == "aya", "NestedParent must only return parent aya docs"
    ix.close()


@pytest.mark.skipif(not _STORE_EXISTS, reason="translation store not found")
def test_nested_qse_child_query_for_gid(nested_qse_index):
    """Querying kind:translation AND gid:1 returns exactly one child per translation."""
    from whoosh.filedb.filestore import FileStorage
    from whoosh import query as wq
    ix = FileStorage(nested_qse_index).open_index()
    with ix.searcher() as s:
        n_trans = len([f for f in os.listdir(_STORE_DIR) if f.endswith(".trans.zip")])
        q = wq.And([wq.Term("kind", "translation"), wq.Term("gid", 1)])
        results = s.search(q, limit=n_trans + 10)
        assert len(results) == n_trans, (
            f"Expected {n_trans} children for gid=1, got {len(results)}"
        )
        for r in results:
            assert r["kind"] == "translation"
            assert r["gid"] == 1
            assert r.get("trans_text"), "trans_text must be non-empty"
    ix.close()


_CORPUS_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "store", "quranic-corpus-morpology.xml"
))
_CORPUS_EXISTS = os.path.isfile(_CORPUS_PATH)


@pytest.fixture(scope="module")
def corpus_qse_index(tmp_path_factory):
    """Build a QSE index with word children from the quranic corpus.

    This fixture specifically exercises the code path that was broken by
    ``UnknownFieldError: No field named 'englishcase'`` — word entries from
    ``_load_corpus_words`` contain keys (englishcase, englishpos, englishmood,
    englishstate, special) that are absent from the aya schema.  The fix
    filters word_doc against ``_schema_names`` before calling
    ``writer.add_document``.
    """
    from alfanous_import.transformer import Transformer
    index_dir = str(tmp_path_factory.mktemp("corpus_main"))
    t = Transformer(index_path=index_dir, resource_path=_RESOURCES_PATH)
    schema = t.build_schema("aya")
    # Must NOT raise UnknownFieldError
    t.build_docindex(schema, corpus_path=_CORPUS_PATH)
    return index_dir


@pytest.mark.skipif(not _CORPUS_EXISTS, reason="quranic corpus file not found")
def test_corpus_index_builds_without_unknown_field_error(corpus_qse_index):
    """Building a QSE index with --corpus must not raise UnknownFieldError.

    Regression test for the bug where 'englishcase', 'englishpos', 'englishmood',
    'englishstate' (present in _load_corpus_words output but absent from the aya
    schema) caused an UnknownFieldError in writer.add_document.
    """
    # If we reached this point the fixture built successfully — that's the test.
    from whoosh.filedb.filestore import FileStorage
    ix = FileStorage(corpus_qse_index).open_index()
    names = ix.schema.names()
    # Word-child fields from the aya schema must be present
    for f in ("word", "word_id", "pos", "root", "lemma"):
        assert f in names, f"Word child field '{f}' missing from schema"
    # The english* fields that caused the crash must NOT be in the aya schema
    for bad in ("englishcase", "englishpos", "englishmood", "englishstate"):
        assert bad not in names, (
            f"Field '{bad}' should not be in the aya schema — "
            "it belongs only in the wordqc schema"
        )
    ix.close()


@pytest.mark.skipif(not _CORPUS_EXISTS, reason="quranic corpus file not found")
def test_corpus_index_word_children_stored(corpus_qse_index):
    """Word children written with corpus data must be retrievable from the index."""
    from whoosh.filedb.filestore import FileStorage
    from whoosh import query as wq
    ix = FileStorage(corpus_qse_index).open_index()
    with ix.searcher() as s:
        q = wq.And([wq.Term("kind", "word"), wq.Term("gid", 1)])
        results = s.search(q, limit=20)
        assert len(results) > 0, "At least one word child must be stored for gid=1"
        for r in results:
            assert r["kind"] == "word"
            assert r["gid"] == 1
            assert r.get("word"), "word field must be non-empty for word children"
    ix.close()


@pytest.mark.skipif(not _STORE_EXISTS, reason="translation store not found")
def test_nested_qse_index_size_under_limit(nested_qse_index):
    """Built index (with all translations nested) must stay under 99 MB on disk."""
    total_bytes = sum(
        os.path.getsize(os.path.join(nested_qse_index, f))
        for f in os.listdir(nested_qse_index)
        if os.path.isfile(os.path.join(nested_qse_index, f))
    )
    total_mb = total_bytes / (1024 * 1024)
    assert total_mb < _INDEX_SIZE_LIMIT_MB, (
        f"Index size {total_mb:.1f} MB exceeds the {_INDEX_SIZE_LIMIT_MB} MB limit"
    )
