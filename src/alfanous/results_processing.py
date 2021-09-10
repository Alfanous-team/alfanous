
from whoosh.scoring import BM25F
from whoosh.highlight import highlight, Fragment, \
    HtmlFormatter, ContextFragmenter, BasicFragmentScorer, WholeFragmenter
from alfanous.text_processing import QHighLightAnalyzer, QDiacHighLightAnalyzer, Gword_tamdid


def QScore():
    return BM25F(B=0.75, K1=1.2)


def QSort(sortedby):
    """  Controls the results sorting options    """
    if sortedby == "mushaf":
        return "gid"
    elif sortedby == "tanzil":
        return "sura_order", "aya_id"
    elif sortedby == "subject":
        return "chapter", "topic", "subtopic"
    elif sortedby == "ayalength":
        return "a_l", "a_w"
    elif sortedby in ["relevance", "score"]:
        return None

    return sortedby



def QFilter(results, new_results):
    """ Filter give results with new results"""
    results.filter(new_results)
    return results




def QPaginate(results, pagelen=10):
    """generator of pages"""
    l = len(results)
    minimal = lambda x, y: y if x > y else x
    for i in range(0, l, 10):
        yield i / pagelen, results[i:minimal(i + pagelen, l)]


def Qhighlight(text, terms,     type="css", strip_vocalization=True):

    if type == "bold":
        formatter = QBoldFormatter()
    else:  # css
        formatter = HtmlFormatter(tagname="span", classname="match", termclass="term", maxclasses=8)

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





class QBoldFormatter(object):
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
