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

AYA_RESULTS_TEMPLATE = Template("""

<style type="text/css">



a {color: black;}

.aya_words a { text-decoration: none; }
a:hover{color: green;}


.xbre
{
	color: Blue;
	font: 12px/29px tahoma;
}

.xtitle
{
	color: Gray;
	font: 12px/29px tahoma;
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
	.xdrops_continer{direction:ltr;}

/* Abdellah */


.wordheader {
	font-size:16pt;
	color:#ff0000;
	display: inline-block;
}

.suggestionheader {
	font-size:16pt; 
	color:#ff0000;
}

.runtime {
	color:grey;
	font-size: 12px;
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
	margin: 1px 1px 1px 2px;
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

.word_vocalization {
	background-color: #FFF;
	color: #90A;
	padding: 5px 2px 4px 2px;
	/* font-size:100%;*/
}

.word_synonym_nb {
	background-color: #09A;
	color: #FFF;
}

.word_synonym {
	background-color: #FFF;
	color: #09A;
	padding: 5px 2px 4px 2px;
	/* font-size:100%;*/
}

.word_derivation_nb {
	background-color: #A90;
	color: #FFF;
}

.word_derivation {
	background-color: #FFF;
	color: #A90;
	padding: 5px 2px 4px 2px;
	/* font-size:100%;*/
}



.word_annotation_nb {
	background-color: #0A9;
	color: #FFF;	
}

.annotation_details {
	margin:10px 2px 5px 30px;
}

.word_annotation {
	background-color: #0A9;
	color: #FFF;
	font-size: 12px;
	font-weight: bold;
}

.word_annotation_info0 {
	background-color: #3BB;
	color: #FFF;
}

.word_annotation_info1 {
	background-color: #7B8;
	color: #FFF;
}

.word_annotation_info2 {
	background-color: #5A9;
	color: #FFF;
}

.word_annotation_info3 {
	background-color: #497;
	color: #FFF;
}

.word_annotation_info4 {
	background-color: #5B4;
	color: #FFF;
}

.word_annotation_info5 {
	background-color: #7D7;
	color: #FFF;
}

.word_annotation_info6 {
	background-color: #088;
	color: #FFF;
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
	font-family: me_quran, Scheherazade,  KacstBook, KacstQurn, ArabeyesQr, "KFGQPC Uthman Taha Naskh", Arial;

}

.main_aya {
	font-size: 22px;
	margin: 2px 5px 10px 5px;
	color: #000;
	direction: rtl;
}

.prev_aya {
	font-size: 14px;
	margin: 2px 5px 10px 5px;
	color:#666;
}

.next_aya {
	font-size: 14px;
	margin: 2px 5px 10px 5px;
	color:#666;
}

.quran_decoration {
	direction: rtl;
	font-family: ArabeyesQr, Scheherazade;
	line-height: 180%;
	
}

.quran_translation {
	font-family: Droid Sans, Tahoma, Bitstream Vera Sans, DejaVu Sans, Verdana, Geneva, Arial, Sans-serif; 
	line-height: 150%;
	direction: ltr;
}


.match {
	color: #181;
}

/* Assem: Terms Static Highlighting colors */
.term0, .term10 { color: #118; }
.term1, .term11 { color: #811; }
.term2, .term12 { color: #807; }
.term3, .term13 { color: #F50; }
.term4, .term14 { color: #f00; }
.term5, .term15 { color: #f39; }
.term6, .term16 { color: #f43; }
.term7, .term17 { color: #660; }
.term8, .term18 { color: #444; }
.term9, .term19 { color: #5C3; }


.word_details,  .sura_details, .aya_details, .sura_stat_details, .theme_details {
	margin: 8px 5px 2px 20px;
}

.word_extra_details {
	margin: 5px 5px 10px 40px;
	padding: 3px 1px 1px 1px;
}


.aya_stat0, .sura_stat1, .translation_author {
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

.aya_pos0, .translation_language {
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
	border-width:2px;
}

.filter {
	
	border-color:#000;
	
}

.no_decoration {
	text-decoration:none;
		
}

.page_link {
				color: blue;
			}





/* Assem: Error, NotFound */
.notfound {
	margin: 30px 30px 30px 30px;
}

.error {
	margin: 30px 30px 30px 30px;

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

.justify {
	text-align: justify;
}


.list li{
	display:list-item;
	list-style-type: circle;
	margin: 10px;
	padding: 5px;
}

.list a {
	color:blue;
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
			{% if results.search.words.nb_words %}
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
				{% for wordcpt, wordstat in results.search.words.individual.items %}
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
								<div class='details_label word_vocalization clickable quran'> {{ vocalization }} </div>
							{% endfor %}
							
							
							{% if wordstat.nb_synonyms != 0 %}
								<br />
								<div class='details_label word_synonym_nb'> {{ _("synonyms") }} | {{ wordstat.nb_synonyms }} </div>
								{% for synonym in wordstat.synonyms %} 
											<div class='details_label word_synonym clickable quran'> {{ synonym }} </div>
								{% endfor %}
								<div class='details_label word_synonym clickable quran'>  ~  </div>
							{% endif %}
							
			
							{% if wordstat.nb_derivations != 0 %}
								<br />
								<div class='details_label word_derivation_nb'> {{ _("derivations") }} | {{ wordstat.nb_derivations }} </div> 
								{% for derivation in wordstat.derivations %} 
								
									<div class='details_label word_derivation clickable quran'> {{ derivation }} </div>
								{% endfor %}
								<div class='details_label word_derivation clickable quran'>  >  </div>
							{% endif %}

						{% for annotation_word, parts in wordstat.annotations.items %}
							{% for part_order, annotation_detail in parts.items %} 
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
						   </div>
						   </div>
				{% endfor %}
				</div> 
			{% endif %}
			
			
			<!-- Ayahs results -->
			<h2 style=' font-size:15pt;  color:#ff0000;'>
			  {{ _("Results") }} ( {{ results.search.interval.start }} 
			  {{ _("to") }} {{ results.search.interval.end }}
			  {{ _("of") }} {{ results.search.interval.total }} )
			</h2><br/>
			
			{% for ayaresult_id, ayaresult_content in  	results.search.ayas.items() %}
			    <fieldset class='main_re_item'>
				  <legend class='main_re_item_title' style='font-size:14pt; direction:ltr;' >
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
								({{ ayaresult_content.aya.prev_aya.sura }} {{ ayaresult_content.aya.prev_aya.id }})  
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
					  		   
											({{ ayaresult_content.identifier.sura_name }} {{ ayaresult_content.aya.id }})  
							
					   
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
							   
					
							({{ ayaresult_content.aya.next_aya.sura }} {{ ayaresult_content.aya.next_aya.id }}) 
							
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
						  <div class='aya_details'>
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
						  </div><br /><br />
					  {% endif %}
					  {% if  ayaresult_content.sajda.exist %}
					  		<br /><div>
					  		<div class='details_label aya_sajda_exist clickable'> {{ _("sajda") }} </div>
							<div class='details_label aya_sajda_id'> {{ _("n°") }} | {{ ayaresult_content.sajda.id }} </div>
						    <div class='details_label aya_sajda_type'> {{ _("type") }} | {{ ayaresult_content.sajda.type }}</div>
							</div><br />
					  {% endif %}
				
			     </fieldset><br />
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



""")