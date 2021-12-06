
"""
This is a test module for alfanous.TextProcessing

"""

from alfanous.text_processing import QArabicSymbolsFilter, unicode_

def test_arabic_symbol_filter():
    ASF = QArabicSymbolsFilter()
    assert ASF.normalize_all( u"عاصِمٌ" ) == u"عاصم"


def test_partial_vocalization():
    WORD1 = unicode_( u"عَاصِمُ" )
    WORD2 = unicode_( u"عَاصمُ" )
    LIST_HARAKAT1 = WORD1.list_harakat()
    LIST_HARAKAT2 = WORD2.list_harakat()
    assert LIST_HARAKAT1 == {0: '\u064e', 2: '\u0650', 3: '\u064f'}
    assert LIST_HARAKAT2 == {0: '\u064e', 3: '\u064f'}
    WORD3 = unicode_( u"فاعل" )
    PHRASE = unicode_( u"كانَ" )
    assert WORD3.apply_harakat_list( LIST_HARAKAT1 ) == 'فَاعِلُ'

    assert unicode_.compare_harakat( LIST_HARAKAT1, LIST_HARAKAT2 )
    assert WORD1.shakl_compare( WORD1, WORD2 )
    assert PHRASE.tokenize_shakl() == ['\u0643\u0627\u0646\u064e']

    WORD4 = unicode_( u"عاصم" )
    WORD5 = unicode_( u"عاصِم" )

    assert WORD4 == WORD5
