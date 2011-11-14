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
a middle code to use alfanous from interfaces ,


@author: assem
@contact: assem.ch [at] gmail.com
@license: AGPL


@todo: visitors counter
@todo: multithreading server-clients

@deprecated: not clean code , use alfanous-json instead

"""

import sys 
from sys import path
from os import chdir,curdir,environ

import urllib
import re


from alfanous.main import *


import gettext;
gettext.bindtextdomain("alfanous", "./locale");
gettext.textdomain("alfanous");
_=gettext.gettext
n_ = gettext.ngettext



QSE = QuranicSearchEngine("./indexes/main/")
TSE=TraductionSearchEngine("./indexes/extend/")

aratable = {"sura":u"السورة", "aya_id":u"الآية", "aya":u"نص الآية"}
ara = lambda key:aratable[key] if aratable.has_key(key) else key

kword = re.compile(u"[^,،]+")
keywords = lambda phrase: kword.findall(phrase)

def Gword_tamdid(aya):
    """ add a tamdid to lafdh aljalala to eliminate the double vocalization """
    return aya.replace(u"لَّه", u"لَّـه").replace(u"لَّه", u"لَّـه")

PERPAGE=10
Traductions={ u'ghomshei': u'Mahdi Elahi Ghomshei-Persian', u'indonesian': u'Bahasa Indonesia-Indonesian', u'noghmani': u'Noghmani-tt', u'korkut': u'Besim Korkut-Bosnian', u'makarem': u'Ayatollah Makarem Shirazi-Persian', u'osmanov': u'M.-N.O. Osmanov-Russian', u'amroti': u'Maulana Taj Mehmood Amroti-sd', u'ozturk': u'Prof. Yasar Nuri Ozturk-Turkish', u'shakir': u'Mohammad Habib Shakir-English', u'muhiuddinkhan': u'Maulana Muhiuddin Khan-bn', u'arberry': u'Arthur John Arberry-English', u'irfan_ul_quran': u'Maulana Doctor Tahir ul Qadri-ur', u'jalandhry': u'Jalandhry-ur', u'porokhova': u'V. Porokhova-Russian', u'kuliev': u'E. Kuliev-Russian', u'transliteration-en': u'Transliteration-English', u'pickthall': u'Mohammed Marmaduke William Pickthall-English', u'ansarian': u'Hussain Ansarian-Persian'}
tradlista=map(lambda item:'<option value="'+item[0]+'"><?= _("'+item[1]+'")?></option>' ,Traductions.items())


Folder={u'Mishary Rashid Alafasy': u'http://www.versebyversequran.com/data/Alafasy_128kbps',
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

	
def recitations(type="site"):
	""" return a list of recitations """
	A = ayaByaya()
	list = A.list_it("name")
	
	if type == "site":
		text = "\n".join(["<option value=\"" + item + "\"><?=_(\"" + item + "\")></option>" for item in list])
	else:
		text = "\r\n".join(list)
	return text.encode('utf-8')	

def translations(type="site"):
	""" return the list of available translations """
	pass


def flashplayer(link, number,width="150"):
	    """ the code of a flash player 
	    @param link: the link of soundfile
	    @param number: the number of the current flash player
	    
	    
	    """
	    html = "\n<span align=\"left\">"
	    html += "<object  type=\"application/x-shockwave-flash\" data=\"files/player.swf\" id=\"audioplayer" + str(number) + "\" height=\"24\" width=\"%s\">" % width
	    html += "<param name=\"movie\" value=\"files/player.swf\">"
	    html += "<param name=\"FlashVars\" value=\"playerID=audioplayer" + str(number) + "&soundFile=" + link + "\">"
	    html += "<param name=\"quality\" value=\"high\">"
	    html += "<param name=\"menu\" value=\"false\">"
	    html += "<param name=\"wmode\" value=\"transparent\">"
	    html += "</object></span>" 
	    return html
	



def suggest_text(query):
	""" return lines of suggestions
	@param type:the type of results: html or text 
	"""
	try:
		text = ""
		for key, value in QSE.suggest_all(unicode(query.replace("\\",""), 'utf8')).items():
			if type == "html":
				text += "<b>" + key + "</b>" + ":" + ",".join(value) + "<br>"
			elif type =="gui":
				text += "<b>" + key + "</b>" + ":" + ",".join(value) + "<br>"
			else:
				text += key + ":" + "،".join(value) + "#\r\n"
			
			
	except Exception:
		 text =""
		
	return text	
    
def suggest_html(query):
        """ return lines of suggestions
        """

        items=QSE.suggest_all(unicode(query.replace("\\",""), 'utf8')).items()
        text=u""
        if len(items):
                text=u"<p align=\"right\" %s style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; color:#ff0000;\"><h2><b>%s (%d)</b></h2></span></p>" %(_(u"dir='rtl'"),_(u"الإقتراحات"),len(items))
                for key, value in items:
                        text +=u"<p align=\"right\" dir='rtl' style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#246b14;\">%s</span><span style=\" font-weight:600; color:#246f0d;\">:</span><span style=\" color:#000000;\">%s.</span></p>" % (key,u"،".join(value))
               

            
        return text

def results(query, type="text", sortedby="score", fields=["sura", "aya_id", "aya"], recitation="Mishary Rashid Alafasy",page=1,highlight=True,traduction="None"):
    """
	return the results as text or html
	@param type:the type of results: html or text or gui or bot or sitenew
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
	
    if type == "site":
        html = ""
        """
        <!--tableresults-->
<h2><span><?= _("النتائج")?></span>&nbsp;</h2>
<br>

<center>
<table id="searchResult">
	<thead id="tableHead">
		<tr class="headerZ">
			<th><?= _("الرقم")?></th>
			<th><?= _("السورة")?></th>
			<th><?= _("الآية")?></th>
			<th> <span class="sortby"><?= _("نص الآية")?>
			(
<a href=<?php echo '"?query='.$query.'&recitation='.$recit.'&sortedby=score"'?> title=<?= _("ترتيب حسب نسبة التشابه مع جملة الاستعلام")?>>
<?= _("نسبة التشابه")?> </a>
,<a href=<?php echo '"?query='.$query.'&recitation='.$recit.'&sortedby=mushaf"'?> title=<?= _("ترتيب حسب المصحف")?>>
<?= _("المصحف")?></a>, 
<a href=<?php echo '"?query='.$query.'&recitation='.$recit.'&sortedby=tanzil"'?> title=<?= _("ترتيب حسب زمن التنزيل")?>>
<?= _("التنزيل")?></a>
) </span></th>
	<th><?= _("ترجمة")?></th>
	<th><?= _("تفسير")?></th>
	<th><?= _("تلاوة")?></th>
		</tr>
	</thead>
<div id="test" name="test" >
	<tbody id="results" name="results">
	
	</tbody>
</div>

</table>
"""
        cpt = startpage
        for r in reslist :
			cpt += 1
			html += "<tr><td class=\"vertTh\">" + str(cpt) + "\t</td>"
			for key in fields:
				if key in r.keys():
					val = r[key]	
					if val :
						html += "\n\t<td class=\"vertTh\">" + "\t"
						if key in ["aya_", "aya", "uth", "uth_"]:
							html += Gword_tamdid(QSE.highlight(r["aya_"], terms) if highlight else r["aya_"] )
						else:
							html += keywords(unicode(val))[0]
						html += "</td>"
								
					else: html += "#######"
			html += "\n\t<td class=\"vertTh\"></td>" #translation
			html += "\n\t<td class=\"vertTh\"></td>" #tafssir
			recit = Folder[recitation]+ "/" + "%03d%03d.mp3" % (r["sura_id"],r["aya_id"])
			html += "\n\t<td class=\"vertTh\">" + flashplayer(recit, cpt) + "</td>" #recitation
			html += "\n</tr>\r\n"
        html +='<span class="stat">\n'
        html += u'<b>runtime</b> : %2.5f,' % res.runtime
        html +=u'<b>number</b> : %d<br>' % len(res)
        html +='</span>'

        return html.encode('utf8')
    elif type == "gui":
		html = "<table dir=\"rtl\" align=\"right\"><tr><th>الرقم</th><th>اسم السورة</th><th>رقم الآية</th><th>نص الآية</th></tr>"
		cpt = startpage
		for r in reslist :
			cpt += 1
			html += "<tr><td class=\"vertTh\">" + str(cpt) + "\t</td>"
			for key in fields:
				if key in r.keys():
					val = r[key]	
					if val :
						html += "\n\t<td class=\"vertTh\">" + "\t"
						if key in ["aya_", "aya", "uth", "uth_"]:
							html += Gword_tamdid(QSE.highlight(r["aya_"], terms) if highlight else r["aya_"] )
						else:
							html += keywords(unicode(val))[0]
						html += "</td>"
								
					else: html += "#######"
			html += "\n\t<td class=\"vertTh\"></td>" #translation
			html += "\n\t<td class=\"vertTh\"></td>" #tafssir
			html += "\n</tr>\r\n"
		html+="</table>"

		return {"results":html,"time":res.runtime,"resnum":len(res)}
	
    elif type == "bot":
        html = u"<br>runtime : %2.5f, " % res.runtime   
        html += u"number : %d<br> " % len(res)
        cpt = 0 
        for r in list(res)[:PERPAGE]:
			cpt += 1
			html += "<br>"
			html += u"النتيجة رقم <b>" + str(cpt) + "</b> - "
			html += u"الآية ( " + keywords(r["sura"])[0] + ":"
			html += u"" + str(r["aya_id"]) + ")<br>"
			html += " {{ "
			html += QSE.highlight(Gword_tamdid(r["aya_"]), terms) if highlight else r["aya_"]
			html += " }} "
			html += u"ـ<br>\r\n"
        return html.encode('utf8')
    
    elif type=="newbot":
        H=lambda X:QSE.highlight(X, terms,"bold") if highlight and X else X if X else u"-----"
        N=lambda X:X if X else 0
        html=u'<br>\n<b>%s</b> : %2.5f' % (_(u"الزمن المستغرق"),res.runtime)
        #print terms
        wordshtml=u""
        matches=0
        docs=0
        cpt=1;
        for term in termz :
            if term[0]=="aya":
                
                if term[2]:                
                    matches+=term[2]
                    docs+=term[3]
                    wordshtml+=u'<br>\n%d. %s : %s %d %s %s %d %s' %  (cpt,term[1],_(u"وردت"),term[2],n_(u"مرة",u"مرة",term[2]),_(u"في"),term[3],n_(u"آية",u"آية",term[3]))
                    cpt+=1

                wordshtml+u"<br>\n"
        if cpt-1:
            html+=u'<br>\n\n<b>%s</b> ( %d %s %s %d %s  ) : ' %  (_(u"الكلمات"),cpt-1,n_(u"كلمة",u"كلمة",cpt-1),_(u"وردت"),matches,n_(u"مرة",u"مرة",matches))
            html+= wordshtml   
            html+=u"<br>\n"
         
        #traductions
            trad_query=u"( 0"
            for r in reslist :
                trad_query+=" OR gid:"+unicode(r["gid"])+u" "
            trad_query+=" )"+u" AND id:"+unicode(traduction)
            trad_res=TSE.find_extended(trad_query, "gid")
            trad_text={}
            for tr in trad_res:
                trad_text[tr["gid"]]=tr["text"]
        
        if reslist:
            html+="<br>\n\n<b>%s</b> (%d %s %d %s %d)" % (_(u"النتائج"),start+1,_(u"إلى"),end,_(u"من أصل"),len(res))

        cpt = startpage
        for r in reslist :
            cpt += 1

            html += u"<br>\n<br>\n%s <b>%d</b> - %s <b>%d</b> %s <b>%s</b> "  % (_(u"النتيجة رقم"),cpt,_(u"الآية رقم"),r["aya_id"],_(u"من سورة"),H(keywords(r["sura"])[0]))
            #html+= u"<br>\n(%s:<b>%d</b>،%s :<b>%s</b>،%s :<b>%d</b>، %s : <b>%d</b>، %s  :<b>%d</b>، %s :<b>%d</b>، %s :<b>%d</b>، %s :<b>%d</b>)" %(_(u"الرقم"),r["sura_id"],_(u"مكان النزول"),H(r["sura_type"]),_(u"ترتيب النزول"),r["sura_order"],_(u"الآيات"),r["s_a"],_(u"الكلمات"),N(r["s_w"]),_(u"ألفاظ الجلالة"),N(r["s_g"]),_(u"الأحرف"),N(r["s_l"]),_(u"الركوعات"),N(r["s_r"]))
         
            html += u"<br>\n{ <b>%s</b> }" % Gword_tamdid(H(r["aya_"]) )
            
            #if traduction!="None" and traduction: html += u'<br>\n%s' % (trad_text[r["gid"]])
            #html += u"<br>\n%s:<b>%d</b> -(%s : <b>%d</b> ، %s : <b>%d</b>) - %s :<b>%d</b> -  %s :<b>%s</b>" % (_(u"المنزل"),r["manzil"],_(u"الحزب"),r["hizb"],_(u"الربع"),r["rub"]%4,_(u"الركوع"),r["ruku"],_(u"الصفحة"),r["page"])       
            #html += u"<br>\n%s : <b>%s</b> %s : <b>%s</b> %s : <b>%s</b>" % (_(u"الفصل"),H(r["chapter"]),_(u"الفرع"),H(r["topic"]),_(u"الباب"),H(r["subtopic"]))        
            #html += u"<br> \n%s : <b>%d</b> - %s :  <b>%d</b> - %s :  <b>%d</b>  " % (_(u"عدد الكلمات"),N(r["a_w"]),_(u"عدد الأحرف"),N(r["a_l"]),_(u"عدد ألفاظ الجلالة"),N(r["a_g"]))
            if r["sajda"]==u"نعم": html+=u'<br> \n%s  %s،%s %d' % (_(u"dir='rtl'"),_(u"هذه الآية تحتوي على سجدة"),H(r["sajda_type"]),_(u"رقمها"),N(r["sajda_id"]))

        return html.encode('utf8')
		

    elif type=="html":
        H=lambda X:QSE.highlight(X, terms,"css") if highlight and X else X if X else u"-----"
        N=lambda X:X if X else 0
        html=u'<center><b>%s</b> : %2.5f</center>' % (_(u"الزمن المستغرق"),res.runtime)
        html+=suggest_html(query)
        #print terms
        wordshtml=u""
        matches=0
        docs=0
        cpt=1;
        for term in termz :
            if term[0]=="aya":
                
                if term[2]:                
                    matches+=term[2]
                    docs+=term[3]
                    wordshtml+=u'<p dir="%s" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt; color:#00aa00;">%d .  </span><span style=" font-size:14pt; color:#005800;">%s : </span><span style=" font-size:14pt;"> %s </span><span style=" font-size:14pt; color:#005500;">%d </span>%s <span style=" font-size:14pt;">%s  </span><span style=" font-size:14pt; color:#005500;">%d</span><span style=" font-size:14pt;"> %s</span>.' %  (_(u"rtl"),cpt,term[1],_(u"وردت"),term[2],n_(u"مرة",u"مرة",term[2]),_(u"في"),term[3],n_(u"آية",u"آية",term[3]))
                    cpt+=1

                wordshtml+=u"</p>"
        if cpt-1:
            html+=u'<p dir="%s" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><h2 style="font-size:16pt; font-weight:600; color:#ff0000;"> %s ( %d %s %s %d %s   ) : </h2></p>' %  (_(u"rtl"),_(u"الكلمات"),cpt-1,n_(u"كلمة",u"كلمة",cpt-1),_(u"وردت"),matches,n_(u"مرة",u"مرة",matches))
            html+= wordshtml   
            html+=u"<br>"
         
        #traductions
            trad_query=u"( 0"
            for r in reslist :
                trad_query+=" OR gid:"+unicode(r["gid"])+u" "
            trad_query+=" )"+u" AND id:"+unicode(traduction)
            trad_res=TSE.find_extended(trad_query, "gid")
            trad_text={}
            for tr in trad_res:
                trad_text[tr["gid"]]=tr["text"]
        
        if reslist:
            html+="<p align=\"right\" dir='%s' style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><h2 style=\" font-size:15pt; font-weight:600; color:#ff0000;\">%s (%d %s %d %s %d)</h2></p>" % (_(u"rtl"),_(u"النتائج"),start+1,_(u"إلى"),end,_(u"من أصل"),len(res))

        cpt = startpage
        for r in reslist :
            cpt += 1
            html+=u'<fieldset class="res right">'
  
            html += u"<legend class=\"title\"   %s style=\"font-size:14pt; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'arial ,sans serif'; color:#0000ff; \"> %s <span style=\" font-family:'arial ,sans serif'; font-weight:600; color:#0000ff;\"> <b>%d</b> </span><span style=\" font-family:'arial ,sans serif'; color:#0000ff;\">  - %s </span><span style=\" font-family:'arial ,sans serif'; font-weight:600; color:#0000ff;\"> <b>%d</b> </span><span style=\" font-family:'arial ,sans serif'; color:#0000ff;\"> %s </span><span style=\" font-family:'arial ,sans serif'; font-weight:600; color:#0000ff;\"> <b>%s</b> </span>"  % (_(u"dir='rtl'"),_(u"النتيجة رقم"),cpt,_(u"الآية رقم"),r["aya_id"],_(u"من سورة"),H(keywords(r["sura"])[0]))
            recit = Folder[recitation].encode("utf-8")+ "/" + "%03d%03d.mp3" % (r["sura_id"],r["aya_id"])
            html += flashplayer(recit, cpt,width="350") 
            html+= u"<br><span style=\" font-family:'arial ,sans serif';font-size:70%%; color:#0000ff;\">(<span style=\" font-weight:600; color:#9933ff;\">  %s: <b>%d</b>،%s : <b>%s</b> ، %s :  <b>%d</b>، %s : <b>%d</b>، %s  :<b>%d</b>، %s :<b>%d</b>، %s :<b>%d</b></span>)</span></legend>" %(_(u"الرقم"),r["sura_id"],_(u"مكان النزول"),H(r["sura_type"]),_(u"ترتيب النزول"),r["sura_order"],_(u"الآيات"),r["s_a"],_(u"الكلمات"),N(r["s_w"]),_(u"ألفاظ الجلالة"),N(r["s_g"]),_(u"الأحرف"),N(r["s_l"]))
         
            html += u"<br><p align=\"center\" style=\"margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\"font-family:'ArabeyesQr';  font-weight:800; color:#7b563a;\"><br />[ <span style=\"font-family:'me_quran';\"><b>%s</b></span>] <br /></span></p>" % Gword_tamdid(H(r["aya_"]) )
            
            if traduction!="None" and traduction: html += u'<br><p dir="ltr" align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">%s</span></p><br/>' % (trad_text[r["gid"]])
            html += u"<br><p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#808080;\">%s:   <b>%d</b> -(%s : <b>%d</b> ، %s : <b>%d</b>) -   %s :<b>%s</b></span></p> " % (_(u"المنزل"),r["manzil"],_(u"الحزب"),r["hizb"],_(u"الربع"),r["rub"]%4,_(u"الصفحة"),r["page"])       
            html += u"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#808080;\">%s : <b>%s</b> %s : <b>%s</b> %s : <b>%s</b> </span></p>" % (_(u"الفصل"),H(r["chapter"]),_(u"الفرع"),H(r["topic"]),_(u"الباب"),H(r["subtopic"]))        
            html += u"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#808080;\">%s : </span><span style=\" font-weight:600; color:#808080;\"> <b>%d</b> </span><span style=\" color:#808080;\"> - %s :  <b>%d</b>  </span><span style=\" color:#808080;\"> - %s :  <b>%d</b>  </span></p>" % (_(u"عدد الكلمات"),N(r["a_w"]),_(u"عدد الأحرف"),N(r["a_l"]),_(u"عدد ألفاظ الجلالة"),N(r["a_g"]))
            if r["sajda"]==u"نعم": html+=u'<p align="center" %s style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#b88484;">%s  %s،%s %d</span></p>' % (_(u"dir='rtl'"),_(u"هذه الآية تحتوي على سجدة"),H(r["sajda_type"]),_(u"رقمها"),N(r["sajda_id"]))
            html += u"</fieldset>"
        return html.encode('utf8')


    elif type=="bbcode":
        H=lambda X:QSE.highlight(X, terms,"bbcode") if highlight and X else X if X else u"-----"
        N=lambda X:X if X else 0
        html=u'[center][b]%s[/b] : %2.5f[/center]' % (_(u"الزمن المستغرق"),res.runtime)
        html+=suggest_html(query)
        #print terms
        wordshtml=u""
        matches=0
        docs=0
        cpt=1;
        for term in termz :
            if term[0]=="aya":
                
                if term[2]:                
                    matches+=term[2]
                    docs+=term[3]
                    wordshtml+=u'\n [dir=%s][color=green] %d %s : %s %d %s %s %d %s .[/color][/dir]' %  (_(u"rtl"),cpt,term[1],_(u"وردت"),term[2],n_(u"مرة",u"مرة",term[2]),_(u"في"),term[3],n_(u"آية",u"آية",term[3]))
                    cpt+=1


        if cpt-1:
            html+=u'\n  [dir=%s][color=red][size=+2] %s ( %d %s %s %d %s   ) : [/size][/color][/dir]' %  (_(u"rtl"),_(u"الكلمات"),cpt-1,n_(u"كلمة",u"كلمة",cpt-1),_(u"وردت"),matches,n_(u"مرة",u"مرة",matches))
            html+= wordshtml   
            html+=u"\n"
         
        #traductions
            trad_query=u"( 0"
            for r in reslist :
                trad_query+=" OR gid:"+unicode(r["gid"])+u" "
            trad_query+=" )"+u" AND id:"+unicode(traduction)
            trad_res=TSE.find_extended(trad_query, "gid")
            trad_text={}
            for tr in trad_res:
                trad_text[tr["gid"]]=tr["text"]
        
        if reslist:
            html+="\n [dir=%s][size=+2][color=red]%s (%d %s %d %s %d)[/color][/size][/dir]" % (_(u"rtl"),_(u"النتائج"),start+1,_(u"إلى"),end,_(u"من أصل"),len(res))

        cpt = startpage
        for r in reslist :
            cpt += 1
            html+=u'\n\n____________'
  
            html += u"\n\n [dir=%s] [color=blue] %s [b]%d[/b] - %s [b]%d[/b] %s [/color][/dir]"  % (_(u"rtl"),_(u"النتيجة رقم"),cpt,_(u"الآية رقم"),r["aya_id"],_(u"من سورة"),H(keywords(r["sura"])[0]))
            recit = Folder[recitation].encode("utf-8")+ "/" + "%03d%03d.mp3" % (r["sura_id"],r["aya_id"])
            html += flashplayer(recit, cpt,width="350") 
            html+= u"\n[color=gray]( %s: [b]%d[/b]،%s : [b]%s[/b] ، %s :  [b]%d[/b]، %s : [b]%d[/b]، %s  :[b]%d[/b]، %s :[b]%d[/b]، %s :[b]%d[/b]، %s :[b]%d[/b])[/color]" %(_(u"الرقم"),r["sura_id"],_(u"مكان النزول"),H(r["sura_type"]),_(u"ترتيب النزول"),r["sura_order"],_(u"الآيات"),r["s_a"],_(u"الكلمات"),N(r["s_w"]),_(u"ألفاظ الجلالة"),N(r["s_g"]),_(u"الأحرف"),N(r["s_l"]),_(u"الركوعات"),N(r["s_r"]))
         
            html += u"\n\n{ [b]%s[/b] } \n" % Gword_tamdid(H(r["aya_"]) )
            
            if traduction!="None" and traduction: html += u'\n\n%s' % (trad_text[r["gid"]])
            html += u"\n\n[center][color=gray]%s:   [b]%d[/b] -(%s : [b]%d[/b] ، %s : [b]%d[/b]) - %s :[b]%d[/b] -  %s :[b]%s[/b][/color][/center] " % (_(u"المنزل"),r["manzil"],_(u"الحزب"),r["hizb"],_(u"الربع"),r["rub"]%4,_(u"الركوع"),r["ruku"],_(u"الصفحة"),r["page"])       
            html += u"\n>[center][color=gray]%s : [b]%s[/b] %s : [b]%s[/b] %s : [b]%s[/b] [/color][/center]" % (_(u"الفصل"),H(r["chapter"]),_(u"الفرع"),H(r["topic"]),_(u"الباب"),H(r["subtopic"]))        
            html += u"\n[center][color=gray]%s : [b]%d[/b] - %s :  [b]%d[/b]  - %s :  [b]%d[/b] [/color][/center]" % (_(u"عدد الكلمات"),N(r["a_w"]),_(u"عدد الأحرف"),N(r["a_l"]),_(u"عدد ألفاظ الجلالة"),N(r["a_g"]))
            if r["sajda"]==u"نعم": html+=u'\n[center] [dir=%s][color=red]%s  %s،%s %d' % (_(u"rtl"),_(u"هذه الآية تحتوي على سجدة"),H(r["sajda_type"]),_(u"رقمها"),N(r["sajda_id"]))
            html += u"\n"
        return html.encode('utf8')
    
    else:#type==text
		 text = "@"    
		 for r in res:
		 	for key in fields:
			 	if key in r.keys():
			 		val = r[key]	
			 		if val :
			 			text += "#\t" + ara(key) + ":"
			 			if key in ["aya_", "aya", "uth", "uth_"]:
					 		text += QSE.highlight(val, terms) 
					 	else:
					 		text += unicode(val)
				 		text += "\n"
					 			
				 	else: text += "#######"
		 	text += "\r\n"
		 return text.encode('utf8')
	

#	
def visits():
	file = open("log", "r")
	cpt = file.read()
	return cpt

def visitsplus():
	cpt = visits()
	cpt = str(int(cpt) + 1)
	file = open("log", "r+")
	file.write(cpt)

	
	
#
def whoami():
	"""what is alfanous"""
	return """
	.الفانوس هو مشروع محرك بحث قرآني  يحتوي على ميزات بحث للقرآن متقدمة منها اللغوية
	 المشروع يحتاج الى دعم  
	
	"""
