'''
Created on 21 avr. 2010

@author: assem
'''


import pickle 

"""
from main import * 
QSE=QuranicSearchEngine
file_pi = open('qse.obj', 'w') 
pickle.dump(QSE, file_pi) 

"""
filehandler = open('qse.obj', 'r') 
object= pickle.load(filehandler) 

print object()