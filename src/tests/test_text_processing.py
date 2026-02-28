
"""
This is a test module for alfanous.TextProcessing

"""

from alfanous.text_processing import QArabicSymbolsFilter

def test_arabic_symbol_filter():
    ASF = QArabicSymbolsFilter()
    assert ASF.normalize_all( u"عاصِمٌ" ) == u"عاصم"
