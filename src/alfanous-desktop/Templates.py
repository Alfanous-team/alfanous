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



""").decode("utf8"))
