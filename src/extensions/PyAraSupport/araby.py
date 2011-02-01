#!/usr/bin/python
# -*- coding=utf-8 -*-

# ------------
# Description:
# ------------
#
# Arabic codes
#
# (C) Copyright 2010, Taha Zerrouki
# -----------------
#  $Date: 2010/03/01
#  $Author: Taha Zerrouki$
#  $Revision: 0.1 $
#  This program is written under the Gnu Public License.
#
"""
Arabic module

@todo: normalize_spellerrors,normalize_hamza,normalize_shaping
@todo: statistics calculator

"""
import re
class araby:
    """
    the arabic chars contains all arabic letters, a sub class of unicode,
    """

    COMMA            = u'\u060C'
    SEMICOLON        = u'\u061B'
    QUESTION         = u'\u061F'
    HAMZA            = u'\u0621'
    ALEF_MADDA       = u'\u0622'
    ALEF_HAMZA_ABOVE = u'\u0623'
    WAW_HAMZA        = u'\u0624'
    ALEF_HAMZA_BELOW = u'\u0625'
    YEH_HAMZA        = u'\u0626'
    ALEF             = u'\u0627'
    BEH              = u'\u0628'
    TEH_MARBUTA      = u'\u0629'
    TEH              = u'\u062a'
    THEH             = u'\u062b'
    JEEM             = u'\u062c'
    HAH              = u'\u062d'
    KHAH             = u'\u062e'
    DAL              = u'\u062f'
    THAL             = u'\u0630'
    REH              = u'\u0631'
    ZAIN             = u'\u0632'
    SEEN             = u'\u0633'
    SHEEN            = u'\u0634'
    SAD              = u'\u0635'
    DAD              = u'\u0636'
    TAH              = u'\u0637'
    ZAH              = u'\u0638'
    AIN              = u'\u0639'
    GHAIN            = u'\u063a'
    TATWEEL          = u'\u0640'
    FEH              = u'\u0641'
    QAF              = u'\u0642'
    KAF              = u'\u0643'
    LAM              = u'\u0644'
    MEEM             = u'\u0645'
    NOON             = u'\u0646'
    HEH              = u'\u0647'
    WAW              = u'\u0648'
    ALEF_MAKSURA     = u'\u0649'
    YEH              = u'\u064a'
    MADDA_ABOVE      = u'\u0653'
    HAMZA_ABOVE      = u'\u0654'
    HAMZA_BELOW      = u'\u0655'
    ZERO             = u'\u0660'
    ONE              = u'\u0661'
    TWO              = u'\u0662'
    THREE            = u'\u0663'
    FOUR             = u'\u0664'
    FIVE             = u'\u0665'
    SIX              = u'\u0666'
    SEVEN            = u'\u0667'
    EIGHT            = u'\u0668'
    NINE             = u'\u0669'
    PERCENT          = u'\u066a'
    DECIMAL          = u'\u066b'
    THOUSANDS        = u'\u066c'
    STAR             = u'\u066d'
    MINI_ALEF        = u'\u0670'
    ALEF_WASLA       = u'\u0671'
    FULL_STOP        = u'\u06d4'
    BYTE_ORDER_MARK  = u'\ufeff'

    # Diacritics
    FATHATAN         = u'\u064b'
    DAMMATAN         = u'\u064c'
    KASRATAN         = u'\u064d'
    FATHA            = u'\u064e'
    DAMMA            = u'\u064f'
    KASRA            = u'\u0650'
    SHADDA           = u'\u0651'
    SUKUN            = u'\u0652'

    # Small Letters
    SMALL_ALEF      =u"\u0670"
    SMALL_WAW       =u"\u06E5"
    SMALL_YEH       =u"\u06E6"
    #Ligatures
    LAM_ALEF                    =u'\ufefb'
    LAM_ALEF_HAMZA_ABOVE        =u'\ufef7'
    LAM_ALEF_HAMZA_BELOW        =u'\ufef9'
    LAM_ALEF_MADDA_ABOVE        =u'\ufef5'
    simple_LAM_ALEF             =u'\u0644\u0627'
    simple_LAM_ALEF_HAMZA_ABOVE =u'\u0644\u0623'
    simple_LAM_ALEF_HAMZA_BELOW =u'\u0644\u0625'
    simple_LAM_ALEF_MADDA_ABOVE =u'\u0644\u0622'
    # groups
    LETTERS=u''.join([
            ALEF , BEH , TEH  , TEH_MARBUTA  , THEH  , JEEM  , HAH , KHAH ,
            DAL   , THAL  , REH   , ZAIN  , SEEN   , SHEEN  , SAD , DAD , TAH   , ZAH   ,
            AIN   , GHAIN   , FEH  , QAF , KAF , LAM , MEEM , NOON, HEH , WAW, YEH  ,
            HAMZA  ,  ALEF_MADDA , ALEF_HAMZA_ABOVE , WAW_HAMZA   , ALEF_HAMZA_BELOW  , YEH_HAMZA  ,
            ])

    TASHKEEL =(FATHATAN, DAMMATAN, KASRATAN,
                FATHA,DAMMA,KASRA,
                SUKUN,
                SHADDA);
    HARAKAT =(  FATHATAN,   DAMMATAN,   KASRATAN,
                FATHA,  DAMMA,  KASRA,
                SUKUN
                );
    SHORTHARAKAT =( FATHA,  DAMMA,  KASRA, SUKUN);

    TANWIN =(FATHATAN,  DAMMATAN,   KASRATAN);


    LIGUATURES=(
                LAM_ALEF,
                LAM_ALEF_HAMZA_ABOVE,
                LAM_ALEF_HAMZA_BELOW,
                LAM_ALEF_MADDA_ABOVE,
                );
    HAMZAT=(
                HAMZA,
                WAW_HAMZA,
                YEH_HAMZA,
                HAMZA_ABOVE,
                HAMZA_BELOW,
                ALEF_HAMZA_BELOW,
                ALEF_HAMZA_ABOVE,
                );
    ALEFAT=(
                ALEF,
                ALEF_MADDA,
                ALEF_HAMZA_ABOVE,
                ALEF_HAMZA_BELOW,
                ALEF_WASLA,
                ALEF_MAKSURA,
                SMALL_ALEF,

            );
    WEAK   = ( ALEF, WAW, YEH, ALEF_MAKSURA);
    YEHLIKE= ( YEH,  YEH_HAMZA,  ALEF_MAKSURA,   SMALL_YEH  );

    WAWLIKE     =   ( WAW,  WAW_HAMZA,  SMALL_WAW );
    TEHLIKE     =   ( TEH,  TEH_MARBUTA );

    SMALL   =( SMALL_ALEF, SMALL_WAW, SMALL_YEH)
    MOON =(HAMZA            ,
            ALEF_MADDA       ,
            ALEF_HAMZA_ABOVE ,
            ALEF_HAMZA_BELOW ,
            ALEF             ,
            BEH              ,
            JEEM             ,
            HAH              ,
            KHAH             ,
            AIN              ,
            GHAIN            ,
            FEH              ,
            QAF              ,
            KAF              ,
            MEEM             ,
            HEH              ,
            WAW              ,
            YEH
        );
    SUN=(
            TEH              ,
            THEH             ,
            DAL              ,
            THAL             ,
            REH              ,
            ZAIN             ,
            SEEN             ,
            SHEEN            ,
            SAD              ,
            DAD              ,
            TAH              ,
            ZAH              ,
            LAM              ,
            NOON             ,
        );
    AlphabeticOrder={
                    ALEF             : 1,
                    BEH              : 2,
                    TEH              : 3,
                    TEH_MARBUTA      : 3,
                    THEH             : 4,
                    JEEM             : 5,
                    HAH              : 6,
                    KHAH             : 7,
                    DAL              : 8,
                    THAL             : 9,
                    REH              : 10,
                    ZAIN             : 11,
                    SEEN             : 12,
                    SHEEN            : 13,
                    SAD              : 14,
                    DAD              : 15,
                    TAH              : 16,
                    ZAH              : 17,
                    AIN              : 18,
                    GHAIN            : 19,
                    FEH              : 20,
                    QAF              : 21,
                    KAF              : 22,
                    LAM              : 23,
                    MEEM             : 24,
                    NOON             : 25,
                    HEH              : 26,
                    WAW              : 27,
                    YEH              : 28,
                    HAMZA            : 29,

                    ALEF_MADDA       : 29,
                    ALEF_HAMZA_ABOVE : 29,
                    WAW_HAMZA        : 29,
                    ALEF_HAMZA_BELOW : 29,
                    YEH_HAMZA        : 29,
                    }
    NAMES ={
                    ALEF             :  u"ألف",
                    BEH              : u"باء",
                    TEH              : u'تاء' ,
                    TEH_MARBUTA      : u'تاء مربوطة' ,
                    THEH             : u'ثاء' ,
                    JEEM             : u'جيم' ,
                    HAH              : u'حاء' ,
                    KHAH             : u'خاء' ,
                    DAL              : u'دال' ,
                    THAL             : u'ذال' ,
                    REH              : u'راء' ,
                    ZAIN             : u'زاي' ,
                    SEEN             : u'سين' ,
                    SHEEN            : u'شين' ,
                    SAD              : u'صاد' ,
                    DAD              : u'ضاد' ,
                    TAH              : u'طاء' ,
                    ZAH              : u'ظاء' ,
                    AIN              : u'عين' ,
                    GHAIN            : u'غين' ,
                    FEH              : u'فاء' ,
                    QAF              : u'قاف' ,
                    KAF              : u'كاف' ,
                    LAM              : u'لام' ,
                    MEEM             : u'ميم' ,
                    NOON             : u'نون' ,
                    HEH              : u'هاء' ,
                    WAW              : u'واو' ,
                    YEH              : u'ياء' ,
                    HAMZA            : u'همزة' ,

                    TATWEEL          : u'تطويل' ,
                    ALEF_MADDA       : u'ألف ممدودة' ,
                    ALEF_MAKSURA      : u'ألف مقصورة' ,
                    ALEF_HAMZA_ABOVE : u'همزة على الألف' ,
                    WAW_HAMZA        : u'همزة على الواو' ,
                    ALEF_HAMZA_BELOW : u'همزة تحت الألف' ,
                    YEH_HAMZA        : u'همزة على الياء' ,
                    FATHATAN         : u'فتحتان',
                    DAMMATAN         : u'ضمتان',
                    KASRATAN         : u'كسرتان',
                    FATHA            : u'فتحة',
                    DAMMA            : u'ضمة',
                    KASRA            : u'كسرة',
                    SHADDA           : u'شدة',
                    SUKUN            : u'سكون',
                    }

    # regular expretion
    HARAKAT_pattern =re.compile(ur"["+u"".join(HARAKAT)+u"]")
    TASHKEEL_pattern =re.compile(ur"["+u"".join(TASHKEEL)+u"]")
    HAMZAT_pattern =re.compile(ur"["+u"".join(HAMZAT)+u"]");
    ALEFAT_pattern =re.compile(ur"["+u"".join(ALEFAT)+u"]");
    LIGUATURES_pattern =re.compile(ur"["+u"".join(LIGUATURES)+u"]");

    def __init__(self,):
        pass;

    ################################################
    #{ is letter functions
    ################################################
    def isSukun(self,archar):
        """Checks for Arabic Sukun Mark.
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar==self.SUKUN:
            return True;
        else: return False;

    def isShadda(self,archar):
        """Checks for Arabic Shadda Mark.
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar==self.SHADDA:
            return True;
        else: return False;

    def isTatweel(self,archar):
        """Checks for Arabic Tatweel letter modifier.
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar==self.TATWEEL:
            return True;
        else: return False;
    def isTanwin(self,archar):
        """Checks for Arabic Tanwin Marks (FATHATAN, DAMMATAN, KASRATAN).
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.TANWIN:
            return True;
        else: return False;

    def isTashkeel(self,archar):
        """Checks for Arabic Tashkeel Marks (FATHA,DAMMA,KASRA, SUKUN, SHADDA, FATHATAN,DAMMATAN, KASRATAn).
        @param archar: arabic unicode char
        @type archar: unicode
        """
##        if re.search(self.TASHKEEL,word):
        if  archar in  self.TASHKEEL:
            return True;
        else: return False;

    def isHaraka(self,archar):
        """Checks for Arabic Harakat Marks (FATHA,DAMMA,KASRA,SUKUN,TANWIN).
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.HARAKAT:
            return True;
        else: return False;

    def isShortharaka(self,archar):
        """Checks for Arabic  short Harakat Marks (FATHA,DAMMA,KASRA,SUKUN).
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.SHORTHARAKAT:
            return True;
        else: return False;

    def isLigature(self,archar):
        """Checks for Arabic  Ligatures like LamAlef.
        (LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE)
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.LIGUATURES:
            return True;
        else: return False;

    def isHamza(self,archar):
        """Checks for Arabic  Hamza forms.
        HAMZAT are (HAMZA, WAW_HAMZA, YEH_HAMZA, HAMZA_ABOVE, HAMZA_BELOW,ALEF_HAMZA_BELOW, ALEF_HAMZA_ABOVE )
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.HAMZAT:
            return True;
        else: return False;

    def isAlef(self,archar):
        """Checks for Arabic Alef forms.
        ALEFAT=(ALEF, ALEF_MADDA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW,ALEF_WASLA, ALEF_MAKSURA );
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.ALEFAT:
            return True;
        else: return False;

    def isYehlike(self,archar):
        """Checks for Arabic Yeh forms.
        Yeh forms : YEH, YEH_HAMZA, SMALL_YEH, ALEF_MAKSURA
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.YEHLIKE:
            return True;
        else: return False;

    def isWawlike(self,archar):
        """Checks for Arabic Waw like forms.
        Waw forms : WAW, WAW_HAMZA, SMALL_WAW
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.WAWLIKE:
            return True;
        else: return False;

    def isTeh(self,archar):
        """Checks for Arabic Teh forms.
        Teh forms : TEH, TEH_MARBUTA
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.TEHLIKE:
            return True;
        else: return False;
    def isSmall(self,archar):
        """Checks for Arabic Small letters.
        SMALL Letters : SMALL ALEF, SMALL WAW, SMALL YEH
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.SMALL:
            return True;
        else: return False;

    def isWeak(self,archar):
        """Checks for Arabic Weak letters.
        Weak Letters : ALEF, WAW, YEH, ALEF_MAKSURA
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.WEAK:
            return True;
        else: return False;

    def isMoon(self,archar):
        """Checks for Arabic Moon letters.
        Moon Letters :
        @param archar: arabic unicode char
        @type archar: unicode
        """

        if archar in self.MOON:
            return True;
        else: return False;

    def isSun(self,archar):
        """Checks for Arabic Sun letters.
        Moon Letters :
        @param archar: arabic unicode char
        @type archar: unicode
        """
        if archar in self.SUN:
            return True;
        else: return False;
    #####################################
    #{ general  letter functions
    #####################################
    def order(self,archar):
        """return Arabic letter order between 1 and 29.
        Alef order is 1, Yeh is 28, Hamza is 29.
        Teh Marbuta has the same ordre with Teh, 3.
        @param archar: arabic unicode char
        @type archar: unicode
        @return: arabic order.
        @rtype: integer;
        """
        if self.AlphabeticOrder.has_key(archar):
            return self.AlphabeticOrder[archar];
        else: return 0;

    def name(self,archar):
        """return Arabic letter name in arabic.
        Alef order is 1, Yeh is 28, Hamza is 29.
        Teh Marbuta has the same ordre with Teh, 3.
        @param archar: arabic unicode char
        @type archar: unicode
        @return: arabic name.
        @rtype: unicode;
        """
        if self.NAMES.has_key(archar):
            return self.NAMES[archar];
        else:
            return u'';

    def arabicrange(self):
        """return a list of arabic characteres .
        Return a list of characteres between \u060c to \u0652
        @return: list of arabic characteres.
        @rtype: unicode;
        """
        mylist=[];
        for i in range(0x0600, 0x00653):
            try :
                mylist.append(unichr(i));
            except ValueError:
                pass;
        return mylist;


    #####################################
    #{ Has letter functions
    #####################################
    def hasShadda(self,word):
        """Checks if the arabic word  contains shadda.
        @param word: arabic unicode char
        @type word: unicode
        """
        if re.search(self.SHADDA,word):
            return True;
        else:
            return False;

    #####################################
    #{ word and text functions
    #####################################
    def isVocalized(self,word):
        """Checks if the arabic word is vocalized.
        the word musn't  have any spaces and pounctuations.
        @param word: arabic unicode char
        @type word: unicode
        """
        if word.isalpha(): return False;
#        n (self.FATHA,self.DAMMAN,self.KASRA):
        else:
            if re.search(self.HARAKAT_pattern,word):
                return True;
            else:
                return False;
    def isVocalizedtext(self,text):
        """Checks if the arabic text is vocalized.
        The text can contain many words and spaces
        @param text: arabic unicode char
        @type text: unicode
        """
        if re.search(self.HARAKAT_pattern,text):
            return True;
        else:
            return False;
##    def isArabicstring(self,text):
##        """ Checks for an  Arabic Unicode block characters;
##        @param text: input text
##        @type text: unicode
##        @return: True if all charaters are in Arabic block
##        @rtype: Boolean
##        """
##        if re.search(u"([^\u0600-\u0652%s%s%s\w])"%(self.LAM_ALEF, self.LAM_ALEF_HAMZA_ABOVE,self.LAM_ALEF_MADDA_ABOVE),text):
##            return False;
##        return True;

    def isArabicword(self,word):
        """ Checks for an valid Arabic  word.
        An Arabic word
        @param word: input word
        @type word: unicode
        @return: True if all charaters are in Arabic block
        @rtype: Boolean
        """
        if len(word)==0 : return False;
        elif re.search(u"([^\u0600-\u0652%s%s%s\w])"%(self.LAM_ALEF, self.LAM_ALEF_HAMZA_ABOVE,self.LAM_ALEF_MADDA_ABOVE),word):
            return False;
        elif self.isHaraka(word[0]) or word[0] in (self.WAW_HAMZA,self.YEH_HAMZA):
            return False;
    #  if Teh Marbuta or Alef_Maksura not in the end
        elif re.match(u"^(.)*[%s](.)+$"%self.ALEF_MAKSURA,word):
            return False;
        elif re.match(u"^(.)*[%s]([^%s%s%s])(.)+$"%(self.TEH_MARBUTA,self.DAMMA,self.KASRA,self.FATHA),word):
            return False;
        else:
            return True;

    #####################################
    #{Strip functions
    #####################################
    def stripHarakat(self,text):
        """Strip Harakat from arabic word except Shadda.
        The striped marks are :
        	- FATHA, DAMMA, KASRA
        	- SUKUN
        	- FATHATAN, DAMMATAN, KASRATAN, , , .
        Example:
        	>>> text=u"الْعَرَبِيّةُ"
        	>>> stripTashkeel(text)
        	العربيّة

        @param text: arabic text.
        @type text: unicode.
        @return: return a striped text.
        @rtype: unicode.
        """
        return  re.sub(self.HARAKAT_pattern,u'',text)

    def stripTashkeel(self,text):
        """Strip vowels from a text, include Shadda.
        The striped marks are :
        	- FATHA, DAMMA, KASRA
        	- SUKUN
        	- SHADDA
        	- FATHATAN, DAMMATAN, KASRATAN, , , .
        Example:
        	>>> text=u"الْعَرَبِيّةُ"
        	>>> stripTashkeel(text)
        	العربية

        @param text: arabic text.
        @type text: unicode.
        @return: return a striped text.
        @rtype: unicode.
        """
        return re.sub(self.TASHKEEL_pattern,'',text);

    def stripTatweel(self,text):
        """
        Strip tatweel from a text and return a result text.

        Example:
        	>>> text=u"العـــــربية"
        	>>> stripTatweel(text)
        	العربية

        @param text: arabic text.
        @type text: unicode.
        @return: return a striped text.
        @rtype: unicode.
        """
        return re.sub(self.TATWEEL,'',text);

    def normalizeLigature(self,text):
    	"""Normalize Lam Alef ligatures into two letters (LAM and ALEF), and Tand return a result text.
    	Some systems present lamAlef ligature as a single letter, this function convert it into two letters,
    	The converted letters into  LAM and ALEF are :
    		- LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE

    	Example:
    		>>> text=u"لانها لالء الاسلام"
    		>>> normalize_lamalef(text)
    		لانها لالئ الاسلام

    	@param text: arabic text.
    	@type text: unicode.
    	@return: return a converted text.
    	@rtype: unicode.
    	"""
    	return self.LIGUATURES_pattern.sub(u'%s%s'%(self.LAM,self.ALEF), text)
    #     #------------------------------------------------
    def vocalizedlike(self, word, vocalized):
        """return True if the given word have the same or the partial vocalisation like the pattern vocalized

    	@param word: arabic word, full/partial vocalized.
    	@type word: unicode.
    	@param vocalized: arabic full vocalized word.
    	@type vocalized: unicode.
    	@return: True if vocalized.
    	@rtype: unicode.
        """
        if not self.isVocalized(vocalized) or not self.isVocalized(word):
            if self.isVocalized(vocalized):
                vocalized=self.stripTashkeel(vocalized);
            if self.isVocalized(word):
                word=self.stripTashkeel(word);
            if word==vocalized:
                return True;
            else:
                return False;
        else:
            for mark in self.TASHKEEL:
                vocalized=re.sub(u"[%s]"%mark,u"[%s]?"%mark,vocalized)
        	vocalized="^"+vocalized+"$";
        	pat=re.compile("^"+vocalized+"$");
        	if pat.match("^"+vocalized+"$",word):
        	    return True;
        	else: return False;
