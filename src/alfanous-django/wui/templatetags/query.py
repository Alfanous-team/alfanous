from django.template import Library
from django.utils.datastructures import SortedDict
from wui.templatetags import Params, xget, optional_assignment_tag

Library.optional_assignment_tag = optional_assignment_tag
register = Library()

def quotes(s):
  return '"%s"' % s

@register.optional_assignment_tag(takes_context=True)
def custom_query(context, query, page, filter):
  """
  Build a custom search query link.
  usage: <a href="?{% custom_query query filter %}">link</a>
  """
  params = context['params']

  # create a copy so that we don't mutate the original params
  new_params = params.copy()

  # update params
  new_params["page"] = page
  if filter == "True" and params["query"] != query:
    new_params["query"] = "(%s) + %s" % (params["query"], query)
  else:
    new_params["query"] = query
  return Params(new_params)


def build_query(params, colon_separated_query, separator=' + '):
  query = separator.join(
    '%s:%s' % (k, v) for k, v in colon_separated_query.iteritems()
  )
  return Params(params, **{
    'page': 1,
    'query': query
  })

@register.optional_assignment_tag(takes_context=True)
def aya_query(context, result_or_aya):
  fields = xget(context, 'bidi.fields')
  return build_query(context['params'], SortedDict([
    (fields['sura'], quotes(xget(result_or_aya, 'identifier.sura_name', 'sura'))),
    (fields['aya_id'], xget(result_or_aya, 'aya.id', 'aya.aya_id', 'id')),
  ]))

@register.optional_assignment_tag(takes_context=True)
def ar_aya_query(context, result_content):
  fields = xget(context, 'bidi.fields')
  return build_query(context['params'], SortedDict([
    (fields['sura_arabic'], quotes(xget(result_content, 'identifier.sura_arabic_name'))),
    (fields['aya_id'], xget(result_content, 'aya.id')),
  ]))

@register.optional_assignment_tag(takes_context=True)
def simple_query(context, separator, **kwargs):
  query = SortedDict(kwargs.iteritems())
  return build_query(context['params'], query, separator=separator)
