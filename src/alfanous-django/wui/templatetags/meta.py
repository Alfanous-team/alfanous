from collections import defaultdict
from django.template import Library
from django.utils.translation import ugettext as _

register = Library()


def get_search_description(params, unit, vocalized):
  return _(
    'Alfanous search results searching in %(unit)s looking for the query %(query)s, the page %(page)s, '
    'the view %(view)s, the script %(script)s%(vocalized)s, and the translation %(translation)s. '
    'The fuzzy search is %(fuzzy)s.'
  ) % defaultdict(str, params, **{
    'unit': unit,
    'vocalized': ' vocalized' if vocalized else '',
    'fuzzy': 'activated' if params.get('fuzzy') else 'deactivated',
  })


@register.simple_tag(name='meta_description')
def description(params, unit, vocalized):
  if 'query' in params:
    return get_search_description(params, unit, vocalized)
  elif unit == 'word':
    return _('Alfanous has the feautre to search in the Quran words, their properties and occurences')
  elif unit == 'translation':
    return _('Alfanous has the feautre to search in the translations of Quran meanings to lot of world languages')
  else:
    return _(
      'Alfanous is a functional, dynamic, comprehensive Qur\'an search engine '
      'that has been effectively designed to carry out simple or advanced '
      'Quranic searches.'
    )
