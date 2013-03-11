#
# templatetags/kwacros.py - Support for macros in Django templates
#
# Based on snippet by
# Author: Michal Ludvig <michal@logix.cz>
#         http://www.logix.cz/michal
#
# modified for args and kwargs by Skylar Saveland http://skyl.org
#

"""

Usage example:

0) Save this file as <yourapp>/templatetags/kwacros.py

1) In your template load the library:
    {% load kwacros %}

2) Define a new macro called 'my_macro' that takes two args and a kwarg.
   All will be optional.

    {% kwacro test2args1kwarg arg1 arg2 baz="Default baz" %}
    {% firstof arg1 "default arg1" %}
    {% if arg2 %}{{ arg2 }}{% else %}default arg2{% endif %}
    {{ baz }}
    {% endkwacro %}

3) Use the macro with a string parameters or context variables::

    {% usekwacro test2args1kwarg "foo" "bar" baz="KW" %}
    <br>
    {% usekwacro test2args1kwarg num_pages "bar" %}
    <br>
    {% usekwacro test2args1kwarg %}
    <br>
    {% usekwacro test2args1kwarg "new" "foobar"|join:"," baz="diff kwarg" %}

    renders like

    foo bar KW
    77 bar Default baz
    default arg1 default arg2 Default baz
    new f,o,o,b,a,r diff kwarg

4) Alternatively save your macros in a separate
   file, e.g. "mymacros.html" and load it to the
   current template with:
        {% loadkwacros "mymacros.html" %}
   Then use these loaded macros in {% usekwacro %}
   as described above.

Bear in mind that defined and loaded kwacros are local
to each template file and are not inherited
through {% extends ... %} tags.
"""

from django import template
from django.template import FilterExpression
from django.template.loader import get_template

register = template.Library()


def _setup_macros_dict(parser):
    ## Metadata of each macro are stored in a new attribute
    ## of 'parser' class. That way we can access it later
    ## in the template when processing 'usemacro' tags.
    try:
        ## Only try to access it to eventually trigger an exception
        parser._macros
    except AttributeError:
        parser._macros = {}


class DefineMacroNode(template.Node):
    def __init__(self, name, nodelist, args):

        self.name = name
        self.nodelist = nodelist
        self.args = []
        self.kwargs = {}
        for a in args:
            if "=" not in a:
                self.args.append(a)
            else:
                name, value = a.split("=")
                self.kwargs[name] = value

    def render(self, context):
        ## empty string - {% macro %} tag does no output
        return ''


@register.tag(name="kwacro")
def do_macro(parser, token):
    try:
        args = token.split_contents()
        tag_name, macro_name, args = args[0], args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
            % token.contents.split()[0])
        raise template.TemplateSyntaxError, m
    # TODO: could do some validations here,
    # for now, "blow your head clean off"
    nodelist = parser.parse(('endkwacro', ))
    parser.delete_first_token()

    ## Metadata of each macro are stored in a new attribute
    ## of 'parser' class. That way we can access it later
    ## in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    parser._macros[macro_name] = DefineMacroNode(macro_name, nodelist, args)
    return parser._macros[macro_name]


class LoadMacrosNode(template.Node):
    def render(self, context):
        ## empty string - {% loadmacros %} tag does no output
        return ''


@register.tag(name="loadkwacros")
def do_loadmacros(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
            % token.contents.split()[0])
        raise template.TemplateSyntaxError, m
    if filename[0] in ('"', "'") and filename[-1] == filename[0]:
        filename = filename[1:-1]
    t = get_template(filename)
    macros = t.nodelist.get_nodes_by_type(DefineMacroNode)
    ## Metadata of each macro are stored in a new attribute
    ## of 'parser' class. That way we can access it later
    ## in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    for macro in macros:
        parser._macros[macro.name] = macro
    return LoadMacrosNode()


class UseMacroNode(template.Node):

    def __init__(self, macro, fe_args, fe_kwargs):
        self.macro = macro
        self.fe_args = fe_args
        self.fe_kwargs = fe_kwargs

    def render(self, context):

        for i, arg in enumerate(self.macro.args):
            try:
                fe = self.fe_args[i]
                context[arg] = fe.resolve(context)
            except IndexError:
                context[arg] = ""

        for name, default in self.macro.kwargs.iteritems():
            if name in self.fe_kwargs:
                context[name] = self.fe_kwargs[name].resolve(context)
            else:
                context[name] = FilterExpression(default,
                                                 self.macro.parser
                ).resolve(context)

        return self.macro.nodelist.render(context)


@register.tag(name="usekwacro")
def do_usemacro(parser, token):
    try:
        args = token.split_contents()
        tag_name, macro_name, values = args[0], args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError, m
    try:
        macro = parser._macros[macro_name]
    except (AttributeError, KeyError):
        m = "Macro '%s' is not defined" % macro_name
        raise template.TemplateSyntaxError, m

    fe_kwargs = {}
    fe_args = []

    for val in values:
        if "=" in val:
            # kwarg
            name, value = val.split("=")
            fe_kwargs[name] = FilterExpression(value, parser)
        else:  # arg
            # no validation, go for it ...
            fe_args.append(FilterExpression(val, parser))

    macro.parser = parser
    return UseMacroNode(macro, fe_args, fe_kwargs)
