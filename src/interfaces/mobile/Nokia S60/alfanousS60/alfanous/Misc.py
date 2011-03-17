# coding: utf-8



import locale
import sys
from  Constantes import buck2uni_table


#correct the direction of arabic
#import pyfribidi
#bd_ = pyfribidi.log2vis

#translation functions
import gettext
gettext.bindtextdomain("fanous", "./locale")
gettext.textdomain("fanous")
_ = gettext.gettext
n_ = gettext.ngettext


#get location
LOC = locale.getdefaultlocale()[0]

#get platform
SYS = sys.platform

def buck2uni(string,ignore=""):
    """ decode buckwalter """
    result = ""
    for ch in string :
            if buck2uni_table.has_key(ch) and ch not in ignore:
                result += buck2uni_table[ch]
            else :
                result+=ch
                
    return result



#filter doubles
def filter_doubles(list):
        for i in range(len(list)):
            if list[i] not in list[i + 1:]:
                yield list[i]










#miniShell 
def miniShell():
    """wait for commands of developer to execute"""
    while(True):
        command = raw_input(">>>")
        exec command


            
            
            

          


if __name__ == '__main__':
    print "system is : ", SYS, " &language is :", LOC
    #Assem testing gettext
    print _(u"hello,i love you Python")
    print _(u"سلام")
    print n_(u"man", u"men", 5)
    miniShell()
    




