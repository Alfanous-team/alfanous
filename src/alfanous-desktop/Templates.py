# -*- coding: utf-8 -*-

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
This module contains the html templates used in the GUI results. The reason 
that we don't separate them in independent files, is to avoid the headache of 
including separated files in packaging.
'''

from jinja2 import Template

AYA_RESULTS_TEMPLATE = Template(("""

<style type="text/css">
.results_header {
	font-size:15pt;  
	color:#ff0000;
}

.main_re_item {

   -moz-background-inline-policy: continuous;
    background: none repeat scroll 0 0 #EEFFEE;
    font-family: arial,sans serif;
    padding: 5px;
    width: 90%;
}

.main_re_item_title {
	font-size: 14pt;
	margin: 0;
	text-indent: 0;
	background: none repeat scroll 0 0 #FFDDDD;
	border-bottom: 1px solid #D2B9A6;
	clear: both;
	color: #0000FF;
	font-family: arial,sans serif;
	font-weight: normal;
	line-height: 1.5em;
	padding: 2px 5px;
}

/* Abdellah */
@import url('reset.css');

@font-face {
	font-family:'Scheherazade';
	src:url('../fonts/ScheherazadeRegOT.ttf');
}

/* original */

.buttons {
	float: left;
	padding-bottom: 20px;
	clear: both;
}

a.button {
	background: none repeat scroll 0 0 #6ED0D6;
	background: -webkit-gradient(linear,0% 40%,0% 70%,from(#6ED0D6),to(#6ED0D6));
	border: 1px solid #DCDCDC;
	border-radius: 2px 2px 2px 2px;
	color: white;
	display: inline-block;
	font: bold 16px Helvetica,Arial,sans-serif;
	height: 15px;
	padding: 2px 35px 4px 16px;
	position: relative;
	text-decoration: none;
	text-shadow: 0 0 4px #0F9AA1;
	width: 6px;
	-webkit-border-radius: 2px;
	-moz-border-radius: 2px;
	background: -moz-linear-gradient(linear,0% 40%,0% 70%,from(#F5F5F5),to(#F1F1F1));
	border: solid 1px #dcdcdc;
	border-radius: 2px;
	-webkit-transition: border-color .218s;
	-moz-transition: border .218s;
	-o-transition: border-color .218s;
}

a.button:hover {
	color: #333;
	border-color: #999;
	-moz-box-shadow: 0 2px 0 rgba(0, 0, 0, 0.2) -webkit-box-shadow:0 2px 5px rgba(0, 0, 0, 0.2);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
}

a.button:active {
	color: #000;
	border-color: #444;
}

.enter{
	background: none repeat scroll 0 0 transparent;
	border: 0 none;
	color: gray;
	direction: rtl;
	font-family: tahoma;
	font-weight: bold;
	width: 220px;
	margin:0;
}

a{color: gray;}
.aya_words a { text-decoration: none; }
a:hover{color: green;}
.select {
	background: url("../images/select.gif") no-repeat scroll right top transparent;
	color: gray;
	font: 13px/17px tahoma;
	height: 40px;
	overflow: hidden;
	padding: 11px 15px 0 0;
	position: absolute;
	width: 191px;
	text-align:right;
}
.styled{height: 40px;
	margin-right: 3px;
	opacity: 0;
	position: relative;
	width: 130px;
	z-index: 5;}
.xtitle
{
	color: Gray;
	font: 12px/29px tahoma;
}

.xbutton {
	padding: 7px;
	cursor: pointer;
	font-family: Arial, Geneva, Sans-serif;
	font-size: 10pt;
	font-weight: bold;
	color: black;
	min-width: 70px;
	margin: 0 5px 9px 0;
	/* Css3 Effects */
	border-radius:4px ;
	-moz-border-radius:4px ;
	-webkit-border-radius:4px ;
	opacity:0.8;
	filter: alpha(opacity=80); }
	.xbutton:hover,.xbutton:focus {
	outline: 0;
	-webkit-box-shadow:0 0 4px silver;
	-moz-box-shadow:0 0 4px silver;
	opacity:1;
	filter: alpha(opacity=100);
}

.gray {
	background: #ffffff; /* old browsers */
	background: -moz-linear-gradient(top, #ffffff 0%, #e5e5e5 100%); /* firefox */
	background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,#ffffff), color-stop(100%,#e5e5e5)); /* webkit */
	filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#e5e5e5',GradientType=0 ); /* ie */
	text-shadow:0 1px 1px #eeeeee;
	-moz-text-shadow:0 1px 1px #eeeeee;
	-webkit-text-shadow:0 1px 1px #eeeeee;
	border: 1px solid silver;
}

.green {
	background: #007419; /* old browsers */
	background: -moz-linear-gradient(top, #007419 0%, #005011 100%); /* firefox */
	background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,#007419), color-stop(100%,#005011)); /* webkit */
	filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#007419', endColorstr='#005011',GradientType=0 ); /* ie */
	text-shadow:0 1px 1px #eeeeee;
	-moz-text-shadow:0 1px 1px #eeeeee;
	-webkit-text-shadow:0 1px 1px #eeeeee;
	border: 1px solid silver;
}

.modal {
	opacity:1;
	position:absolute;
	top:10px;
	left:10px;
	background-color:#fff;
	display:none;
	width:300px;
	padding:15px;
	border:2px solid #333;
	-moz-border-radius:6px;
	-webkit-border-radius:6px;
	-moz-box-shadow: 0 0 50px #ccc;
	-webkit-box-shadow: 0 0 50px #ccc;
}

.modal h2 {
	/*background:url(../images/info.png) 0 50% no-repeat; image missing*/
	margin:0px;
	padding:10px 0 10px 45px;
	border-bottom:1px solid #333;
	font-size:20px;
}

.external,.bo {
	margin:3px;
	border:0
}

.external:hover,.bo:hover {
	margin-left:4px;
}

.optaly {
	color: gray;
	font-size: 12px;
}

.newur {
	margin-left: 27px;
}
.xbre{
	border: 2px solid gray;
	color: #0F9AA1;
	font-family: Times New Roman;
	font-size: 28px;
	font-weight: bold;
	padding: 6px;
	text-shadow:0 0 3px gray;
	-moz-text-shadow:0 0 3px gray;
	-webkit-text-shadow:0 0 3px gray;
	-webkit-border-radius: 18px;
	-moz-border-radius: 18px;
}

.main_re_item
{
	background: url("../images/back_g.gif") repeat scroll 0 0 transparent;
	-webkit-border-radius: 35px;
	-moz-border-radius: 35px;
	border-radius: 35px;
	border:0;
	padding: 5px;
}

.main_re_item_title
{
	background: none repeat scroll 0 0 white;
	border: 1px solid green;
	-webkit-border-radius: 12px;
	-moz-border-radius: 12px;
	border-radius: 12px;
	font-size: 14pt;
	margin: 0 15px 0 0;
	padding: 6px;
	text-indent: 0;
	box-shadow: 0 0 8px green;
}

/* +some fun */


.awa-box {
	border:0 none;
	display: inline-block;
	margin:0;
	padding:0;
	float: left;
	position: relative;
	top: 20px;
	left: 10px;
	z-index:95;
	text-align:center;
}

.feedback-box {

	left:0;
	position: fixed;
	top:220px;

 }

.feedback-box a {
	margin-left: -38px;
	line-height:50px;
	padding:0 10px;
	font-weight: bold;
	-webkit-transform: rotate(-90deg);
	-moz-transform: rotate(-90deg);
	-ms-transform: rotate(-90deg);
	-o-transform: rotate(-90deg);
	transform: rotate(-90deg);
	background-color: #3AB034; /*#339A63*/
	color: white;
	display: block;
	height: 41px;
}


.follow-box {
	border:0 none;
	clear:both;
	margin:0;
	padding:0;
	position: fixed;
	top:150px;
	right:0;
	z-index:95;
	width:50px;
	text-align:right;
}

.follow-box a:hover {
	margin-right: 7px;
}

.footer {
	font-family: tahoma;
	font-size: 14px;
	height:20px;
	margin-top:80px;
	text-align: center;
}

#vedio,#vedio3,#vedio4,#vedio5 {
	width:670px
}

.style2
	{
		width: 293px;
	}
	.style3
	{
		width: 227px;
	}
	.style4
	{
		background-color: #CCCCCC;
	}
	.style5
	{
		width: 293px;
		background-color: #CCCCCC;
	}
	.style6
	{
		width: 227px;
		background-color: #CCCCCC;
	}
	.style7
	{
		background-color: #C0C0C0;
	}
	.style8
	{
		width: 293px;
		background-color: #C0C0C0;
	}
	.style9
	{
		width: 227px;
		background-color: #C0C0C0;
	}
	.xdrops_continer{direction:rtl;}

/* Abdellah */

/*
#help_btn {
	position: absolute;
	top:10px;
	right:0;
	z-index:95;
}

#down_btn {
	position: absolute;
	top:10px;
	right:50px;
	z-index:95;
}
*/

#vote_btn a {
	font-weight: normal;
	text-decoration: none;
	color: #000069;
	padding-left: 20px;
	padding-right: 20px;
}


.pages img, select {
	cursor:pointer;
}

#suggestions {
	background-color: #ecf7f9;
	margin: 10px 0px 10px 0px;
	padding: 15px 15px 15px 15px;
}

#suggestions a {
	text-decoration: none;
}

#search_words {
	background-color: #ecf7f9;
	margin: 10px 0px 10px 0px;
	padding: 15px 15px 15px 15px;
}

.details_label {
	display: inline;
	font-size: 12px;
	padding: 1px 5px 2px 5px;
	margin: 1px 1px 0px 2px;
}

.word_item {
	margin: 1px 0px 1px 0px;
	padding: 0px 0px 0px 0px;
}

.result_item0 {
	background-color: #EFE;
	margin: 2px 5px 15px 15px;
	padding: 0px 2px 5px 2px;
}

.result_item1 {
	background-color: #DFD;
	margin: 2px 5px 15px 15px;
	padding: 0px 2px 5px 2px;
}

.word_count {
	background-color: #666;
	color: #FFF;
}

.word_info0 {
	background-color: #F50;
	color: #FFF;
	font-size: 14px;
	font-weight: bold;
}

.word_stat0 {
	background-color: #888;
	color: #FFF;
}

.word_stat1 {
	background-color: #555;
	color: #FFF;
}

.word_vocalization_nb {
	background-color: #90A;
	color: #FFF;
}

.word_derivation_nb {
	background-color: #50F;
	color: #FFF;
}

.word_vocalization {
	background-color: #FFF;
	color: #90A;
	/* font-size:100%;*/
}

.item_number {
	background-color: #FFF;
	font-size: 2em;
	font-weight: bold;
	left: -10px;
	padding: 0px 5px 1px 5px;
	position: relative;
	top: -10px;
}

.quran {
	direction: rtl;
	font-family: me_quran, ArabeyesQr, Scheherazade,  KacstBook, KacstQurn,  "KFGQPC Uthman Taha Naskh", Arial;
	font-size: 1em; 
	margin: 2px 5px 10px 5px;
}

.match {
	color: #181;
}

.word_details, .sura_details, .aya_details {
	margin: 5px 5px 0px 20px;
}

.aya_stat0, .sura_stat1 {
	background-color: #00A;
	color: #FFF;
}

.aya_stat1, .sura_stat2 {
	background-color: #30D;
	color: #FFF;
}

.aya_stat2, .sura_stat3 {
	background-color: #00F;
	color: #FFF;
}

.aya_pos0 {
	background-color: #074;
	color: #FFF;
}

.aya_pos1 {
	background-color: #062;
	color: #FFF;
}

.aya_pos2 {
	background-color: #084;
	color: #FFF;
}

.aya_pos3 {
	background-color: #094;
	color: #FFF;
}

.sura_info0 {
	background-color: #F50;
	color: #FFF;
	font-size: 14px;
	font-weight: bold;
}

.sura_info1 {
	background-color: #E80;
	color: #FFF;
}

.sura_stat0 {
	background-color: #90A;
	color: #FFF;
}

.sura_ord0 {
	background-color: #666;
	color: #FFF;
}

.sura_ord1 {
	background-color: #888;
	color: #FFF;
}

.sura_ord1 {
	background-color: #888;
	color: #FFF;
}

.sura_ord1 {
	background-color: #888;
	color: #FFF;
}


.aya_sajda_exist {

	background-color: #E44;
	color: #FFF;
	
}

.aya_sajda_id {
	
	background-color: #C44;
	color: #FFF;
	
}

.aya_sajda_type {
	background-color: #A44;
	color: #FFF;
}

.clickable {
	font-weight: bold; 
	border-style:solid;
	border-color:#A0C;
	border-width:1px;
}

.filter {
	
	border-color:#000;
	
}

.no_decoration {
	text-decoration:none;
		
}

/* Abdellah AD.*/


.left {
    float: left;
}

img.left {
    margin-right: 10px;
}

.right {
    float: right;
}

img.right {
    margin-left: 10px;
}



/* Footer*/


div#footer-big-wrapper {
    font-family: 'Droid Sans',Georgia, Arial, sans-serif;
    height: 303px;
    background-image: url('../images/footer.png');
    clear: both;
    color: #aaa;
}

div#footer-big-wrapper a {
    text-decoration: none;
    color: #aaa;
}

div#footer-big-wrapper a:hover {
    text-decoration: none;
    color: #fff;
}

div#footer-big {
    height: 303px;
    width: 960px;
    margin: auto;
    font-size: 11px;
    text-shadow: 0px 1px 1px #000;
    background-image: url('../images/footer-bg.png');
    background-position: center;
    background-repeat: no-repeat;
}

div#footer-big div.column {
    float: left;
    width: 180px;
    padding: 20px 20px 20px 0;
}

div#footer-big div.last {
    padding: 20px 0 20px 60px;
    width: 330px;
}

div#footer-big div.last img {
    margin-bottom: 5px;
}

/* Abdellah only1 */
div#footer-big div.last p:last-child {
	line-height: 150%;
}

div#footer-big h1 {
    color: #aaa;
    font-size: 16px;
    margin-bottom: 20px;
    text-shadow: none;
}

div#footer-big ul {
    width: 150px;
}

div#footer-big ul li {
    height: 30px;
    line-height: 30px;
    border-top: 1px solid #2e353d;
}

div#footer-big ul li.last {
    border-bottom: 1px solid #2e353d;
}

div#footer-small-wrapper {
    font-family: 'Droid Sans',Georgia, Arial, sans-serif;
    height: 30px;
    background-color: #000;
    border-top: 1px solid #2e353d;
    color: #aaa;
    font-size: 11px;


}

div#footer-small {
    width: 960px;
    margin: auto;
    line-height: 30px;

}

div#footer-small a {
    text-decoration: none;
    color: #fff;
}

div#footer-small a:hover {
    text-decoration: underline;
}

.quran_decoration {
direction: rtl;
font-family: ArabeyesQr, Scheherazade;
}

</style>


{% if results.error.code == 0  %} 
		<!-- Suggestions-->
		{% if suggestions.error.code == 0 and suggestions.suggest %} 
			<div id='suggestions' style=" text-align:left" >
			<h2 class='suggestionheader'>{{ _("Suggestions:") }}</h2>
			{% for suggestion_key, suggestion_item in suggestions.suggest.items() %}
				<p style='direction:ltr;' >
				<div class='word_details'>
				<span style=' font-size:14pt; color:#00aa00;'> {{ forloop.counter }}. </span>
				<div class='details_label word_info0'>  {{ "word" }} |  {{ suggestion_key }} </div>
				{% for suggestion_sub_item  in suggestion_item %}
	
							<div class='details_label word_stat1 clickable'> {{ suggestion_sub_item }}</div>
	
				{% else %}
					<div class='details_label word_stat0'> {{ "no suggestions!" }} </div>
				{% endfor %}
				</div></p>
			{% endfor %}
		</div><br />
		{% endif %}

		{% if results.search.interval.total %}
			{% if results.search.words.global.nb_words %}
				<!-- Words list -->
				<div id='search_words' style=" text-align:left" >
				  <h2 class='wordheader'> {{ "Words:" }} </h2>
					  <div class='details_label word_count'>  
					    {{ "words" }} | {{  results.search.words.global.nb_words }} 
					  </div>
					  <div class='details_label word_stat0'> 
					    {{ "occurances" }}  | {{ results.search.words.global.nb_matches }} 
					  </div> 
					  <div class='details_label word_vocalization_nb'> 
					    {{ "vocalizations" }} | {{ results.search.words.global.nb_vocalizations }} 
					  </div> 
				  <br />
				{% for wordcpt, wordstat in results.search.words.individual.items() %}
						<p style='direction:ltr;' >
						  <div class='word_details'>
						    <span style=' font-size:14pt; color:#00aa00;'> {{ wordcpt }}.  </span>
						
							<div class='details_label word_info0 clickable'> {{ _("word") }} | {{ wordstat.word }} {% if wordstat.romanization %} ( {{ wordstat.romanization }} ) {%  endif %} </div>
							<div class='details_label word_stat0'> {{ _("occurances") }} | {{ wordstat.nb_matches }} </div>
							<div class='details_label word_stat1'> {{ _("ayates") }} |  {{ wordstat.nb_ayas }} </div>
							<br />
							<div class='word_extra_details'>
							<div class='details_label word_vocalization_nb'> {{ _("vocalizations") }} | {{ wordstat.nb_vocalizations }} </div>
							{% for vocalization in wordstat.vocalizations %} 
								<div class='details_label word_vocalization clickable'> {{ vocalization }} </div>
							{% endfor %}
							
							
							{% if wordstat.nb_synonyms != 0 %}
								<br />
								<div class='details_label word_synonym_nb'> {{ _("synonyms") }} | {{ wordstat.nb_synonyms }} </div>
								{% for synonym in wordstat.synonyms %} 
											<div class='details_label word_synonym clickable'> {{ synonym }} </div>
								{% endfor %}
							
							{% endif %}
							
			
							{% if wordstat.nb_derivations != 0 %}
								<br />
								<div class='details_label word_derivation_nb'> {{ _("derivations") }} | {{ wordstat.nb_derivations }} </div> 
								{% for derivation in wordstat.derivations %} 
								
									<div class='details_label word_derivation clickable'> {{ derivation }} </div>
								{% endfor %}
							{% endif %}
						{% if wordstat.nb_annotations %}
						{% for annotation_word, parts in wordstat.annotations.items() %}
							{% for part_order, annotation_detail in parts.items() %} 
								<p   class='annotation_details'>
								<div style=' font-size:12pt; color:#99aa88;'> {{ wordcpt }}.{{ forloop.counter }}.{{ part_order }} </div>
								<div class='details_label word_annotation clickable'> {{ _("Annotation") }} | {{ annotation_word }} </div>
								<div class='details_label word_annotation_info0'> {{ _("ID") }} | {{ annotation_detail.word_gid }} </div>
								<div class='details_label word_annotation_info0'> {{ _("sura,aya") }} | {{ annotation_detail.sura_id }},{{ annotation_detail.aya_id }} </div>
								{% if annotation_detail.token %}
									<div class='details_label word_annotation_info1'> {{ _("token") }} | {{ annotation_detail.token }} ( {{ annotation_detail.arabictoken }}) </div>
								{% endif %}
								{% if annotation_detail.part %}
									<div class='details_label word_annotation_info1'> {{ _("part") }} | {{ annotation_detail.part }} </div>
								{% endif %}
								{% if annotation_detail.type %}
									<div class='details_label word_annotation_info2'> {{ _("type") }} | {{ annotation_detail.type }} </div>
								{% endif %}
								{% if annotation_detail.pos %}
									<div class='details_label word_annotation_info2'> {{ _("POS") }} | {{ annotation_detail.pos }} ({{ annotation_detail.arabicpos }}) </div>
								{% endif %}
								{% if annotation_detail.lemma %}
									<div class='details_label word_annotation_info5'> {{ _("lemma") }} | {{ annotation_detail.lemma  }} ({{ annotation_detail.arabiclemma }}) </div>
								{% endif %}
								{% if annotation_detail.root %}
									<div class='details_label word_annotation_info5'> {{ _("root") }} | {{ annotation_detail.root }} ({{ annotation_detail.arabicroot }}) </div>
								{% endif %}
								{% if annotation_detail.special %}
									<div class='details_label word_annotation_info5'> {{ _("special") }} | {{ annotation_detail.special }} ({{ annotation_detail.arabicspecial }}) </div>
								{% endif %}
								{% if annotation_detail.aspect %}
									<div class='details_label word_annotation_info6'> {{ _("aspect") }} | {{ annotation_detail.aspect }} </div>
								{% endif %}
								{% if annotation_detail.state %}
									<div class='details_label word_annotation_info6'> {{ _("state") }} | {{ annotation_detail.state }} </div>
								{% endif %}
								{% if annotation_detail.form %}
									<div class='details_label word_annotation_info6'> {{ _("form") }} | {{ annotation_detail.form }} </div>
								{% endif %}
								{% if annotation_detail.case %}
									<div class='details_label word_annotation_info6'> {{ _("case") }} | {{ annotation_detail.case }} ( {{ annotation_detail.arabiccase }}) </div>
								{% endif %}
								{% if annotation_detail.derivation %}
									<div class='details_label word_annotation_info6'> {{ _("derivation") }} | {{ annotation_detail.derivation }} </div>
								{% endif %}
								{% if annotation_detail.person %}
									<div class='details_label word_annotation_info3'> {{ _("person") }} | {{ annotation_detail.person }} </div>
								{% endif %}
								{% if annotation_detail.number %}
									<div class='details_label word_annotation_info3'> {{ _("number") }} | {{ annotation_detail.number }} </div>
								{% endif %}
								{% if annotation_detail.gender %}
									<div class='details_label word_annotation_info3'> {{ _("gender") }} | {{ annotation_detail.gender }} </div>
								{% endif %}
								{% if annotation_detail.voice %}
									<div class='details_label word_annotation_info3'> {{ _("voice") }} | {{ annotation_detail.voice }} </div>
								{% endif %}
								</p>
							{% endfor %}
						{% endfor %}
						{% endif %}
						   </div>
						   </div>
				{% endfor %}
				</div> 
			{% endif %}
			
			
			<!-- Ayahs results -->
			<h2 class="results_header">
			  {{ _("Results") }} ( {{ results.search.interval.start }} 
			  {{ _("to") }} {{ results.search.interval.end }}
			  {{ _("of") }} {{ results.search.interval.total }} )
			</h2><br/>
			
			{% for ayaresult_id, ayaresult_content in  	results.search.ayas.items() %}
			    <fieldset class='main_re_item'>
				  <legend class='main_re_item_title' style=' direction:ltr;' >
				    <span style='text-align:left; color:#0000ff;'>
				      {{ _("Result n°") }} <b> {{ ayaresult_id }} </b> 
				    </span>
				    {% if ayaresult_content.aya.recitation %}
				    <span style='text-align:right;'>
						<object width='350' height='24' id='audioplayer_{{ ayaresult_id }}' name='audioplayer_{{ ayaresult_id }}' data='swf/player.swf' type='application/x-shockwave-flash'>
							<param value='/static/swf/player.swf' name='movie'>
							<param value='playerID=audioplayer_{{ ayaresult_id }}&amp;soundFile={{ ayaresult_content.aya.recitation}}' name='FlashVars'>
							<param value='high' name='quality'>
							<param value='false' name='menu'>
							<param value='transparent' name='wmode'>
						</object>
					</span><br />
					{% endif %}
					  
				   {% if ayaresult_content.sura %}
					   <div class='sura_details'>

							<div class='details_label sura_info0 clickable filter'> {{ _("Sura") }} | {{ ayaresult_content.sura.name }} </div> 
							<div class='details_label sura_ord0'> {{ _("n°") }} | {{ ayaresult_content.sura.id }} </div>

							<div class='details_label sura_info1 clickable filter'> {{ _("type") }} | {{ ayaresult_content.sura.type }} </div>
							<div class='details_label sura_ord1'> {{ _("revelation_order") }}  | {{ ayaresult_content.sura.order }}</div>
							<div class='details_label sura_stat0'> {{ _("ayahs") }} | {{ ayaresult_content.sura.ayas }} </div> 
							{% if ayaresult_content.sura.stat %}
								<br />
								<div class='sura_stat_details'>
									<div class='details_label sura_stat1'> {{ _("words") }} | {{ ayaresult_content.sura.stat.words }} </div>
									<div class='details_label sura_stat2'> {{ _("letters") }} | {{ ayaresult_content.sura.stat.letters }} </div>
									<div class='details_label sura_stat3'> {{ _("divine names") }} | {{ ayaresult_content.sura.stat.godnames }} </div>
								</div>
							{% endif %}
						</div>
				 	{% endif %}
				  </legend>
				  <br />
				  	{% if ayaresult_content.aya.prev_aya  and ayaresult_content.aya.prev_aya.id != 0 %}
					  		<p  style='text-align:center;direction:rtl;' >
					  		<span class='quran_decoration prev_aya'>
							 [ </span>
					  		<span class="quran prev_aya">
					  		  {{ ayaresult_content.aya.prev_aya.text }} 
					  		  
					  		 </span>
					  		 <span class='quran_decoration prev_aya'>
							 ] </span>
							 <span style='direction:ltr;' class='prev_aya'>
								({{ ayaresult_content.aya.prev_aya.sura_arabic }} {{ ayaresult_content.aya.prev_aya.id }})  
					  		</span>
					  		 </p>
					  		
					  		
					  {% endif %}
				  <p style='text-align:center; direction:rtl;'>
					 <span class='quran_decoration main_aya'>
					 [ </span>
					 
					 <span  class='aya_words quran main_aya'>
					  		 {{ ayaresult_content.aya.text }} 
					  </span> 
					 
					  
					 <span class='quran_decoration main_aya'>
					 ] </span>
					  <span style='direction:rtl;' class='main_aya'>
					  		   
											({{ ayaresult_content.identifier.sura_arabic_name }} {{ ayaresult_content.aya.id }})  
							
					   
					  </span>
					  <br />
				    </p>
				    <!-- next ayah -->
				    {% if ayaresult_content.aya.next_aya and ayaresult_content.aya.next_aya.id != 9999 %}
					  		<p  style='text-align:center;direction:rtl;'>
					  		<span class='quran_decoration next_aya'>
							 [ </span>
					  		<span class="quran next_aya">
					  		  {{ ayaresult_content.aya.next_aya.text }} 
					  		  
					  		 </span>
					  		 <span class='quran_decoration next_aya'>
							 ] </span>
							 <span style='direction:ltr;' class='next_aya'>
							   
					
							({{ ayaresult_content.aya.next_aya.sura_arabic }} {{ ayaresult_content.aya.next_aya.id }}) 
							
							</span>
					  		 </p>
					  		
					  		<br />
					  {% endif %}
				    <br />
					  
					  {% if ayaresult_content.aya.translation %}
					  		<p style='direction:ltr;text-align:center;' >
					  		<span class="quran_translation">
					  	  		  {{ ayaresult_content.aya.translation }} 
					   		</span></p>
					  		<br />
					  {% endif %}
					  
					  {% if ayaresult_content.theme %}
						  <p style='text-align:center;' class='theme_details' >
						  	<span style=' color:#808080;'>
						  	{% if ayaresult_content.theme.chapter %}
						  		{{ _("Chapter") }} :  
										  		<b> {{ ayaresult_content.theme.chapter }} </b>
						  	{% endif %}
							{% if ayaresult_content.theme.topic %} 
								{{ _("Topic") }} :  
				
								<b> {{ ayaresult_content.theme.topic }} </b>
							{% endif %}
							{% if ayaresult_content.theme.subtopic %}
								{{ _("Subtopic") }}:  
						
								<b> {{ ayaresult_content.theme.subtopic }} </b> 
							{% endif %}			
							</span>
						  </p>
					   {% endif %}
					  	
					  {% if ayaresult_content.stat or 	ayaresult_content.position %}		
						  <div class='aya_details' style='text-align:center;'>
						  	{% if ayaresult_content.stat %}
			
							  	<div class='details_label aya_stat0 clickable'> {{ _("words") }} | {{ ayaresult_content.stat.words }} </div>
				
								<div class='details_label aya_stat1 clickable'> {{ _("letters") }} | {{ ayaresult_content.stat.letters }} </div>
						
								<div class='details_label aya_stat2 clickable'> {{ _("divine names") }} | {{ ayaresult_content.stat.godnames }} </div>
							{% endif %}
							{% if ayaresult_content.position %}
		
								<div class='details_label aya_pos0 clickable filter'> {{ _("manzil") }} | {{ ayaresult_content.position.manzil }} </div>
								<div class='details_label aya_pos1 clickable filter'> {{ _("hizb") }} | {{ ayaresult_content.position.hizb }} </div>
								<div class='details_label aya_pos2'> {{ _("quart") }} | {{ ayaresult_content.position.rub + 1 }} </div>		
								<div class='details_label aya_pos3 clickable filter'> {{ _("page") }} | {{ ayaresult_content.position.page }} </div>
							{% endif %}
						  </div><br />
					  {% endif %}
					  {% if  ayaresult_content.sajda.exist %}
					  		<br /><div>
					  		<div class='details_label aya_sajda_exist clickable'> {{ _("sajda") }} </div>
							<div class='details_label aya_sajda_id'> {{ _("n°") }} | {{ ayaresult_content.sajda.id }} </div>
						    <div class='details_label aya_sajda_type'> {{ _("type") }} | {{ ayaresult_content.sajda.type }}</div>
							</div><br />
					  {% endif %}
				
			     </fieldset>
			     <hr />
			     <br />
			{% endfor %}
			
		
				
			<!-- Pages control # bottom one -->
			{% block pages_bottom %} {% endblock %}
			
		{% else %}
			<br />
			<div class='notfound'><p> {{ _("Sorry! there is no results for this search query.") }} </p></div>
			<br />
		{% endif %}		
	{% elif results.error %}
		<div id='error' class='error'><p> {{ _("Error ") }} ({{ results.error.code }}) : {{ results.error.msg }}</p></div>
	{% else %}
		
	{% endif %}



""").decode("utf8"))
