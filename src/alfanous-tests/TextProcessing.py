# coding: utf-8

from alfanous.TextProcessing import *


if __name__ == "__main__":
    ASF = QArabicSymbolsFilter()
    text = u"عاصِمٌ"
    text = ASF.normalize_all( text )
    print text

    word1 = unicode_( u"عَاصِمُ" )
    word2 = unicode_( u"عَاصمُ" )
    l1 = word1.list_harakat()
    l2 = word2.list_harakat()
    word3 = unicode_( u"فاعل" )
    phrase = unicode_( u"كانَ" )
    print word3.apply_harakat_list( l1 )
    print l1, "\n", l2, "\n", unicode_.compare_harakat( l1, l2 )
    print word1.shakl_compare( word1, word2 )
    for i in phrase.tokenize_shakl():
        print i,
    t = unicode_( u"عاصم" )
    u = unicode_( u"عاصِم" )

    print t == u
