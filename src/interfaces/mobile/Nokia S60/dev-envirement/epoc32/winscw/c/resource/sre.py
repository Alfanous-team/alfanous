# Portions Copyright (c) 2005 Nokia Corporation 
#
# Secret Labs' Regular Expression Engine
#
# re-compatible interface for the sre matching engine
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# This version of the SRE library can be redistributed under CNRI's
# Python 1.6 license.  For any other use, please contact Secret Labs
# AB (info@pythonware.com).
#
# Portions of this engine have been developed in cooperation with
# CNRI.  Hewlett-Packard provided funding for 1.6 integration and
# other compatibility work.
#

import sys
import sre_compile
import sre_parse

# public symbols
__all__ = [ "match", "search", "sub", "subn", "split", "findall",
    "compile", "purge", "template", "escape", "I", "L", "M", "S", "X",
    "U", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE",
    "UNICODE", "error" ]

__version__ = "2.2.1"

# this module works under 1.5.2 and later.  don't use string methods
#import string

# flags
I = IGNORECASE = sre_compile.SRE_FLAG_IGNORECASE # ignore case
L = LOCALE = sre_compile.SRE_FLAG_LOCALE # assume current 8-bit locale
U = UNICODE = sre_compile.SRE_FLAG_UNICODE # assume unicode locale
M = MULTILINE = sre_compile.SRE_FLAG_MULTILINE # make anchors look for newline
S = DOTALL = sre_compile.SRE_FLAG_DOTALL # make dot match newline
X = VERBOSE = sre_compile.SRE_FLAG_VERBOSE # ignore whitespace and comments

# sre extensions (experimental, don't rely on these)
T = TEMPLATE = sre_compile.SRE_FLAG_TEMPLATE # disable backtracking
DEBUG = sre_compile.SRE_FLAG_DEBUG # dump pattern after compilation

# sre exception
error = sre_compile.error

# --------------------------------------------------------------------
# public interface

def match(pattern, string, flags=0):
    return _compile(pattern, flags).match(string)

def search(pattern, string, flags=0):
    return _compile(pattern, flags).search(string)

def sub(pattern, repl, string, count=0):
    return _compile(pattern, 0).sub(repl, string, count)

def subn(pattern, repl, string, count=0):
    return _compile(pattern, 0).subn(repl, string, count)

def split(pattern, string, maxsplit=0):
    return _compile(pattern, 0).split(string, maxsplit)

def findall(pattern, string):
    return _compile(pattern, 0).findall(string)

if sys.hexversion >= 0x02020000:
    __all__.append("finditer")
    def finditer(pattern, string):
        return _compile(pattern, 0).finditer(string)

def compile(pattern, flags=0):
    return _compile(pattern, flags)

def purge():
    _cache.clear()
    _cache_repl.clear()

def template(pattern, flags=0):
    return _compile(pattern, flags|T)

def escape(pattern):
    s = list(pattern)
    for i in range(len(pattern)):
        c = pattern[i]
        if not ("a" <= c <= "z" or "A" <= c <= "Z" or "0" <= c <= "9"):
            if c == "\000":
                s[i] = "\\000"
            else:
                s[i] = "\\" + c
    return _join(s, pattern)

# --------------------------------------------------------------------
# internals

_cache = {}
_cache_repl = {}

_pattern_type = type(sre_compile.compile("", 0))

_MAXCACHE = 100

def _join(seq, sep):
    # internal: join into string having the same type as sep
    #return string.join(seq, sep[:0])
    return sep[:0].join(seq)

def _compile(*key):
    # internal: compile pattern
    p = _cache.get(key)
    if p is not None:
        return p
    pattern, flags = key
    if type(pattern) is _pattern_type:
        return pattern
    if type(pattern) not in sre_compile.STRING_TYPES:
        raise TypeError, "first argument must be string or compiled pattern"
    try:
        p = sre_compile.compile(pattern, flags)
    except error, v:
        raise error, v # invalid expression
    if len(_cache) >= _MAXCACHE:
        _cache.clear()
    _cache[key] = p
    return p

def _compile_repl(*key):
    # internal: compile replacement pattern
    p = _cache_repl.get(key)
    if p is not None:
        return p
    repl, pattern = key
    try:
        p = sre_parse.parse_template(repl, pattern)
    except error, v:
        raise error, v # invalid expression
    if len(_cache_repl) >= _MAXCACHE:
        _cache_repl.clear()
    _cache_repl[key] = p
    return p

def _expand(pattern, match, template):
    # internal: match.expand implementation hook
    template = sre_parse.parse_template(template, pattern)
    return sre_parse.expand_template(template, match)

def _subx(pattern, template):
    # internal: pattern.sub/subn implementation helper
    template = _compile_repl(template, pattern)
    if not template[0] and len(template[1]) == 1:
        # literal replacement
        return template[1][0]
    def filter(match, template=template):
        return sre_parse.expand_template(template, match)
    return filter

# register myself for pickling

import copy_reg

def _pickle(p):
    return _compile, (p.pattern, p.flags)

copy_reg.pickle(_pattern_type, _pickle, _compile)

# --------------------------------------------------------------------
# experimental stuff (see python-dev discussions for details)

class Scanner:
    def __init__(self, lexicon, flags=0):
        from sre_constants import BRANCH, SUBPATTERN
        self.lexicon = lexicon
        # combine phrases into a compound pattern
        p = []
        s = sre_parse.Pattern()
        s.flags = flags
        for phrase, action in lexicon:
            p.append(sre_parse.SubPattern(s, [
                (SUBPATTERN, (len(p)+1, sre_parse.parse(phrase, flags))),
                ]))
        p = sre_parse.SubPattern(s, [(BRANCH, (None, p))])
        s.groups = len(p)
        self.scanner = sre_compile.compile(p)
    def scan(self, string):
        result = []
        append = result.append
        match = self.scanner.scanner(string).match
        i = 0
        while 1:
            m = match()
            if not m:
                break
            j = m.end()
            if i == j:
                break
            action = self.lexicon[m.lastindex-1][1]
            if callable(action):
                self.match = m
                action = action(self, m.group())
            if action is not None:
                append(action)
            i = j
        return result, string[i:]
