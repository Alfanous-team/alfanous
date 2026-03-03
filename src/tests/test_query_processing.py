
"""
This is a test module for alfanous.QueryProcessing 

"""
from whoosh.query import Term

from alfanous import paths
from alfanous.indexing import QseDocIndex
from alfanous.query_processing import QuranicParser, ArabicParser
from alfanous.query_plugins import StemmingQuery
from alfanous.data import arabic_to_english_fields


def test_preprocess_query():
    """Test Arabic-to-Whoosh query translation: operators (و/أو/وليس/ليس) and field name
    aliases are converted by _preprocess_query before the Whoosh query parser processes them.
    """

    class _ArabicParserStub:
        ara2eng = arabic_to_english_fields
    _preprocess = ArabicParser._preprocess_query.__get__(_ArabicParserStub())

    # و → AND (the bug case: word AND field:value)
    assert _preprocess(u"أصحاب و سورة:الكهف") == u"أصحاب AND sura_arabic:الكهف"
    # أو / او → OR
    assert _preprocess(u"أصحاب أو سورة:الكهف") == u"أصحاب OR sura_arabic:الكهف"
    assert _preprocess(u"أصحاب او سورة:الكهف") == u"أصحاب OR sura_arabic:الكهف"
    # وليس → ANDNOT
    assert _preprocess(u"أصحاب وليس سورة:الكهف") == u"أصحاب ANDNOT sura_arabic:الكهف"
    # ليس → NOT (prefix)
    assert _preprocess(u"ليس سورة:الكهف") == u"NOT sura_arabic:الكهف"
    # Reversed operands (already worked before the fix)
    assert _preprocess(u"سورة:الكهف و أصحاب") == u"sura_arabic:الكهف AND أصحاب"
    # Plain words with no field
    assert _preprocess(u"الصلاة و الزكاة") == u"الصلاة AND الزكاة"
    assert _preprocess(u"سميع أو بصير") == u"سميع OR بصير"


def test_parsing_with_schema():
    D = QseDocIndex(paths.QSE_INDEX)
    QP = QuranicParser(D.get_schema(), otherfields=[])

    assert QP.parse(u"'لو كان البحر '").subqueries == [Term('aya', 'لو'), Term('aya', 'كان'), Term('aya', 'البحر')]
    assert QP.parse(u"\"عاصم\"").__dict__ == {'boost': 1.0,
 'endchar': 5,
 'fieldname': 'aya',
 'minquality': None,
 'startchar': 1,
 'text': 'عاصم'}
    assert QP.parse(u"[1 to 3]").__dict__ == {'boost': 1.0,
                                              'constantscore': True,
                                               'end': '3',
                                               'endexcl': False,
                                               'fieldname': 'aya',
                                               'start': '1',
                                               'startexcl': False}
    query = QP.parse(u"{ملك,فعل}")
    query_dict = query.__dict__.copy()
    words = query_dict.pop('words', [])
    assert query_dict == {'boost': 1.0,
                          'fieldname': 'aya',
                          'props': {'root': '\u0645\u0644\u0643', 'type': '\u0641\u0639\u0644'},
                          'text': '(\u0645\u0644\u0643,\u0641\u0639\u0644)'}
    assert sorted(words) == sorted(['\u0645\u0644\u0643\u062a\u0645',
                                    '\u0623\u0645\u0644\u0643',
                                    '\u0645\u0644\u0643\u062a',
                                    '\u064a\u0645\u0644\u0643',
                                    '\u062a\u0645\u0644\u0643\u0648\u0646',
                                    '\u062a\u0645\u0644\u0643',
                                    '\u064a\u0645\u0644\u0643\u0648\u0646',
                                    '\u062a\u0645\u0644\u0643\u0647\u0645'])
    # Test antonyms plugin - جحيم (hell) should return its antonyms
    antonym_query = QP.parse(u"#جحيم")
    assert antonym_query.boost == 1.0
    assert antonym_query.startchar == 0
    assert antonym_query.endchar == 5
    assert antonym_query.fieldname == 'aya'
    assert antonym_query.text == '\u062c\u062d\u064a\u0645'  # جحيم
    # Should return antonyms: جنة (paradise) and فردوس (paradise)
    assert sorted(antonym_query.words) == sorted(['\u062c\u0646\u0629', '\u0641\u0631\u062f\u0648\u0633'])

    assert QP.parse(u"~جحيم").__dict__ == {'boost': 1.0,
                                           'startchar': 0,
                                           'endchar': 5,
                                           'fieldname': 'aya',
                                           'text': '\u062c\u062d\u064a\u0645',
                                           'words': ['\u062c\u062d\u064a\u0645']}

    assert sorted(QP.parse(u">>سماكم").__dict__['words']) == sorted(['\u0628\u0623\u0633\u0645\u0627\u0621',
           '\u062a\u0633\u0645\u0649',
           '\u0628\u0623\u0633\u0645\u0627\u0626\u0647\u0645',
           '\u0648\u0627\u0644\u0633\u0645\u0627\u0621',
           '\u0627\u0633\u0645\u0647',
           '\u0628\u0633\u0645',
           '\u062a\u0633\u0645\u064a\u0629',
           '\u0633\u0645\u064a\u062a\u0645\u0648\u0647\u0627',
           '\u0628\u0627\u0633\u0645',
           '\u0627\u0644\u0627\u0633\u0645',
           '\u0633\u0645\u0627\u0643\u0645',
           '\u0627\u0644\u0623\u0633\u0645\u0627\u0621',
           '\u0633\u0645\u0627\u0648\u0627\u062a',
           '\u0627\u0633\u0645',
           '\u0644\u064a\u0633\u0645\u0648\u0646',
           '\u0623\u0633\u0645\u0627\u0621',
           '\u0633\u0645\u0648\u0647\u0645',
           '\u0633\u0645\u064a\u062a\u0647\u0627',
           '\u0633\u0645\u0627\u0621',
           '\u0623\u0633\u0645\u0627\u0626\u0647',
           '\u0627\u0644\u0633\u0645\u0627\u0621'])


def test_stemming_query():
    stemming = StemmingQuery('aya', u'كتب')
    assert stemming.text == u'كتب'
    assert stemming._stemmer is not None
    # The stem of the word should match itself (already a root-like form)
    assert stemming._stem == stemming._stemmer.stemWord(u'كتب')
    # Initial words list contains only the query word
    assert stemming.words == [u'كتب']


def test_stemming_plugin_parses():
    D = QseDocIndex(paths.QSE_INDEX)
    QP = QuranicParser(D.get_schema(), otherfields=[])
    # $كتب should be parsed as a StemmingQuery
    query = QP.parse(u"$كتب")
    assert isinstance(query, StemmingQuery)
    assert query.text == u'كتب'
    assert query._stemmer is not None
