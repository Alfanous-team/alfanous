'''
Created on Dec 29, 2012

@author: assem
'''

from django.template import Library


register = Library()


@register.filter
def get_range( value ):
	"""  make a range from a number starting of 1 """
	return range( 1, value + 1 )


@register.filter
def space_split( str ):
	""" split a string counting on spaces """
	return str.split()


@register.filter
def string_replace( string, args ):
    """ replace all occurrences of oldword (arg_list[0]) in string by newword (arg_list[1])   """
    arg_list = [arg.strip() for arg in args.split( ',' )]
    oldword = arg_list[0]
    newword = arg_list[1]
    return string.replace( oldword, newword )


@register.simple_tag
def build_search_link( params, query, page, filter ):
    """ build a search link based on a new query 
    
    usage: {% build_search_link params query filter %}link</a>
    
    """
    # create a mutuable params object
    new_params = {}
    for k, v in params.items():
    	new_params[k] = v
    # update params
    new_params["page"] = page
    if filter == "True" and params["query"] != query:
    	new_params["query"] = "(" + params["query"] + ") + " + query;
    else:
    	new_params["query"] = query;

    return build_params( new_params )


def build_params( params ):
	""" Concatenate the params to build a url GET request
	
	TODO: use a standard url builder if exists
	TODO: encode the generated url

	"""
	get_request = ""
	for k, v in params.items():
		get_request = get_request + unicode( k ) + "=" + unicode( v ) + "&amp;"
	return get_request[:-5] #remove the last "&amp;" #5 symbols
