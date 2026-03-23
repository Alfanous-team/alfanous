from math import log as _log

from whoosh.scoring import BM25F, BM25FScorer, WeightScorer
from whoosh.highlight import highlight, HtmlFormatter, BasicFragmentScorer, WholeFragmenter
from alfanous.text_processing import QHighLightAnalyzer, QDiacHighLightAnalyzer, Gword_tamdid, TranslationHighLightAnalyzer, make_translation_analyzer
from alfanous.constants import QURAN_TOTAL_VERSES


class QAyaWeighting(BM25F):
    """BM25F variant that anchors IDF and avgfl to the parent-aya corpus.

    With Whoosh nested documents each Quranic verse is stored as one parent
    aya doc plus N translation child docs.  Standard BM25F computes IDF and
    average field length over ``doc_count_all()``, which inflates from 6 236
    to ~106 000 once translations are indexed.  This changes every Arabic
    term's IDF and the length-normalisation denominator, producing different
    relevance rankings than the pre-nested index.

    This subclass fixes both statistics to ``QURAN_TOTAL_VERSES`` (the fixed
    parent count) so that scores are stable and independent of how many child
    translation documents exist.
    """

    def idf(self, searcher, fieldname, text):
        parent = searcher.get_parent()
        n = parent.doc_frequency(fieldname, text)
        N = QURAN_TOTAL_VERSES or 1
        return _log(N / (n + 1)) + 1

    def scorer(self, searcher, fieldname, text, qf=1):
        if not searcher.schema[fieldname].scorable:
            return WeightScorer.for_(searcher, fieldname, text)
        B = self._field_B.get(fieldname, self.B)
        sc = BM25FScorer(searcher, fieldname, text, B, self.K1, qf=qf)
        # Overwrite the cached statistics that BM25FScorer pulls from the
        # parent searcher so that child translation docs don't pollute them.
        parent = searcher.get_parent()
        n = parent.doc_frequency(fieldname, text)
        N = QURAN_TOTAL_VERSES or 1
        sc.idf = _log(N / (n + 1)) + 1
        sc.avgfl = (parent.field_length(fieldname) / N) or 1
        return sc


def QScore():
    return QAyaWeighting(B=0.75, K1=1.2)


def QSort(sortedby):
    """  Controls the results sorting options    """
    if sortedby == "mushaf":
        return "gid"
    elif sortedby == "tanzil":
        return "sura_order", "aya_id"
    elif sortedby == "ayalength":
        return "a_l", "a_w"
    elif sortedby in ["relevance", "score"]:
        return None

    return sortedby


def Qhighlight(text, terms, type="css", strip_vocalization=True):
    formatter = _BOLD_FORMATTER if type == "bold" else HtmlFormatter(**_HTML_FORMATTER_KWARGS)

    highlighted = highlight(
        text,
        terms,
        analyzer=QHighLightAnalyzer if strip_vocalization else QDiacHighLightAnalyzer,
        fragmenter=WholeFragmenter,
        formatter=formatter,
        top=3,
        scorer=BasicFragmentScorer,
        minscore=1
    )

    return highlighted or text


def QTranslationHighlight(text, terms, type="css", lang=None, **kwargs):
    analyzer = make_translation_analyzer(lang) if lang else TranslationHighLightAnalyzer
    formatter = _BOLD_FORMATTER if type == "bold" else HtmlFormatter(**_HTML_FORMATTER_KWARGS)

    highlighted = highlight(
        text,
        terms,
        analyzer=analyzer,
        fragmenter=WholeFragmenter,
        formatter=formatter,
        top=3,
        scorer=BasicFragmentScorer,
        minscore=1
    )

    return highlighted or text


class QBoldFormatter:
    """ add the style tags to the text """

    def _format(self, text):
        return "<b>" + Gword_tamdid(text) + "</b>"

    def _format_fragment(self, text, fragment):
        output = []
        index = fragment.startchar

        for t in fragment.matches:
            if t.startchar > index:
                output.append(text[index:t.startchar])

            ttxt = text[t.startchar:t.endchar]
            if t.matched:
                ttxt = self._format(ttxt)
            output.append(ttxt)
            index = t.endchar

        output.append(text[index:fragment.endchar])
        return "".join(output)

    def __call__(self, text, fragments):
        return "".join((self._format_fragment(text, fragment)
                        for fragment in fragments))


# ---------------------------------------------------------------------------
# Module-level formatter singletons.
# QBoldFormatter is stateless so it is safe to share across calls.
# HtmlFormatter maintains a ``seen`` dict that maps terms to CSS class numbers
# (term0, term1, …); sharing it across calls causes indices to accumulate
# across searches, shifting term0→term1 etc.  A fresh instance is therefore
# created on every highlight call (see Qhighlight / QTranslationHighlight).
# ---------------------------------------------------------------------------
_BOLD_FORMATTER = QBoldFormatter()
_HTML_FORMATTER_KWARGS = dict(tagname="span", classname="match", termclass="term", maxclasses=8)
