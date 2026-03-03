
"""
This is a test module for alfanous.TextProcessing

"""

from alfanous.text_processing import QArabicSymbolsFilter, get_arabic_stemmer

def test_arabic_symbol_filter():
    ASF = QArabicSymbolsFilter()
    assert ASF.normalize_all( u"عاصِمٌ" ) == u"عاصم"

def test_get_arabic_stemmer():
    stemmer = get_arabic_stemmer()
    assert stemmer is not None, "PyStemmer Arabic stemmer should be available"
    # Different inflected forms of the same root should yield the same stem.
    # 'كتابة' (writing) and 'كتاب' (book) both stem to 'كتاب' via Snowball Arabic.
    assert stemmer.stemWord(u'كتابة') == stemmer.stemWord(u'كتاب')
    # 'مسلمون' (Muslims, plural) and 'مسلم' (Muslim) both stem to 'مسلم'.
    assert stemmer.stemWord(u'مسلمون') == stemmer.stemWord(u'مسلم')
