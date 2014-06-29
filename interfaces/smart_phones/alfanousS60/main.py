'''
Created on 7 avr. 2010

This is the interface of alfanous in Nokia S60 mobiles

@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: AGPL


@note: this is just a test
'''

import appuifw,e32
from alfanous.main import QuranicSearchEngine    

appuifw.app.screen = "large" # "full" "normal"


def quit():
    print "preparing to quit..."
    app_lock.signal()

def search():
    pass

def about():
    pass

appuifw.app.exit_key_handler = quit
appuifw.app.title = u"Alfanous for S60"

appuifw.app.menu = [(u"search", search), (u"about...",((u"about alfanous", about), (u"about me", about)))]  

appuifw.note(u"Application is now running")
query = unicode(appuifw.query(u"Type a query:", "text"))
limit = appuifw.query(u"Limit:", "number")
sortedby = appuifw.query(u"Sortedby:", "text")
choices = [u"score", u"mushaf", u"tanzil"]  

index = appuifw.popup_menu(choices, u"sortedby:")   
sortedby=choices[index]
    
appuifw.note(u"your query: " + str(query), "info")    
   
   
QSE = QuranicSearchEngine()    
res, terms = QSE.search_all(query, limit=limit, sortedby=sortedby)



app_lock = e32.Ao_lock()
app_lock.wait()



"""
#sound example

   1. import audio  
   2.   
   3. sound = audio.Sound.open("E:\\Sounds\\mysound.mp3")  
   4.   
   5. def playMP3():  
   6.      sound.play()  
   7.      print "PlayMP3 returns.."  
   8.   
   9. playMP3()  
   
"""

