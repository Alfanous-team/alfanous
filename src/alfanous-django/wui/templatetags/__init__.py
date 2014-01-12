from inspect import getargspec
import urllib
from django.template.base import TagHelperNode, TemplateSyntaxError, parse_bits, generic_tag_compiler


class Params(dict):
  def __str__(self):
    return urllib.urlencode(dict(
      (k.encode('UTF-8'), unicode(v).encode('UTF-8')) for k, v in self.iteritems()
    ))

def xget(map, *keys):
  """
  Smart dictionary access:
    d = {'a':2, 'b':{'c':3},'d':{'e':{'f':10}}}

    xget(d, 'a') => 2
    xget(d, 'b.c') => 3
    xget(d, 'a.b') => None
    xget(d, 'd.e.f') => 10
    xget(d, 'd.e') => {'f': 10}

    Fallback keys:
    xget(d, 'a.b', 'b') => {'c': 3}
  """
  for k in keys:
    k_parts = k.split('.')
    val = map
    for ii, part in enumerate(k_parts):
      try:
        if part in val:
          val = val[part]
          if ii == len(k_parts) - 1:
            return val
        else: break
      except TypeError:
        # TypeError will be raised if `val` is not iterable
        break
  return None


def optional_assignment_tag(register, func=None, takes_context=None, name=None):
  def dec(func):
    params, varargs, varkw, defaults = getargspec(func)

    class SimpleNode(TagHelperNode):
      def render(self, context):
        resolved_args, resolved_kwargs = self.get_resolved_arguments(context)
        return func(*resolved_args, **resolved_kwargs)

    class AssignmentNode(TagHelperNode):
      def __init__(self, takes_context, args, kwargs, target_var):
        super(AssignmentNode, self).__init__(takes_context, args, kwargs)
        self.target_var = target_var

      def render(self, context):
        resolved_args, resolved_kwargs = self.get_resolved_arguments(context)
        context[self.target_var] = func(*resolved_args, **resolved_kwargs)
        return ''

    function_name = (name or getattr(func, '_decorated_function', func).__name__)

    def compile_func(parser, token):
      bits = token.split_contents()[1:]

      # When there is an "as"
      if len(bits) >= 2 and bits[-2] == 'as':
        target_var = bits[-1]
        bits = bits[:-2]
        args, kwargs = parse_bits(
          parser, bits, params, varargs, varkw, defaults, takes_context, function_name
        )
        return AssignmentNode(takes_context, args, kwargs, target_var)
      else:
        args, kwargs = parse_bits(
          parser, bits, params, varargs, varkw, defaults, takes_context, function_name
        )
        return SimpleNode(takes_context, args, kwargs)

    compile_func.__doc__ = func.__doc__
    register.tag(function_name, compile_func)
    return func

  if func is None:
    # @register.optional_assignment_tag(...)
    return dec
  elif callable(func):
    # @register.optional_assignment_tag
    return dec(func)
  else:
    raise TemplateSyntaxError("Invalid arguments provided to optional_assignment_tag")
