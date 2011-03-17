# Portions Copyright (c) 2005 Nokia Corporation 
"""A collection of string operations (most are no longer used in Python 1.6).
"""

whitespace = ' \t\n\r\v\f'
lowercase = 'abcdefghijklmnopqrstuvwxyz'
uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
letters = lowercase + uppercase
ascii_lowercase = lowercase
ascii_uppercase = uppercase
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + letters + punctuation + whitespace

_idmap = ''
for i in range(256): _idmap = _idmap + chr(i)
del i

index_error = ValueError
atoi_error = ValueError
atof_error = ValueError
atol_error = ValueError

def lower(s):
    return s.lower()

def upper(s):
    return s.upper()

def swapcase(s):
    return s.swapcase()

def strip(s):
    return s.strip()

def lstrip(s):
    return s.lstrip()

def rstrip(s):
    return s.rstrip()


def split(s, sep=None, maxsplit=-1):
    return s.split(sep, maxsplit)
splitfields = split

def join(words, sep = ' '):
    return sep.join(words)
joinfields = join

def index(s, *args):
    return s.index(*args)

def rindex(s, *args):
    return s.rindex(*args)

def count(s, *args):
    return s.count(*args)

def find(s, *args):
    return s.find(*args)

def rfind(s, *args):
    return s.rfind(*args)

_float = float
_int = int
_long = long
try:
    _StringTypes = (str, unicode)
except NameError:
    _StringTypes = (str,)

def atof(s):
    return _float(s)


def atoi(s , base=10):
    return _int(s, base)


def atol(s, base=10):
    return _long(s, base)


def ljust(s, width):
    return s.ljust(width)

def rjust(s, width):
    return s.rjust(width)

def center(s, width):
    return s.center(width)

def zfill(x, width):
    if not isinstance(x, _StringTypes):
        x = repr(x)
    return x.zfill(width)

def expandtabs(s, tabsize=8):
    return s.expandtabs(tabsize)

def translate(s, table, deletions=""):
    if deletions:
        return s.translate(table, deletions)
    else:
        return s.translate(table + s[:0])

def capitalize(s):
    return s.capitalize()

def capwords(s, sep=None):
    return join(map(capitalize, s.split(sep)), sep or ' ')

_idmapL = None
def maketrans(fromstr, tostr):
    if len(fromstr) != len(tostr):
        raise ValueError, "maketrans arguments must have same length"
    global _idmapL
    if not _idmapL:
        _idmapL = map(None, _idmap)
    L = _idmapL[:]
    fromstr = map(ord, fromstr)
    for i in range(len(fromstr)):
        L[fromstr[i]] = tostr[i]
    return join(L, "")

def replace(s, old, new, maxsplit=-1):
    return s.replace(old, new, maxsplit)

try:
    from strop import maketrans, lowercase, uppercase, whitespace
    letters = lowercase + uppercase
except ImportError:
    pass                                          # Use the original versions
