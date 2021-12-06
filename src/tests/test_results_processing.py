
"""
This is a test module for alfanous.ResultsProcessing.

"""

from alfanous.results_processing import Qhighlight


def test_highlight():
    assert Qhighlight(
                   u"الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", 
                   [u"الحمد", u"لله"], 
                   "html" 
                   )  == ('<span class="match term0">الْحَمْدُ</span> <span class="match '
 'term1">لِلَّهِ</span> رَبِّ الْعَالَمِينَ')

