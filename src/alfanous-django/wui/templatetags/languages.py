from django.conf import settings
from django.template import Library
from django.utils import translation

register = Library()

ERROR_MESSAGE = (
  "Unknown language code: `%s`. It's not supported by Django, and doesn't exist "
  "settings.EXTRA_LANGUAGES."
)


def my_get_language_info(lang_code):
  try:
    return translation.get_language_info(lang_code)
  except KeyError:
    if lang_code in settings.EXTRA_LANGUAGES:
      return settings.EXTRA_LANGUAGES[lang_code]
    else:
      raise KeyError(ERROR_MESSAGE % lang_code)

@register.filter
def my_language_name(lang_code):
  return my_get_language_info(lang_code)['name']

@register.filter
def my_language_name_local(lang_code):
  return my_get_language_info(lang_code)['name_local']
