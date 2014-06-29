# coding: utf-8


##     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

##     This program is free software: you can redistribute it and/or modify
##     it under the terms of the GNU Affero General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU Affero General Public License for more details.

##     You should have received a copy of the GNU Affero General Public License
##     along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''


@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: AGPL


'''

from alfanous.Support.whoosh.scoring import   BM25F #TF_IDF, Frequency,
from alfanous.Support.whoosh.highlight import highlight, BasicFragmentScorer, Fragment, GenshiFormatter, HtmlFormatter #NullFragmenter,FIRST,
from alfanous.TextProcessing import QHighLightAnalyzer, QDiacHighLightAnalyzer, Gword_tamdid

#from alfanous.Support.whoosh.analysis import StandardAnalyzer

#Results.extend(results)Results.upgrade(results)Results.upgrade_and_extend(results)    
def QScore( methode = None ):
    """ chooose the methode of score
        - Cosine
        - BM25F
        - TF_IDF
        - Frequency

    """
    if not methode:methode = BM25F( B = 0.75, K1 = 1.2 )#Frequency
    return methode

def QSort( sortedby ):
    """  Controls the results sorting options    """
    if sortedby == "mushaf": sortedby = "gid"
    elif sortedby == "tanzil": sortedby = ( "sura_order", "aya_id" )
    elif sortedby == "subject": sortedby = ( "chapter", "topic", "subtopic" )
    elif sortedby == "ayalength": sortedby = ( "a_l", "a_w" )
    elif sortedby == "relevance" or sortedby == "score": sortedby = None
    else: sortedby = sortedby
    return sortedby


def QFilter( results, new_results ):
    """ Filter give results with new results"""
    results.filter( new_results )
    return results

def QExtend():
    pass

def QPaginate( results, pagelen = 10 ):
    """generator of pages"""
    l = len( results )
    minimal = lambda x, y:y if x > y  else  x
    for i in range( 0, l, 10 ):
        yield ( i / pagelen, results[i:minimal( i + pagelen, l )] )


def Qhighlight( text, terms, type = "css", strip_vocalization = True ):
    """ highlight terms in text

    @param type: the type of formatting , html or css or genchi

    """
    if type == "html":
        formatter = QHtmlFormatter()
    elif type == "genshi":
        formatter = GenshiFormatter()
    elif type == "bold":
        formatter = QBoldFormatter()
    elif type == "bbcode":
        formatter = QBBcodeFormatter()
    else: #css
        formatter = HtmlFormatter( tagname = "span", classname = "match", termclass = "term", maxclasses = 8 )



    h = highlight( 
                      text,
                      terms,
                      analyzer = QHighLightAnalyzer if strip_vocalization else QDiacHighLightAnalyzer,
                      fragmenter = QFragmenter(),
                      formatter = formatter,
                      top = 3,
                      scorer = BasicFragmentScorer,
                      minscore = 1
                )

    if h:return h
    else:return text

class QFragmenter:
    """ TO DO """
    def __init__( self ):
        pass

    def __call__( self, text, tokens ):
        return [Fragment( list( tokens ) )]


class QHtmlFormatter( object ):
    """ add the style tags to the text """
    def __init__( self, change_size = True, color_cycle = ["red", "green", "orange", "blue"] ):

        self._change_size = True
        self._color_cycle = color_cycle


    def _format( self, text, color, score = 1 ):
        if self._change_size:ration = 100 + ( score - 1 ) * 0.25
        else:ration = 100

        return "<span style=\"color:" + color + ";font-size:" + str( ration ) + "%\"><b>" + Gword_tamdid( text ) + "</b></span>"



    def _format_fragment( self, text, fragment ):
        output = []
        index = fragment.startchar
        CC = self._color_cycle
        CPT = 0
        MAX = len( CC )
        for t in fragment.matches:
            if t.startchar > index:
                output.append( text[index:t.startchar] )

            ttxt = text[t.startchar:t.endchar]
            if t.matched:
                ttxt = self._format( ttxt, color = CC[CPT] )#:TO DO: SCORE score=BasicFragmentScorer(fragment)
                CPT = ( CPT + 1 ) % MAX
            output.append( ttxt )
            index = t.endchar

        output.append( text[index:fragment.endchar] )
        return "".join( output )

    def __call__( self, text, fragments ):
        return "".join( ( self._format_fragment( text, fragment )
                                  for fragment in fragments ) )
class QBBcodeFormatter( object ):
    """ format to bbcode(forums syntax) """
    def __init__( self, change_size = True, color_cycle = ["red", "green", "orange", "blue"] ):

        self._change_size = True
        self._color_cycle = color_cycle


    def _format( self, text, color, score = 1 ):
        return "[color=" + color + "]" + "[B]" + Gword_tamdid( text ) + "[/B][/color]"



    def _format_fragment( self, text, fragment ):
        output = []
        index = fragment.startchar
        CC = self._color_cycle
        CPT = 0
        MAX = len( CC )
        for t in fragment.matches:
            if t.startchar > index:
                output.append( text[index:t.startchar] )

            ttxt = text[t.startchar:t.endchar]
            if t.matched:
                ttxt = self._format( ttxt, color = CC[CPT] )#:TO DO: SCORE score=BasicFragmentScorer(fragment)
                CPT = ( CPT + 1 ) % MAX
            output.append( ttxt )
            index = t.endchar

        output.append( text[index:fragment.endchar] )
        return "".join( output )

    def __call__( self, text, fragments ):
        return "".join( ( self._format_fragment( text, fragment )
                                  for fragment in fragments ) )

class QBoldFormatter( object ):
    """ add the style tags to the text """

    def _format( self, text ):
        return "<b>" + Gword_tamdid( text ) + "</b>"



    def _format_fragment( self, text, fragment ):
        output = []
        index = fragment.startchar

        for t in fragment.matches:
            if t.startchar > index:
                output.append( text[index:t.startchar] )

            ttxt = text[t.startchar:t.endchar]
            if t.matched:
                ttxt = self._format( ttxt )
            output.append( ttxt )
            index = t.endchar

        output.append( text[index:fragment.endchar] )
        return "".join( output )

    def __call__( self, text, fragments ):
        return "".join( ( self._format_fragment( text, fragment )
                                  for fragment in fragments ) )


