'''
Created on Dec 29, 2012

@author: assem
'''

from django.template import Library

register = Library()




@register.filter
def get_range( value ):
  """  make a range from a number starting of 1 """
  try:
    value = int(value)
  except ValueError:
    value = 1
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
