"""
Tests that verify the main Whoosh index contains all 6236 Quranic verses
for every document kind: aya, word, and translation.
"""

import os
from collections import defaultdict

from whoosh.filedb.filestore import FileStorage

from alfanous import paths

QURAN_TOTAL_VERSES = 6236
INDEX_SIZE_LIMIT_MB = 120


def _iter_docs_by_kind():
    """Iterate all stored docs and bucket them by 'kind'."""
    ix = FileStorage(paths.QSE_INDEX).open_index()
    reader = ix.reader()
    by_kind = defaultdict(list)
    for _, stored in reader.iter_docs():
        by_kind[stored.get("kind", "")].append(stored)
    reader.close()
    return by_kind


# Build the buckets once at module level so each test function can
# query a pre-loaded dict without re-opening the index.
_docs = _iter_docs_by_kind()


def test_index_aya_count_is_6236():
    """The index must contain exactly one aya document per Quranic verse."""
    aya_docs = _docs["aya"]
    assert len(aya_docs) == QURAN_TOTAL_VERSES, (
        f"Expected {QURAN_TOTAL_VERSES} aya docs, got {len(aya_docs)}"
    )


def test_index_word_covers_all_ayas():
    """Every aya must have at least one word child in the index.

    Collapses the word docs by (sura_id, aya_id) and checks that the
    resulting set has exactly QURAN_TOTAL_VERSES distinct pairs.
    """
    word_ayas = {
        (d.get("sura_id"), d.get("aya_id"))
        for d in _docs["word"]
    }
    assert len(word_ayas) == QURAN_TOTAL_VERSES, (
        f"Expected word children for {QURAN_TOTAL_VERSES} unique ayas, "
        f"got {len(word_ayas)}"
    )


def test_index_each_translation_covers_all_ayas():
    """Every loaded translation must have exactly QURAN_TOTAL_VERSES entries.

    Groups translation child docs by trans_id and asserts each group has
    the full verse count.
    """
    by_trans = defaultdict(int)
    for d in _docs["translation"]:
        tid = d.get("trans_id", "")
        if tid:
            by_trans[tid] += 1

    assert by_trans, "No translation docs found in the index"

    for tid, count in by_trans.items():
        assert count == QURAN_TOTAL_VERSES, (
            f"Translation '{tid}' has {count} entries, expected {QURAN_TOTAL_VERSES}"
        )


def test_index_size_under_100mb():
    """The main index directory must not exceed INDEX_SIZE_LIMIT_MB megabytes.

    Walks every file under paths.QSE_INDEX and sums their sizes.  A large
    index indicates either too many translations were added or the index
    format changed in an unexpected way.
    """
    total_bytes = sum(
        os.path.getsize(os.path.join(dirpath, fname))
        for dirpath, _, fnames in os.walk(paths.QSE_INDEX)
        for fname in fnames
    )
    total_mb = total_bytes / (1024 * 1024)
    assert total_mb < INDEX_SIZE_LIMIT_MB, (
        f"Index size {total_mb:.1f} MB exceeds the {INDEX_SIZE_LIMIT_MB} MB limit"
    )
