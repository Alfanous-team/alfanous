# -*- coding=utf-8 -*-

import re
from arabic_const import *


HARAKAT_pat = re.compile(ur"[" + u"".join([FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN, SHADDA]) + u"]")
HAMZAT_pat = re.compile(ur"[" + u"".join([WAW_HAMZA, YEH_HAMZA]) + u"]");
ALEFAT_pat = re.compile(ur"[" + u"".join([ALEF_MADDA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, HAMZA_ABOVE, HAMZA_BELOW]) + u"]");
LAMALEFAT_pat = re.compile(ur"[" + u"".join([LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE]) + u"]");

#--------------------------------------
def strip_tashkeel(w):
	"strip vowel from a word and return a result word"
	return HARAKAT_pat.sub('', w)

#strip tatweel from a word and return a result word
#--------------------------------------
def strip_tatweel(w):
	"strip tatweel from a word and return a result word"
	return re.sub(ur'[%s]' % TATWEEL, 	'', w)
	
#--------------------------------------
def strip_shadda(w):
	"strip tatweel from a word and return a result word"
	return re.sub(ur'[%s]' % SHADDA, 	'', w)
#--------------------------------------
def normalize_uthmani_symbols(w):
    "normalize specail letters on uthmani script, and strip extra symbols "
    w = re.sub(ur'[%s]' % MINI_ALEF+SMALL_WAW+SMALL_YEH, 	'', w)
    w = re.sub(ur'[%s]' % ALEF_WASLA, 	ALEF, w)
    return w

#--------------------------------------
def normalize_hamza(w):
	"strip vowel from a word and return a result word"
	w = ALEFAT_pat.sub(ALEF, w)
	return HAMZAT_pat.sub(HAMZA, w)


#--------------------------------------
def normalize_lamalef(w):
	"strip vowel from a word and return a result word"
	return LAMALEFAT_pat.sub(u'%s%s' % (LAM, ALEF), w)

#--------------------------------------
def normalize_spellerrors(w):
	"strip vowel from a word and return a result word"
	w = re.sub(ur'[%s]' % TEH_MARBUTA, 	HEH, w)
	return re.sub(ur'[%s]' % ALEF_MAKSURA, 	YEH, w)


def normalize_text(text):
	"""return normalized text
	
	Normalisation steps:
	*	strip diacritics
	*   strip tatweel
	*   normalize lam-alef
	*   normalize hamza
	* 	normalize spellerrors
	  
	"""
	text = strip_tashkeel(text)
	text = strip_tatweel(text)
	text = normalize_lamalef(text)
	text = normalize_hamza(text)
	text = normalize_spellerrors(text)
	return text















#--------------------------------------
def replace_pos (word, rep, pos):
	return word[0:pos] + rep + word[pos + 1:];
#--------------------------------------
def chomp(s):
	if ( s.endswith( '\n' ) ):
		return s[:-1]
	else:
		return s
#--------------------------------------
# readfile : extract text as à string from a file
#--------------------------------------
def readfile (filename):
	try:
		fl = open(filename);
	except :
		print " Error :No such file or directory: %s" % filename
		return None;
	line = fl.readline().decode("utf8");
	text = u""
	while line :
		text = " ".join([text, chomp(line)])
		line = fl.readline().decode("utf");
	#print text.encode("utf8");
	return text;
