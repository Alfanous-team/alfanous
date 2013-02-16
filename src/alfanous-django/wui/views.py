# Create your views here.

"""

TODO make a fields English-Arabic mapping based on the "bidi" value to be used in localization

"""
import json
import datetime
from sys import path


from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.conf import settings

from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.translation import pgettext_lazy # for ambiguities
from django.utils.translation import get_language_info
from django.utils.datastructures import SortedDict

## either append the path of alfanous API as:
path.append( "alfanous.egg/alfanous" ) ## an egg, portable
path.append( "../../src" ) ## a relative path, development mode
path.append( "/home/alfanous/alfanous-django/src/" ) ## absolute  path, server mode

from alfanous.Outputs import Raw


# load the search engine, use default paths
RAWoutput = Raw()

def control_access ( request ):
	""" Controling access to  the API """
	#print request.META["REMOTE_ADDR"]
	#print request.META["REMOTE_HOST"]
	#print request.META["QUERY_STRING"]
	#print request.META["HTTP_REFERER"]
	#print "is ajax?", request.is_ajax()
	return True


def jos2( request ):
    """ JSON Output System II """
    control_access( request )
    if len( request.GET ):
        response_data = RAWoutput.do( request.GET )
        response = HttpResponse( json.dumps( response_data, sort_keys = False, indent = 4 ), mimetype = "application/json" )
        response['charset'] = 'utf-8'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'
        #response['Content-Encoding'] = 'gzip'
    else:
        response_data = RAWoutput._information["json_output_system_note"]
        response = HttpResponse( response_data )
    return response

def results( request, unit = "aya", language = None ):
    """     """
    available_units = SortedDict ( [
						( "aya", "Ayahs" ),
						#( "sura", "Surahs" ),
						#( "word", "Words" ),
						( "translation", "Translations" ),
						#  tafsir, hadith, dream, poem
						] )
    if unit not in available_units.keys():
    	unit = "aya"
    mutable_request = {}
    for k, v in request.GET.items():
    	mutable_request[k] = v
    show_params = { "action":"show", "query": "all" }
    if mutable_request.has_key( "query" ) and not ( mutable_request.has_key( "action" ) and not mutable_request["action"] == "search" ):
        search_params = mutable_request
        suggest_params = { "action":"suggest", "query": mutable_request["query"] }
    elif mutable_request.has_key( "search" ):
    	## back-compatibility of links:
    	# if it's a classic API style, wrap it to the new API style
        search_params = { "action": "search",
                        "query": mutable_request["search"],
                        "page": mutable_request["page"] if mutable_request.has_key( "page" ) else 1,
                        "sortedby": rmutable_request["sortedby"] if mutable_request.has_key( "sortedby" ) else "relevance"
                        }
        suggest_params = {
						"action":"suggest",
                        "query": mutable_request["search"]
                         }
    else:
        search_params = {}
        suggest_params = {}
    #override the unit flag
    mutable_request["unit"] = unit
    #use search as first action
    raw_search = RAWoutput.do( search_params ) if search_params else None
    #use suggest as second action
    raw_suggest = RAWoutput.do( suggest_params ) if suggest_params else None
    #use show as third action
    raw_show = RAWoutput.do( show_params )   if show_params else None
    # language information
    current_language = translation.get_language()
    request_language = translation.get_language_from_request( request )[:2]
    available_languages = settings.LANGUAGES
    try:
        translation.activate( language )
        language_info = get_language_info( language )
    except:
    	try:
	        translation.activate( request_language )
	        language_info = get_language_info( request_language )
	        language = request_language
    	except:
    		translation.activate( current_language )
	        language_info = get_language_info( current_language )
	        language = current_language
    request.LANGUAGE_CODE = translation.get_language()
    # language direction  properties
    bidi_val = language_info['bidi']
    fields_mapping_en_ar = raw_show["show"]["fields_reverse"]
    fields_mapping_en_en = {}
    for k in fields_mapping_en_ar.keys():
        fields_mapping_en_en[k] = k
    #python 2.7: { k:k for k in fields_mapping_en_ar.keys() }
    bidi_properties = {
		  				 False : {
								 	"val": bidi_val,
								 	"direction": "ltr",
								 	"align": "left",
								 	"align_inverse": "right",
								 	"image_extension": "_en",
								 	"fields": fields_mapping_en_en
	   				 			  },
		  				 True : {
								 	"val": bidi_val,
								 	"direction": "rtl",
								 	"align": "right",
								 	"align_inverse": "left",
								 	"image_extension": "_ar",
								 	"fields": fields_mapping_en_ar
	   				 			  }
					}
    mytemplate = unit + '_search.html'
    return render_to_response( mytemplate ,
                              {
                                'current': {
											'path': request.path,
                                			'request': request.GET.urlencode(),
                                   			'unit': unit,
                                	     	'language': language,
											},
                                "bidi":bidi_properties[bidi_val],
                                "language": language_info,
                                "available": {
											"languages": available_languages,
											"units": available_units,
											},
                                "params": search_params,
                                "results": raw_search,
                                "suggestions": raw_suggest,
                                "info": raw_show
                               }
                              )
