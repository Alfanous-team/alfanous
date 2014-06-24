from collections import defaultdict
from django.template import Library
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
import re
from wui.templatetags import xget
from alfanous.Support.PyArabic.araby_constants import TASHKEEL

register = Library()

TITLE_SUFFIX = {
  'aya': _("Quran Ayah Search"),
  'translation': _("Quran Translation Search"),
  'word': _("Quran Word Search"),
}

TITLE_CLEANER = re.compile('[^\w%s_]+' % ''.join(TASHKEEL), re.UNICODE)

def query_for_title(query):
  return TITLE_CLEANER.sub(' ', query).encode('UTF-8')

@register.simple_tag(takes_context=True)
def page_title(context):
  params = xget(context, 'params')
  unit = xget(context, 'current.unit')

  parts = []
  if 'query' in params:
    parts.extend((query_for_title(params['query']), '-'))

  parts.extend((
    TITLE_SUFFIX[unit].encode('UTF-8'),
    '-',
    _("Alfanous").encode('UTF-8')
  ))
  return escape(' '.join(parts))


def get_search_description(params, unit):
  return _(
    '"Alfanous search results searching in %(unit)s looking for the query %(query)s, the page %(page)s, '
    'the view %(view)s, the script %(script)s%(vocalized)s, and the translation %(translation)s. '
    'The fuzzy search is %(fuzzy)s.'
  ) % defaultdict(str, params, **{
    'unit': unit,
    'vocalized': ' vocalized' if params.get('vocalized') else '',
    'fuzzy': 'activated' if params.get('fuzzy') else 'deactivated',
  })

@register.simple_tag(takes_context=True)
def meta_description(context):
  params = xget(context, 'params')
  unit = xget(context, 'current.unit')
  if 'query' in params:
    description = get_search_description(params, unit)
  elif unit == 'word':
    description = _('Alfanous has the feautre to search in the Quran words, their properties and occurences')
  elif unit == 'translation':
    description = _('Alfanous has the feautre to search in the translations of Quran meanings to lot of world languages')
  else:
    description = _(
      'Alfanous is a functional, dynamic, comprehensive Qur\'an search engine '
      'that has been effectively designed to carry out simple or advanced '
      'Quranic searches.'
    )
  return escape(description)

# Open Graph tags
# https://developers.facebook.com/docs/opengraph/howtos/maximizing-distribution-media-content

# To check how FB is seeing our website:
# https://developers.facebook.com/tools/debug/og/object?q=www.alfanous.org

@register.simple_tag(takes_context=True)
def og_title(context):
  params = xget(context, 'params')
  unit = xget(context, 'current.unit')

  parts = []
  if 'query' in params:
    parts.extend((query_for_title(params['query']), '-'))
  parts.append(TITLE_SUFFIX[unit].encode('UTF-8'))
  return ' '.join(parts)

@register.simple_tag(takes_context=True)
def og_description(context):
  return meta_description(context)
