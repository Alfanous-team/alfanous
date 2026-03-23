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


def test_translation_highlight_stemmed_terms():
    # Test that stemmed query terms correctly highlight the original word in the text.
    # Words like "praise" and "merciful" are stemmed by the English Snowball stemmer:
    #   "praise" -> "prais"
    #   "merciful" -> "merci"
    # Without language-aware highlighting, "prais" would not match "praise" in the text.
    # Passing lang="en" makes QTranslationHighlight use the same stemming analyzer,
    # so "praise" in the text is also stemmed to "prais" and the match succeeds.
    assert QTranslationHighlight(
        u"All praise is due to Allah.",
        [u"prais"],
        "html",
        lang="en",
    ) == ('All <span class="match term0">praise</span> is due to Allah.')

    assert QTranslationHighlight(
        u"In the name of Allah, the Beneficent, the Merciful.",
        [u"merci"],
        "html",
        lang="en",
    ) == ('In the name of Allah, the Beneficent, the <span class="match term0">Merciful</span>.')

    # "say" -> "say" (unchanged); inflected forms "says" and "saying" should
    # also be highlighted because they stem to "say" via the English analyzer.
    assert QTranslationHighlight(
        u"He says that Allah is One.",
        [u"say"],
        "html",
        lang="en",
    ) == ('He <span class="match term0">says</span> that Allah is One.')

    assert QTranslationHighlight(
        u"They are saying false things.",
        [u"say"],
        "html",
        lang="en",
    ) == ('They are <span class="match term0">saying</span> false things.')
