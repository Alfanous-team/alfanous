# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
"""
This is a test module for most of features provided by alfanous.main module.

"""

from alfanous.main import QuranicSearchEngine, FuzzyQuranicSearchEngine
from alfanous.main import TraductionSearchEngine
from alfanous.main import WordSearchEngine
from alfanous.results_processing import QPaginate
from six.moves import input
#from alfanous.ResultsProcessing import QFilter



if __name__ == '__main__':
    
    QSE = QuranicSearchEngine( "../alfanous/indexes/main/" )
    FQSE = FuzzyQuranicSearchEngine( "../alfanous/indexes/main/" )
    TSE = TraductionSearchEngine( "../alfanous/indexes/extend/" )
    QWSE = WordSearchEngine( "../alfanous/indexes/word/" )

    if QWSE.OK:
        print("most frequent vocalized words")
        MFW = QWSE.most_frequent_words( 10, "word" )
        for term in MFW:
            print("\t", term[1], " - frequence = ", term[0], ".")
        print("most  frequent unvocalized words")
        MFW = QWSE.most_frequent_words( 10, "normalized" )
        for term in MFW:
            print("\t", term[1], " - frequence = ", term[0], ".")


        RESULTS, TERMS = QWSE.search_all( "word_id:1", 
                                       limit = 6236, 
                                       sortedby = "score", 
                                       reverse = True )
        print(len( RESULTS ))

        print("\n#list field stored VALUES# type")
        print(",".join( [str( item ) for item in QWSE.list_values( "type" )] ))

    if QSE.OK:
        print("\n#most frequent words#")

        MFW = QSE.most_frequent_words( 9999999, "uth_" )
        print(len( MFW ))
        MFW_CSVFILE = open( "./uthmani_vocalized.csv", "w+" )
        for term in MFW:
            pass
            #print "\t", term[1], " - frequence = ", term[0], "."
            #print>>MFW_CSVFILE,"\t", term[1]," ;\t",term[0],"\n"



        print("\n#list field stored values#")
        print(",".join( [str( item ) for item in QSE.list_values( "gid" )] ))



    if TSE.OK:
        print("\n#extended search#", end='')
        RESULTS = TSE.find_extended( "gid:1 OR gid:2", defaultfield = "gid" )
        print("\n".join( [str( result ) for result in RESULTS] ))

        print("\n#list all translations id#")
        print(",".join( TSE.list_values( "id" ) ))



    QUERY1 = "الصلاة+الزكاة"
    # >>الأمل
    # %المأصدة
    # لله
    # ال*لك
    # رب     
    # "رسول * الله"  
    # الصلاة وليس الزكاة
    # #السعير  
    # ~السعير
    # نعمت
    #رقم_السورة:[1 الى 5] و الله 
    #آية_:'مَن '
    # {ملك,فعل}
    # >>سماكم
    #>سماكم
    #سماكم
    #سجدة:نعم
    #fawoqa
    #\" رب العالمين\"
    #جزء:8

    if QSE.OK:
        print("#suggestions#")
        for key, value in QSE.suggest_all( QUERY1 ).items():
            print(key, ":", ",".join( value ))
        print("\n#search#")
        RESULTS, TERMS = QSE.search_all( QUERY1, 
                                     limit = 6236, 
                                     sortedby = "score", 
                                     reverse = True )


        for key, freq in RESULTS.key_terms("aya", docs=1, numterms=15000): 
            print(key, "(", freq, "),", end='')



        ## test filtering results
        #QUERY2 = u"عاصم"
        #RESULTS2,TERMS2  = QSE.search_all(QUERY2, sortedby="mushaf")
        #RESULTS=QFilter(RESULTS,RESULTS2)
        #TERMS = list( set(TERMS) &  set( TERMS2))
        



        print("\n#of#")
        for term in TERMS:
            print("%s  (%d in %d)," % term[1:], end='')

        VALUES = [term[1] for term in list( TERMS )]
        print("\n#is#")
        #print RESULTS.key_terms("aya")
        HTML = "Results(time=%f,number=%d):\n" % ( 
                                                   RESULTS.runtime,
                                                   len( RESULTS ) 
                                                   )
        for num, respage in QPaginate( RESULTS, 5 ):
            HTML += "~~~~~page " + str( num ) + "~~~~~~\n"
            for r in respage:
                HTML += "(" + \
                        str( r["aya_id"] ) + "," + \
                        str( r["sura_id"] ) + ") :<p>" + \
                        QSE.highlight( r["aya_"], VALUES, "html" ) + "</p>\n"
            print(HTML)
            HTML = ""
            input("press any key...")






