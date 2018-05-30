'''
Created on Dec 29, 2012

@author: assem
'''

from django.template import Library,Node
from django.template.defaultfilters import stringfilter

register = Library()


@register.filter
def get_range(value):
    """  make a range from a number starting of 1 """
    try:
        value = int(value)
    except ValueError:
        value = 1
    return range(1, value + 1)


@register.filter
def space_split(string):
    """ split a string counting on spaces """
    return string.split()


@register.filter
def string_replace(string, args):
    """ replace all occurrences of oldword (arg_list[0]) in string by newword (arg_list[1])   """
    arg_list = [arg.strip() for arg in args.split(',')]
    oldword = arg_list[0]
    newword = arg_list[1]
    return string.replace(oldword, newword)


@register.tag
def lineless(parser, token):
    nodelist = parser.parse(('endlineless',))
    parser.delete_first_token()
    return LinelessNode(nodelist)


class LinelessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        input_str = self.nodelist.render(context)
        output_str = ''
        for line in input_str.splitlines():
            if line.strip():
                output_str = '\n'.join((output_str, line))
        return output_str
