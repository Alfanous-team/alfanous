



import alfanous.api


def test_search():
    # Mushaf-order search must not raise
    alfanous.api.search(u"الله", sortedby='mushaf')

    results = alfanous.api.do({"action": "search", "query": u"الله"})
    del results['search']['runtime']

    # Total occurrence count of "الله" in the Quran is an invariant.
    assert results['search']['interval'] == {
        'end': 10, 'nb_pages': 157.5, 'page': 1.0, 'start': 1, 'total': 1566
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
