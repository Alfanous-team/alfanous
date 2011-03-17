# Portions Copyright (c) 2005 Nokia Corporation 
# A stripped-down version

__all__ = ["urlsplit"]

# A classification of schemes ('' means apply by default)
uses_netloc = ['ftp', 'http', 'gopher', 'nntp', 'telnet', 'wais',
               'file',
               'https', 'shttp', 'snews',
               'prospero', 'rtsp', 'rtspu', '']
uses_query = ['http', 'wais',
              'https', 'shttp',
              'gopher', 'rtsp', 'rtspu', 'sip',
              '']
uses_fragment = ['ftp', 'hdl', 'http', 'gopher', 'news', 'nntp', 'wais',
                 'https', 'shttp', 'snews',
                 'file', 'prospero', '']

# Characters valid in scheme names
scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

MAX_CACHE_SIZE = 20
_parse_cache = {}

def clear_cache():
    global _parse_cache
    _parse_cache = {}

def urlparse(url, scheme='', allow_fragments=1):
    """Parse a URL into 6 components:
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    Return a 6-tuple: (scheme, netloc, path, params, query, fragment).
    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes."""
    tuple = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = tuple
    if scheme in uses_params and ';' in url:
        url, params = _splitparams(url)
    else:
        params = ''
    return scheme, netloc, url, params, query, fragment

def _splitparams(url):
    if '/'  in url:
        i = url.find(';', url.rfind('/'))
        if i < 0:
            return url, ''
    else:
        i = url.find(';')
    return url[:i], url[i+1:]

def urlsplit(url, scheme='', allow_fragments=1):
    key = url, scheme, allow_fragments
    cached = _parse_cache.get(key, None)
    if cached:
        return cached
    if len(_parse_cache) >= MAX_CACHE_SIZE: # avoid runaway growth
        clear_cache()
    netloc = query = fragment = ''
    i = url.find(':')
    if i > 0:
        if url[:i] == 'http': # optimize the common case
            scheme = url[:i].lower()
            url = url[i+1:]
            if url[:2] == '//':
                i = url.find('/', 2)
                if i < 0:
                    i = url.find('#')
                    if i < 0:
                        i = len(url)
                netloc = url[2:i]
                url = url[i:]
            if allow_fragments and '#' in url:
                url, fragment = url.split('#', 1)
            if '?' in url:
                url, query = url.split('?', 1)
            tuple = scheme, netloc, url, query, fragment
            _parse_cache[key] = tuple
            return tuple
        for c in url[:i]:
            if c not in scheme_chars:
                break
        else:
            scheme, url = url[:i].lower(), url[i+1:]
    if scheme in uses_netloc:
        if url[:2] == '//':
            i = url.find('/', 2)
            if i < 0:
                i = len(url)
            netloc, url = url[2:i], url[i:]
    if allow_fragments and scheme in uses_fragment and '#' in url:
        url, fragment = url.split('#', 1)
    if scheme in uses_query and '?' in url:
        url, query = url.split('?', 1)
    tuple = scheme, netloc, url, query, fragment
    _parse_cache[key] = tuple
    return tuple

if __name__ == '__main__':
    pass
