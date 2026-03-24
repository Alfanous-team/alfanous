



import pytest
import alfanous.api
from alfanous.data import QSE
from alfanous import paths


@pytest.fixture(autouse=True)
def _require_index():
    if not QSE(paths.QSE_INDEX).OK:
        pytest.skip("Search index not built — run `make build` first")


def test_search():
    # Mushaf-order search must not raise
    alfanous.api.search(u"الله", sortedby='mushaf')

    results = alfanous.api.do({"action": "search", "query": u"الله"})
    del results['search']['runtime']

    # Total occurrence count of "الله" in the Quran is an invariant.
    assert results['search']['interval'] == {
        'end': 10, 'nb_pages': 157, 'page': 1.0, 'start': 1, 'total': 1567
    }

    # Top-level structure
    assert results['error'] == {'code': 0, 'msg': 'success'}
    search = results['search']
    assert set(search.keys()) >= {'ayas', 'interval', 'translation_info', 'words'}
    ayas = search['ayas']
    assert len(ayas) == 10

    # Every result page item must have the expected structure and contain "الله"
    expected_keys = {'annotations', 'aya', 'identifier', 'position', 'sajda', 'stat', 'sura', 'theme'}
    for pos, item in ayas.items():
        assert set(item.keys()) >= expected_keys, f"position {pos} missing keys"
        aya = item['aya']
        assert 'الله' in aya['text_no_highlight'], f"position {pos} aya doesn't contain الله"
        ident = item['identifier']
        assert {'aya_id', 'gid', 'sura_id', 'sura_name', 'sura_arabic_name'} == set(ident.keys())
        assert isinstance(ident['gid'], int)
        assert isinstance(ident['sura_id'], int)


def test_correct_query_via_do():
    result = alfanous.api.do({"action": "correct_query", "query": "الله"})
    assert "error" in result
    assert result["error"]["code"] == 0
    assert "correct_query" in result
    cq = result["correct_query"]
    assert "original" in cq
    assert "corrected" in cq
    assert cq["original"] == "الله"
    assert isinstance(cq["corrected"], str)


def test_correct_query_function():
    result = alfanous.api.correct_query("الله")
    assert "error" in result
    assert result["error"]["code"] == 0
    assert "correct_query" in result


def test_correct_query_unsupported_unit():
    result = alfanous.api.correct_query("الله", unit="word")
    assert "error" in result
    assert result["correct_query"] is None


def test_correct_query_multiword_phrase():
    # Multi-word query with all known terms — corrected equals original
    result = alfanous.api.correct_query("الرحمن الرحيم")
    assert result["error"]["code"] == 0
    cq = result["correct_query"]
    assert cq["original"] == "الرحمن الرحيم"
    assert isinstance(cq["corrected"], str)


def test_correct_query_misspelled_phrase():
    # Misspelled multi-word query — corrector should suggest nearest known terms
    result = alfanous.api.correct_query("الرحمان الرحيم")
    assert result["error"]["code"] == 0
    cq = result["correct_query"]
    assert cq["original"] == "الرحمان الرحيم"
    assert isinstance(cq["corrected"], str)
    # Corrected must differ from original because الرحمان is misspelled
    assert cq["corrected"] != cq["original"]


def test_correct_query_quoted_phrase_no_error():
    # Quoted phrase with all valid terms — corrected equals original (quotes preserved)
    result = alfanous.api.correct_query('"الرحمن الرحيم"')
    assert result["error"]["code"] == 0
    cq = result["correct_query"]
    assert cq["original"] == '"الرحمن الرحيم"'
    assert cq["corrected"] == '"الرحمن الرحيم"'


def test_correct_query_quoted_phrase_with_error():
    # Quoted phrase with a misspelled term — corrector fixes the term inside quotes
    result = alfanous.api.correct_query('"الرحمان الرحيم"')
    assert result["error"]["code"] == 0
    cq = result["correct_query"]
    assert cq["original"] == '"الرحمان الرحيم"'
    # Corrected version should differ (الرحمان → الرحمن)
    assert cq["corrected"] != cq["original"]
    assert isinstance(cq["corrected"], str)


def test_correct_query_long_phrase():
    # Multi-word phrase including one misspelled word
    result = alfanous.api.correct_query("بسم الله الرحمان الرحيم")
    assert result["error"]["code"] == 0
    cq = result["correct_query"]
    assert cq["original"] == "بسم الله الرحمان الرحيم"
    assert cq["corrected"] != cq["original"]


def test_correct_query_long_quoted_phrase_no_error():
    # Well-formed quoted phrase — corrected equals original
    result = alfanous.api.correct_query('"بسم الله الرحمن الرحيم"')
    assert result["error"]["code"] == 0
    cq = result["correct_query"]
    assert cq["corrected"] == cq["original"]


# ---------------------------------------------------------------------------
# Nested translation / tafsir tests
# ---------------------------------------------------------------------------

def test_search_translation_unit_english():
    """unit='translation' with an English query returns English translation child docs."""
    result = alfanous.api.search("merciful", unit="translation")
    assert result["error"]["code"] == 0
    search = result["search"]
    assert search["interval"]["total"] > 0, "Expected at least one translation match for 'merciful'"
    trans = search["translations"]
    assert len(trans) > 0
    # Every returned item must carry the required fields
    for pos, item in trans.items():
        ident = item["identifier"]
        assert "gid" in ident and isinstance(ident["gid"], int)
        assert "translation_id" in ident
        assert "aya_id" in ident
        assert "sura_id" in ident
        assert "sura_name" in ident
        assert "aya" in item, "Expected 'aya' context block in translation result"
        assert "text" in item["aya"], "Expected 'text' in 'aya' context block"
        translation = item["translation"]
        assert "text" in translation
        assert "lang" in translation
        assert translation["lang"] is not None
    # The word "merciful" appears in English translations — verify at least one is English
    langs = {item["translation"]["lang"] for item in trans.values() if item["translation"]["lang"]}
    assert "en" in langs, f"Expected English translations among results, got langs: {langs}"



def test_search_aya_with_translation_param():
    """aya search with translation='en.sahih' returns translation text alongside each aya."""
    result = alfanous.api.search("الرحمن الرحيم", translation="en.sahih")
    assert result["error"]["code"] == 0
    ayas = result["search"]["ayas"]
    assert len(ayas) > 0
    # At least some results must have a non-None translation (those that have en.sahih)
    translations_found = [item["aya"]["translation"] for item in ayas.values()]
    assert any(t is not None for t in translations_found), (
        "Expected at least one aya to include en.sahih translation text"
    )
    # Any non-None translation must be a plain string, not a dict
    for t in translations_found:
        if t is not None:
            assert isinstance(t, str), f"translation must be a plain string, got {type(t)}"


def test_search_aya_with_lang_en():
    """aya search with search_lang='en' returns an English translation alongside each aya."""
    result = alfanous.api.search("الله", search_lang="en")
    assert result["error"]["code"] == 0
    ayas = result["search"]["ayas"]
    assert len(ayas) > 0
    translations_found = [item["aya"]["translation"] for item in ayas.values()]
    assert any(t is not None for t in translations_found), (
        "Expected at least one aya to include an English translation (lang=en)"
    )
    for t in translations_found:
        if t is not None:
            assert isinstance(t, str)


def test_search_aya_with_tafsir_jalalayn():
    """aya search with translation='ar.jalalayn' returns jalalayn tafsir alongside each aya."""
    result = alfanous.api.search("الصراط المستقيم", translation="ar.jalalayn")
    assert result["error"]["code"] == 0
    ayas = result["search"]["ayas"]
    assert len(ayas) > 0
    translations_found = [item["aya"]["translation"] for item in ayas.values()]
    assert any(t is not None for t in translations_found), (
        "Expected at least one aya to include ar.jalalayn tafsir text"
    )
    for t in translations_found:
        if t is not None:
            assert isinstance(t, str)


def test_search_aya_with_transliteration():
    """aya search with translation='en.transliteration' returns transliteration text."""
    result = alfanous.api.search("بسم الله", translation="en.transliteration")
    assert result["error"]["code"] == 0
    ayas = result["search"]["ayas"]
    assert len(ayas) > 0
    translations_found = [item["aya"]["translation"] for item in ayas.values()]
    assert any(t is not None for t in translations_found), (
        "Expected at least one aya to include en.transliteration text"
    )


def test_non_arabic_search_returns_ayas():
    """A non-Arabic query returns parent aya docs that contain matching translations."""
    result = alfanous.api.search("merciful")
    assert result["error"]["code"] == 0
    search = result["search"]
    assert search["interval"]["total"] > 0, "Expected aya results for non-Arabic query 'merciful'"
    ayas = search["ayas"]
    assert len(ayas) > 0
    # Results must be ayas (have the expected aya structure)
    expected_keys = {"aya", "identifier", "sajda", "stat"}
    for pos, item in ayas.items():
        assert set(item.keys()) >= expected_keys, f"position {pos} missing aya keys"
        assert isinstance(item["identifier"]["gid"], int)


def test_non_arabic_aya_search_stemming():
    """Inflected forms must match the same ayas as the base/stemmed form.

    'fires' and 'fire' must produce identical result counts because the
    translation fields are indexed and queried with the same Snowball stemmer.
    """
    result_fire  = alfanous.api.search("fire")
    result_fires = alfanous.api.search("fires")
    assert result_fire["error"]["code"] == 0
    assert result_fires["error"]["code"] == 0
    total_fire  = result_fire["search"]["interval"]["total"]
    total_fires = result_fires["search"]["interval"]["total"]
    assert total_fires > 0, "Expected results for 'fires'"
    assert total_fire == total_fires, (
        f"'fires' ({total_fires}) must return the same count as 'fire' ({total_fire})"
    )


def test_translation_unit_search_stemming():
    """Translation-unit search: inflected forms match the same translations as base form."""
    result_fire  = alfanous.api.search("fire",  unit="translation")
    result_fires = alfanous.api.search("fires", unit="translation")
    assert result_fire["error"]["code"] == 0
    assert result_fires["error"]["code"] == 0
    total_fire  = result_fire["search"]["interval"]["total"]
    total_fires = result_fires["search"]["interval"]["total"]
    assert total_fires > 0, "Expected results for 'fires' (translation unit)"
    assert total_fire == total_fires, (
        f"translation 'fires' ({total_fires}) must equal 'fire' ({total_fire})"
    )


# ---------------------------------------------------------------------------
# Highlight in translation search
# ---------------------------------------------------------------------------

def test_translation_search_default_highlight():
    """Translation search bold highlight wraps the matched term in <b> tags."""
    result = alfanous.api.search("merciful", unit="translation", highlight="bold")
    assert result["error"]["code"] == 0
    trans = result["search"]["translations"]
    assert len(trans) > 0
    # At least one item must have the query term wrapped in <b>…</b>.
    highlighted = [
        item for item in trans.values()
        if "<b>" in item["translation"]["text"]
    ]
    assert len(highlighted) > 0, (
        "Expected at least one translation result with bold-highlighted 'merciful'"
    )
    for item in highlighted:
        # The <b>-wrapped segment must be adjacent to the query term.
        assert "<b>" in item["translation"]["text"] and "</b>" in item["translation"]["text"]
        # The raw text must not contain markup.
        assert "<b>" not in item["translation"]["text_no_highlight"]


def test_translation_search_css_highlight():
    """Translation search CSS highlight wraps matched terms in <span class='match'> tags."""
    result = alfanous.api.search("merciful", unit="translation", highlight="css")
    assert result["error"]["code"] == 0
    trans = result["search"]["translations"]
    assert len(trans) > 0
    highlighted = [
        item for item in trans.values()
        if "<span" in item["translation"]["text"]
    ]
    assert len(highlighted) > 0, (
        "Expected at least one translation result with CSS-highlighted 'merciful'"
    )
    for item in highlighted:
        # The span must carry the 'match' class as produced by HtmlFormatter.
        assert 'class="match' in item["translation"]["text"], (
            "CSS highlight must include class='match' on the <span> element"
        )
        # The raw text must not contain markup.
        assert "<span" not in item["translation"]["text_no_highlight"]


def test_translation_search_no_highlight():
    """Translation search with highlight='none' returns text equal to text_no_highlight."""
    result = alfanous.api.search("merciful", unit="translation", highlight="none")
    assert result["error"]["code"] == 0
    trans = result["search"]["translations"]
    assert len(trans) > 0
    for pos, item in trans.items():
        assert item["translation"]["text"] == item["translation"]["text_no_highlight"], (
            f"position {pos}: 'none' highlight must leave text unchanged"
        )


def test_translation_search_highlight_text_no_highlight_always_plain():
    """text_no_highlight is always a plain string regardless of highlight setting."""
    for highlight_mode in ("bold", "css", "none"):
        result = alfanous.api.search("merciful", unit="translation", highlight=highlight_mode)
        assert result["error"]["code"] == 0
        for pos, item in result["search"]["translations"].items():
            raw = item["translation"]["text_no_highlight"]
            assert isinstance(raw, str), f"text_no_highlight must be a string (mode={highlight_mode})"
            assert "<b>" not in raw and "<span" not in raw, (
                f"text_no_highlight must not contain HTML markup (mode={highlight_mode})"
            )
