import re

from .constants import *

__all__ = ['normalize_uthmani_symbols','normalize_hamza','normalize_lamalef',
           'normalize_spellerrors','normalize_text']

from .strip_functions import stripTashkeel, stripTatweel

_ALEFAT = (ALEF_MADDA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, HAMZA_ABOVE, HAMZA_BELOW)
_HAMZAT = (WAW_HAMZA, YEH_HAMZA)
_LAMALEFAT = (LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE)

# Regex matching all Quranic annotation marks in the U+06D6–U+06ED block.
# These are Uthmanic-script-specific marks (verse markers, small letters, stops)
# that should be stripped when producing a normalised standard-Arabic form.
_UTHMANI_ANNOTATION_RE = re.compile(r'[\u06D6-\u06ED]')

def normalize_uthmani_symbols(w):
    """Remove or replace Uthmanic-script symbols so the result matches plain Arabic.

    Key mappings:
    - MINI_ALEF (U+0670, superscript alef): replaced with ALEF so that words
      like سَمَّٰكُمُ normalize to سماكم matching standard user input.
    - ALEF_MADDA (U+0622, آ): replaced with ALEF so that السَّمَآءِ
      normalizes to السماء.
    - ALEF_WASLA (U+0671): replaced with ALEF.
    - Full U+06D6–U+06ED range (Quranic annotation marks such as small high
      letters, stops, and verse markers): stripped entirely so that no
      Uthmanic mark leaks into normalised or word_standard fields.
    """
    w = w.replace(MINI_ALEF, ALEF)\
         .replace(ALEF_MADDA, ALEF)\
         .replace(ALEF_WASLA, ALEF)
    return _UTHMANI_ANNOTATION_RE.sub('', w)

#--------------------------------------
def normalize_hamza(w):
    s = ''
    for letter in w:
        if letter in _ALEFAT: s += ALEF
        elif letter in _HAMZAT: s += HAMZA
        else: s += letter
    
    return s


#--------------------------------------
def normalize_lamalef(w):
    s = ''
    
    for letter in w:
        if letter in _LAMALEFAT: s += (LAM + ALEF)
        else: s += letter
    
    return s

#--------------------------------------
def normalize_spellerrors(w):
    '''
    strip vowel from a word and return a result word
    
    >>> normalize_spellerrors('')
    u''
    >>> normalize_spellerrors(TEH_MARBUTA+ALEF_MAKSURA+ALEF+BEH+TEH_MARBUTA+TEH+ALEF_MAKSURA) == (HEH+YEH+ALEF+BEH+HEH+TEH+YEH)
    True
    '''
    return w.replace(TEH_MARBUTA, HEH).replace(ALEF_MAKSURA, YEH)

def normalize_text(text):
    '''
    return normalized text
    
    Normalisation steps:
    *   strip diacritics
    *   strip tatweel
    *   normalize lam-alef
    *   normalize hamza
    *   normalize spellerrors
    
    >>> normalize_text('')
    u''
    '''
    text = stripTashkeel(text)
    text = stripTatweel(text)
    text = normalize_lamalef(text)
    text = normalize_hamza(text)
    text = normalize_spellerrors(text)
    
    return text

def normalizeLigature( text ):
    """Normalize Lam Alef ligatures into two letters (LAM and ALEF), and Tand return a result text.
    Some systems present lamAlef ligature as a single letter, this function convert it into two letters,
    The converted letters into  LAM and ALEF are :
        - LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE

    @param text: arabic text.
    @type text: unicode.
    @return: return a converted text.
    @rtype: unicode.

    >>> normalizeLigature( '' )
    ''
    >>> normalizeLigature( 'abc' )
    'abc'
    >>> normalizeLigature( 'a' + LAM_ALEF + 'b' + LAM_ALEF_MADDA_ABOVE ) == ('a' + LAM + ALEF + 'b' + LAM + ALEF)
    True
    >>> normalizeLigature( 'a' + LAM_ALEF + 'bc' + LAM_ALEF_MADDA_ABOVE ) == ('a' + LAM + ALEF + 'bc' + LAM + ALEF)
    True
    >>> normalizeLigature( ALEF + LAM_ALEF + BEH + TEH + LAM_ALEF_MADDA_ABOVE ) == (ALEF + LAM + ALEF + BEH + TEH + LAM + ALEF)
    True
    """
    s = ''

    for letter in text:
        s += (LAM + ALEF) if letter in LIGUATURES else letter

    return s
