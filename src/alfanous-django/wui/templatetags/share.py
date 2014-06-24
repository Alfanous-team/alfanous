import urllib
from django.template import Library
from django.utils.translation import ugettext as _
from wui.templatetags import Params, xget

register = Library()

SHARE_PATTERNS = {
  'twitter': 'https://twitter.com/intent/tweet?text=%(title)s&url=%(url)s',
  'facebook': 'http://www.facebook.com/sharer/sharer.php?s=100&p[url]=%(url)s&p[title]=%(title)s',
  'gplus': 'https://plus.google.com/share?url=%(url)s',
  'linkedin': 'http://www.linkedin.com/shareArticle?url=%(url)s&title=%(title)s&summary=%(summary)s',
}


def encodeURLComponent(text):
  return urllib.quote(text.encode('UTF-8'))

def aya_title(result):
  return '%s - (%s,%s)' % (
    xget(result, 'aya.text_no_highlight'),
    xget(result, 'identifier.sura_arabic_name'),
    xget(result, 'aya.id'),
  )

def translation_title(result):
  return '%s - %s (%s %s)' % (
    xget(result, 'text'),
    _('Interpretation of'),
    xget(result, 'aya.sura_name'),
    xget(result, 'aya.aya_id'),
  )

title = {
  'aya': aya_title,
  'translation': translation_title,
  'word': aya_title,
}

def linkedin_title(result):
  return '%s %s' % (
    xget(result, 'identifier.sura_name', 'aya.sura_name'),
    xget(result, 'aya.id', 'aya.aya_id'),
  )

def get_share_url(path, params):
  return 'http://www.alfanous.org%s?%s' % (
    path,
    Params(params, **{'page': 1}),
  )

@register.simple_tag(takes_context=True)
def twitter_share(context, result, path, params):
  unit = xget(context, 'current.unit')
  return SHARE_PATTERNS['twitter'] % {
    'title': encodeURLComponent(title[unit](result)),
    'url': encodeURLComponent(get_share_url(path, params)),
  }

@register.simple_tag(takes_context=True)
def facebook_share(context, result, path, params):
  unit = xget(context, 'current.unit')
  return SHARE_PATTERNS['facebook'] % {
    # TODO: We should use OG tags for share title & images.
    'title': encodeURLComponent(title[unit](result)),
    'url': encodeURLComponent(get_share_url(path, params)),
  }

@register.simple_tag(takes_context=True)
def gplus_share(context, result, path, params):
  return SHARE_PATTERNS['gplus'] % {
    'url': encodeURLComponent(get_share_url(path, params)),
  }

@register.simple_tag(takes_context=True)
def linkedin_share(context, result, path, params):
  unit = xget(context, 'current.unit')
  return SHARE_PATTERNS['linkedin'] % {
    'title': encodeURLComponent(linkedin_title(result)),
    'summary': encodeURLComponent(title[unit](result)),
    'url': encodeURLComponent(get_share_url(path, params)),
  }
