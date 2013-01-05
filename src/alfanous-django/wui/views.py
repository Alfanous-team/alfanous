# Create your views here.

"""

TODO make a fields English-Arabic mapping based on the "bidi" value to be used in localization

"""
import json
import datetime
from sys import path


from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.translation import pgettext_lazy # for ambiguities
from django.utils.translation import get_language_info

path.append( "alfanous.egg/alfanous" )
from alfanous.Outputs import Raw


# load the search engine, use default paths
RAWoutput = Raw()


def jos2( request ):
    """ JSON Output System II """

    if len( request.GET ):
        response_data = RAWoutput.do( request.GET )
        response = HttpResponse( json.dumps( response_data ), mimetype = "application/json" )
        response['charset'] = 'utf-8'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'

    else:
        response_data = RAWoutput._information["json_output_system_note"]
        response = HttpResponse( response_data )

    return response


def results( request ):
    """    """
    show_params = { "action":"show", "query": "all" }

    if request.GET.has_key( "query" ) and not ( request.GET.has_key( "action" ) and not request.GET["action"] == "search" ):
        search_params = request.GET
        suggest_params = { "action":"suggest", "query": request.GET["query"] }
    elif request.GET.has_key( "search" ):
    	## back-compatibility of links:
    	# if it's a classic API style, wrap it to the new API style
        search_params = { "action": "search",
                        "query": request.GET["search"],
                        "page": request.GET["page"] if request.GET.has_key( "page" ) else 1,
                        "sortedby": request.GET["sortedby"] if request.GET.has_key( "sortedby" ) else "relevance"
                        }
        suggest_params = { 
						"action":"suggest",
                        "query": request.GET["search"]
                                        }
    else:
        search_params = {}
        suggest_params = {}

    #use search as first action
    raw_search = RAWoutput.do( search_params ) if search_params else None
    #use suggest as second action
    raw_suggest = RAWoutput.do( suggest_params ) if suggest_params else None
    #use show as third action
    raw_show = RAWoutput.do( show_params )   if show_params else None


    # language information
    language = translation.get_language_from_request( request )
    language_info = get_language_info( language )

    #print  language ,language_info['name'], language_info['name_local'], language_info['bidi']


    translation.activate( language )
    request.LANGUAGE_CODE = translation.get_language()


    return render_to_response( 'wui.html',
                              {
                                'current_path': request.get_full_path(),
                                "bidi": "rtl" if language_info['bidi']
                                              else "ltr",
                                "language_local_name": language_info['name_local'],
                                "align": "right" if language_info['bidi']
                                              else "left",
                                "align_inverse": "left" if language_info['bidi']
                                              else "right",
                                "image_extension": "_ar" if language_info['bidi']
                                              else "_en",

                                "params": search_params,
                                "results": raw_search,
                                "suggestions": raw_suggest,
                                "info": raw_show

                               }
                              )
