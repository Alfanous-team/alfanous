from django.template import Library
from collections import OrderedDict as SortedDict

from django.utils.encoding import iri_to_uri

from . import optional_assignment_tag, Params, xget

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


@register.simple_tag
def build_search_link(params, query, page, filter, encode=True):
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
    new_params["query"] = "(" + params["query"] + ") + " + query
  else:
    new_params["query"] = query

  built_params = build_params(new_params)
  if encode:
    return iri_to_uri(built_params)
  else:
    return built_params.replace('&', '%26').replace('<', '%3C').replace('>', '%3E').replace('"', '%22').replace("'",
                                                                                                                '%27')


def build_params(params):
  """ Concatenate the params to build a url GET request

  TODO: use a standard url builder if exists
  TODO: encode the generated url

  """
  get_request = ""
  for k, v in params.items():
    get_request = get_request + unicode(k) + "=" + unicode(v) + "&amp;"
  return get_request[:-5]  # remove the last "&amp;" #5 symbols