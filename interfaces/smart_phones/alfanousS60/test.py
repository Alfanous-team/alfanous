'''
Created on 7 avr. 2010

an interface of alfanous in Nokia S60 mobiles

@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: AGPL



@note: this is just a test
'''

import appuifw,e32

def quit():
    print "preparing to quit..."
    app_lock.signal()

def search():
    pass

def about():
    pass

appuifw.app.exit_key_handler = quit
appuifw.app.title = u"Alfanous"

appuifw.app.menu = [(u"search", search), (u"about...",((u"about alfanous", about), (u"about me", about)))]  

appuifw.note(u"Application is now running")
query = unicode(appuifw.query(u"Type a query:", "text"))
limit = appuifw.query(u"Limit:", "number")
sortedby = appuifw.query(u"Sortedby:", "text")
choices = [u"score", u"mushaf", u"tanzil"]  

index = appuifw.popup_menu(choices, u"sortedby:")   
sortedby=choices[index]
    
appuifw.note(u"your query: " + str(query), "info")    
   
   


app_lock = e32.Ao_lock()
app_lock.wait()




