#!/bin/python
# config : utf-8

import json

from alfanous.main import TraductionSearchEngine


LANGS = {
		'el': 'Greek',
		'eo': 'Esperanto',
		'en': 'English',
		'vi': 'Vietnamese',
		'ca': 'Catalan',
		'it': 'Italian',
		'lb': 'Luxembourgish',
		'eu': 'Basque',
		'ar': 'Arabic',
		'bg': 'Bulgarian',
		'cs': 'Czech',
		'et': 'Estonian',
		'gl': 'Galician',
		'id': 'Indonesian',
		'ru': 'Russian',
		'nl': 'Dutch',
		'pt': 'Portuguese',
		'no': 'Norwegian',
		'tr': 'Turkish',
		'lv': 'Latvian',
		'lt': 'Lithuanian',
		'th': 'Thai',
		'es': 'Spanish',
		'ro': 'Romanian',
		'en_GB': 'British English',
		'fr': 'French',
		'hy': 'Armenian',
		'uk': 'Ukrainian',
		'pt_BR': 'Brazilian',
		'hr': 'Croatian',
		'de': 'German',
		'da': 'Danish',
		'fa': 'Persian',
		'bs': 'Bosnian',
		'fi': 'Finnish',
		'hu': 'Hungarian',
		'ja': 'Japanese',
		'he': 'Hebrew',
		'ka': 'Georgian',
		'zh': 'Chinese',
		'kk': 'Kazakh',
		'sr': 'Serbian',
		'sq': 'Albanian',
		'ko': 'Korean',
		'sv': 'Swedish',
		'mk': 'Macedonian',
		'sk': 'Slovak',
		'pl': 'Polish',
		'ms': 'Malay',
		'sl': 'Slovenian',
		'sw': 'Swahili',
		'sd': 'Sindhi',
		'ml': 'Malayalam',
		'tg': 'Tajik',
		'ta': 'Tamil',
		'ur': 'Urdu',
		'uz': 'Uzbek',
		'hi': 'Hindi',
		'tt': 'Tatar',
		'so': 'Somali',
		'az': 'Azerbaijani',
		'bn': 'Bengali',
		'dv': 'Divehi',
		'ha': 'Hausa',
		'ug': 'Uughur'
		} #languages

def  update_translations_list( TSE_index = "../../indexes/extend", translations_list_file = "../../resources/configs/translations.js" ):
      TSE = TraductionSearchEngine( TSE_index )
      list1 = [item for item in TSE.list_values( "id" ) if item]
      list2 = []
      list3 = []
      for id in list1:
	  list2.extend( [item for item in TSE.list_values( "lang", conditions = [( "id", id )] ) if item] )
	  list3.extend( [item for item in TSE.list_values( "author", conditions = [( "id", id )] ) if item] )
      list5 = map( lambda x: LANGS[x] if LANGS.has_key( x ) else x, list2 )
      D = {}
      for i in range( len( list3 ) ):
	  D[list1[i]] = list5[i] + "-" + list3[i]
      TDICT = json.dumps( D )
      f = open( translations_list_file, "w" )
      f.write( TDICT )

      return TDICT
