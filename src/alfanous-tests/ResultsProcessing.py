# coding: utf-8

from alfanous.ResultsProcessing import *

if __name__ == "__main__":
    H = Qhighlight( u"الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", [u"الحمد", u"لله"], "html" )
    print H
