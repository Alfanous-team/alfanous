# coding: utf-8
'''
Created on 17 avr. 2010

a module to calculate different statistiques on coranic text 


@author: assem
'''
from araby import araby
import re
araby=araby()

def letters(text):
    return len([char for char in text if char in araby.LETTERS])


def diacritics(text):
    return len([char for char in text if char in araby.TASHKEEL])

def letter_count(text,letter):
    return len([char for char in text if char==letter])

def hamza_count(text):
    return len([char for char in text if char in araby.HAMZAT]) 


def words(text):
    word_pattern=re.compile("[^\n\r \t]+")
    return len(word_pattern.findall(text))

def gwords(text):
    gword_pattern=re.compile(u"لله")
    return len(gword_pattern.findall(araby.stripTashkeel(text)))

def sunletters(text):
    return len([char for char in text if char in araby.SUN])

def moonletters(text):
    return len([char for char in text if char in araby.MOON])



if __name__=="__main__":
    str=u" اللّهم يً ْيسئء سبي شبيشيش شسيشسي"
    print "letters=",letters(str)
    print "diacritics=",diacritics(str)
    print "letter_count=",letter_count(str,u"ش")
    print "hamza_count=", hamza_count(str)
    print "words=",words(str)
    print "gwords=",gwords(str)
    print "sunletters=",sunletters(str)
    print "moonletters=",moonletters(str)