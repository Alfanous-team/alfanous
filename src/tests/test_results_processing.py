"""
This is a test module for alfanous.ResultsProcessing.

"""

from alfanous.results_processing import Qhighlight, QTranslationHighlight


def test_highlight():
    assert Qhighlight(
        u"الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        [u"الحمد", u"لله"],
        "html"
    ) == ('<span class="match term0">الْحَمْدُ</span> <span class="match '
          'term1">لِلَّهِ</span> رَبِّ الْعَالَمِينَ')


def test_translation_highlight():
    # Test case-insensitive matching (search term lowercase, text capitalized)
    assert QTranslationHighlight(
        u"In the name of Allah, the Beneficent, the Merciful.",
        [u"merciful"],
        "html"
    ) == ('In the name of Allah, the Beneficent, the <span class="match term0">Merciful</span>.')

    # Test punctuation handling: RegexTokenizer strips punctuation so
    # "Allah," is tokenized to "allah" matching the search term "allah"
    assert QTranslationHighlight(
        u"In the name of Allah, the Beneficent.",
        [u"allah"],
        "html"
    ) == ('In the name of <span class="match term0">Allah</span>, the Beneficent.')
