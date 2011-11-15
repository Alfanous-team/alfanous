#!/usr/bin/python
# -*- coding: UTF-8 -*- 


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


"""
@author: assem chelli
@contact: assem.ch [at] gmail.com
@license: AGPL


@todo: add  ID of requester for  better experience
@todo: multithreading server-clients


"""







import cgi,cgitb,sys,urllib,re,json
from sys import path
from os import chdir,curdir,environ

#cgitb.enable()
form = cgi.FormContentDict()



path.append("alfanous.egg/alfanous")




from alfanous.main import *
from alfanous.dynamic_ressources.arabicnames_dyn import ara2eng_names as Fields



import gettext;
gettext.bindtextdomain("alfanous", "./locale");
gettext.textdomain("alfanous");
_=gettext.gettext
n_ = gettext.ngettext





aratable = {"sura":u"السورة", "aya_id":u"الآية", "aya":u"نص الآية"}
ara = lambda key:aratable[key] if aratable.has_key(key) else key

kword = re.compile(u"[^,،]+")
keywords = lambda phrase: kword.findall(phrase)

def Gword_tamdid(aya):
    """ add a tamdid to lafdh aljalala to eliminate the double vocalization """
    return aya.replace(u"لَّه", u"لَّـه").replace(u"لَّه", u"لَّـه")

PERPAGE=10

Translations={ u'ghomshei': u'Mahdi Elahi Ghomshei-Persian', u'indonesian': u'Bahasa Indonesia-Indonesian', u'noghmani': u'Noghmani-tt', u'korkut': u'Besim Korkut-Bosnian', u'makarem': u'Ayatollah Makarem Shirazi-Persian', u'osmanov': u'M.-N.O. Osmanov-Russian', u'amroti': u'Maulana Taj Mehmood Amroti-sd', u'ozturk': u'Prof. Yasar Nuri Ozturk-Turkish', u'shakir': u'Mohammad Habib Shakir-English', u'muhiuddinkhan': u'Maulana Muhiuddin Khan-bn', u'arberry': u'Arthur John Arberry-English', u'irfan_ul_quran': u'Maulana Doctor Tahir ul Qadri-ur', u'jalandhry': u'Jalandhry-ur', u'porokhova': u'V. Porokhova-Russian', u'kuliev': u'E. Kuliev-Russian', u'transliteration-en': u'Transliteration-English', u'pickthall': u'Mohammed Marmaduke William Pickthall-English', u'ansarian': u'Hussain Ansarian-Persian'}


Recitations={
 u'Mishary Rashid Alafasy': u'http://www.versebyversequran.com/data/Alafasy_128kbps',
 u'Ahmed_ibn_Ali_al-Ajamy (From QuranExplorer.com)': u'http://www.versebyversequran.com/data/Ahmed_ibn_Ali_al-Ajamy_64kbps_QuranExplorer.Com',
 u'Abdullah Basfar': u'http://www.everyayah.com/data/Abdullah_Basfar_192kbps',
 u'Menshawi (external source)': u'http://www.everyayah.com/data/Menshawi_32kbps',
 u'AbdulBasit AbdusSamad (Murattal style)': u'http://www.versebyversequran.com/data/Abdul_Basit_Murattal_192kbps',
 u'AbdulBasit AbdusSamad (From QuranExplorer.com)': u'http://www.versebyversequran.com/data/AbdulSamad_64kbps_QuranExplorer.Com',
 u'Hani Rifai': u'http://www.everyayah.com/data/Hani_Rifai_192kbps',
 u'Muhammad Ayyoub': u'http://www.everyayah.com/data/Muhammad_Ayyoub_128kbps',
 u'Husary': u'http://www.everyayah.com/data/Husary_128kbps',
 u'Hudhaify': u'http://www.everyayah.com/data/Hudhaify_128kbps',
 u'Abu Bakr Ash-Shaatree': u'http://www.versebyversequran.com/data/Abu Bakr Ash-Shaatree_128kbps',
 u'Ibrahim_Walk': u'http://www.everyayah.com/data/English/Ibrahim_Walk_192kbps_TEST',
 u'Husary Mujawwad': u'http://www.everyayah.com/data/Husary_128kbps_Mujawwad',
 u'Saood bin Ibraaheem Ash-Shuraym': u'http://www.everyayah.com/data/Saood bin Ibraaheem Ash-Shuraym_128kbps',
 u'Saad Al Ghamadi': u'http://www.everyayah.com/data/Ghamadi_40kbps',
 u'Muhammad Ayyoub (external source)': u'http://www.everyayah.com/data/Muhammad_Ayyoub_32kbps'}

	





def suggest(query):
	""" return suggestions """
	try:
		text=json.dumps(QSE.suggest_all(unicode(query.replace("\\",""), 'utf8')).items())
	except Exception:
		 text ="null"
	return text	


def results(query, sortedby="score", fields=["sura", "aya_id", "aya"],page=1,highlight="css",recitation="Mishary Rashid Alafasy",translation="None"):
    """
	return the results as json
	@param fields : fields enabled to be shown
	@return : the results with the type specified
    """
    res, termz = QSE.search_all(unicode(query.replace("\\",""), 'utf8') ,limit=1000, sortedby=sortedby)
    terms = [term[1] for term in list(termz)]
    #pagination
    page=int(page)
    startpage =(page-1)*PERPAGE
    endpage=(page)*PERPAGE
    end=endpage if endpage<len(res) else len(res)
    start=startpage if startpage<len(res) else -1
    reslist=[] if end==0 or start==-1 else list(res)[start:end]
	
    
    output={}
    
    if True:
        H=lambda X:QSE.highlight(X, terms,highlight) if highlight!="none" and X else X if X else u"-----"
        N=lambda X:X if X else 0
        output["runtime"]="%2.5f" % res.runtime
        output["suggestions"]= QSE.suggest_all(unicode(query.replace("\\",""), 'utf8')).items()
        #print terms
        words_output={}
        matches=0
        docs=0
        cpt=1;
        for term in termz :
            if term[0]=="aya":
                
                if term[2]:                
                    matches+=term[2]
                    docs+=term[3]
                    words_output[str(cpt)]={"word":term[1],"nb_matches":term[2],"nb_ayas":term[3]}
                    cpt+=1
                
        words_output["global"]={"nb_words":cpt-1,"nb_matches":matches}
        output["words"]=words_output;
         
        #translations
        trad_query=u"( 0"
        for r in reslist :
                trad_query+=" OR gid:"+unicode(r["gid"])+u" "
        trad_query+=" )"+u" AND id:"+unicode(translation)
        trad_res=TSE.find_extended(trad_query, "gid")
        trad_text={}
        for tr in trad_res:
             trad_text[tr["gid"]]=tr["text"]
        
        
        output["interval"]={"start":start+1,"end":end,"total":len(res)}
        cpt = startpage
        output["ayas"]={}
        for r in reslist :
            cpt += 1
            output["ayas"][str(cpt)]={ 
            		
                      "aya":{
                      		"id":r["aya_id"],
                      		"text": Gword_tamdid(H(r["aya_"]) ),
      				"text_uthmani": Gword_tamdid(H(r["uth_"]) ),
                        	"traduction": trad_text[r["gid"]] if (translation!="None" and translation) else None,
                        	"recitation":Recitations[recitation].encode("utf-8")+ "/" + "%03d%03d.mp3" % (r["sura_id"],r["aya_id"]),
                        	#precedent aya
                        	#next aya
                      
                      },
                                            
                      
                      
            		"sura":{      
            		"name":H(keywords(r["sura"])[0]),
		    		"id":r["sura_id"],
		    		"type":H(r["sura_type"]),
		    		"order":r["sura_order"],
                    "stat":{
                            "ayas":r["s_a"],
        		    		"words":N(r["s_w"]),
        		    		"godnames":N(r["s_g"]),
        		    		"letters":N(r["s_l"])
                            }      		
            		
            		},
            		
            		
            		
                        
                        "position":
                        {
                        	"manzil":r["manzil"],
                        	"hizb":r["hizb"],
                        	"rubu":r["rub"]%4,
                        	"page":r["page"]
                   	},
                   	
                   	"theme":{
			    		"chapter":H(r["chapter"]),
			    		"topic":H(r["topic"]),
			   		 "subtopic":H(r["subtopic"])  
			 	   },
			    
			"stat":{
					"words":N(r["a_w"]),
            				"letters":N(r["a_l"]),
            				"godnames":N(r["a_g"])
			}       ,
			
			"sajda": {
            				"exist":(r["sajda"]==u"نعم"),
            				"type":H(r["sajda_type"]) if (r["sajda"]==u"نعم") else None,
            				"id":N(r["sajda_id"]) if (r["sajda"]==u"نعم") else None,
            			}
            		}
           
           
        return json.dumps(output)


	
	
#
def about():
	return json.dumps(
			{
			"engine":"Alfanous",
			"version": "0.1",
			"author": "Assem chelli", 
			"contact": "assem.ch@gmail.com"	,
			"wiki"	: "http://wiki.alfanous.org/doku.php?id=json_web_service",	
            "visits4search":visits4search()	
						
			}
            )

def salam():
    print unicode(json.dumps([u"سلام"].decode("utf-8") ));
			
			
def visits4search():
    f=open("visits.cpt","r+")
    cpt=int(f.readline())
    cpt+=1
    f=open("visits.cpt","w+")
    f.write(str(cpt))
    return cpt



    







QSE = QuranicSearchEngine("./indexes/main/")   
TSE=TraductionSearchEngine("./indexes/extend/")
	



if form.has_key("suggest"):
    print "Content-Type: application/json; charset=utf-8" 
    #Allow cross domain XHR
    print 'Access-Control-Allow-Origin: *'
    print 'Access-Control-Allow-Methods: GET'
    print 

    print suggest(form["suggest"][0])	

elif  form.has_key("search") :
    print "Content-Type: application/json; charset=utf-8" 
    #Allow cross domain XHR
    print 'Access-Control-Allow-Origin: *'
    print 'Access-Control-Allow-Methods: GET'
    print 

    visits4search()
    
    if form.has_key("sortedby"):
        sortedby = form["sortedby"][0]
    else: sortedby = "score"
    if form.has_key("page"):
        page = form["page"][0]
    else: page = 1
    if form.has_key("recitation"):
        recitation = form["recitation"][0]
    else: 
        recitation = "Mishary Rashid Alafasy"
    if form.has_key("highlight"):
        highlight = form["highlight"][0]
    else: highlight = "css"
    if form.has_key("translation"):
        translation = form["translation"][0]
    else: translation = "None"

    print results(form["search"][0], sortedby=sortedby, highlight=highlight, recitation=recitation,page=page,translation=translation)

elif form.has_key("list"):
    print "Content-Type: application/json; charset=utf-8" 
    #Allow cross domain XHR
    print 'Access-Control-Allow-Origin: *'
    print 'Access-Control-Allow-Methods: GET'
    print 

    if form["list"][0]=="translations":
        print json.dumps(Translations)
    elif form["list"][0]=="recitations":
        print json.dumps(Recitations)
    elif form["list"][0]=="information":
        print about()
    elif form["list"][0]=="fields":
        print json.dumps(Fields)
    else:
        print "choose <b>list=translations | recitations | information | fields</b>"
	

else:
    print "Content-Type: text/html; charset=utf-8\n\n" 
    print 
        
    print """
    This is the <a href='http://json.org/'>JSON</a> output system of <a href="http://wiki.alfanous.org">Alfanous</a> project .This feature is in Alpha test and the Json schema may be it's not stable . We are waiting for real feadbacks and suggestions to improve its efficacity,quality and stability. To contact the author ,please send a direct email to <b> assem.ch[at]gmail.com</b> or to the mailing list <b>alfanous [at] googlegroups.com</b>
    <br/><br/> For more details  visit the page of this service <a href="http://wiki.alfanous.org/doku.php?id=json_web_service">here</a>
    """



##tests
a=suggest("الحم")
print results("الحمد")


                                    

