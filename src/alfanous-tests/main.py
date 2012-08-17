# coding: utf-8

from alfanous.main import *

if __name__ == '__main__':
    import profile
    QSE = QuranicSearchEngine( "../alfanous/indexes/main/" )
    FQSE = FuzzyQuranicSearchEngine( "../alfanous/indexes/main/" )
    TSE = TraductionSearchEngine( "../alfanous/indexes/extend/" )
    QWSE = WordSearchEngine( "../alfanous/indexes/word/" )

    if QWSE.OK:
        print "most frequent vocalized words"
        mfw = QWSE.most_frequent_words( 10, "word" )
        for term in mfw:
            print "\t", term[1], " - frequence = ", term[0], "."
        print "most  frequent unvocalized words"
        mfw = QWSE.most_frequent_words( 10, "normalized" )
        for term in mfw:
            print "\t", term[1], " - frequence = ", term[0], "."


        res, terms = QWSE.search_all( "word_id:1", limit = 6236, sortedby = "score", reverse = True )
        print len( res )

        print "\n#list field stored values# type"
        print ",".join( [str( item ) for item in QWSE.list_values( "type" )] )

    if QSE.OK:
        print "\n#most frequent words#"

        mfw = QSE.most_frequent_words( 9999999, "uth_" )
        print len( mfw )
        f = open( "./uthmani_vocalized.csv", "w+" )
        for term in mfw:
            pass
            #print "\t", term[1], " - frequence = ", term[0], "."
            #print>>f,"\t", term[1]," ;\t",term[0],"\n"



        print "\n#list field stored values#"
        print ",".join( [str( item ) for item in QSE.list_values( "gid" )] )



    if TSE.OK:
        print "\n#extended search#",
        results = TSE.find_extended( u"gid:1 OR gid:2", defaultfield = "gid" )
        print "\n".join( [str( result ) for result in results] )

        print "\n#list all translations id#"
        print ",".join( TSE.list_values( "id" ) )



    string1 = "الصلاة+الزكاة"
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
        print "#suggestions#"
        for key, value in QSE.suggest_all( string1 ).items():
            print key, ":", ",".join( value )
        print "\n#search#"
        res, terms = QSE.search_all( string1, limit = 6236, sortedby = "score", reverse = True )


        #for key,freq in res.key_terms("aya", docs=1, numterms=15000): print key,"(",freq,"),",


        '''
        string2 = u"عاصم"
        res2,terms2  = QSE.search_all(string2, sortedby="mushaf")
        res=QFilter(res1,res2)

        terms=terms1|terms2
        '''


        print "\n#of#"
        for term in terms:
            print "%s  (%d in %d)," % term[1:],

        values = [term[1] for term in list( terms )]
        print "\n#is#"
        #print res.key_terms("aya")
        html = u"Results(time=%f,number=%d):\n" % ( res.runtime, len( res ) )
        for num, respage in QPaginate( res, 5 ):
            html += "~~~~~page " + str( num ) + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            for r in respage:
                html += "(" + str( r["aya_id"] ) + "," + str( r["sura_id"] ) + ") :" + u"<p>" + QSE.highlight( r["aya_"], values, "html" ) + u"</p>\n"
            print html
            html = ""
            raw_input( "press any key..." )






