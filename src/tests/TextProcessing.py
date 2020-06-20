# coding: utf-8

"""
This is a test module for alfanous.TextProcessing

"""

from alfanous.text_processing import QArabicSymbolsFilter, unicode_


if __name__ == "__main__":
    ASF = QArabicSymbolsFilter()
    TEXT = u"عاصِمٌ"
    TEXT = ASF.normalize_all( TEXT )
    print TEXT

    WORD1 = unicode_( u"عَاصِمُ" )
    WORD2 = unicode_( u"عَاصمُ" )
    LIST_HARAKAT1 = WORD1.list_harakat()
    LIST_HARAKAT2 = WORD2.list_harakat()
    WORD3 = unicode_( u"فاعل" )
    PHRASE = unicode_( u"كانَ" )
    print WORD3.apply_harakat_list( LIST_HARAKAT1 )
    print LIST_HARAKAT1, "\n", LIST_HARAKAT2
    print unicode_.compare_harakat( LIST_HARAKAT1, LIST_HARAKAT2 )
    print WORD1.shakl_compare( WORD1, WORD2 )
    for i in PHRASE.tokenize_shakl():
        print i,
    
    WORD4 = unicode_( u"عاصم" )
    WORD5 = unicode_( u"عاصِم" )

    print WORD4 == WORD5
