# coding: utf-8

"""
This is a test module for alfanous.ResultsProcessing.

"""

from alfanous.results_processing import Qhighlight

if __name__ == "__main__":
    H = Qhighlight( 
                   "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", 
                   ["الحمد", "لله"], 
                   "html" 
                   )
    print(H)
