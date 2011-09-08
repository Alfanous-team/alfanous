# coding: utf-8
#    Copyright (C) 2009-2010 Assem Chelli <assem.ch@gmail.com>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

'''
The System of Exceptions


@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL
@version: 0.1
@organization: Alone,but Need Support
'''

    
    
    
class Ta7rif(Exception):
    """ raise when an error in Holy Quran text 
    
    example:
    ========
        >>> raise Ta7rif(type="new",value=u"ابراهام",original="ابراهيم",aya_gid=0,msg="word changed")
    
    @param type:type of ta7rif
    @type type:string
    @param value:value of ta7rif
    @type value:unicode
    @param original:the original value
    @type original:unicode
    @param aya_gid:the general id of aya
    @type aya_gid:int
    @param msg:the message of error
    @type msg:unicode
    
    """
    def __init__(self, type="new", value="undefined", original=None, aya_gid=None, msg=""):     
        self.type = type
        self.aya_gid = aya_gid
        self.value = value
        self.original = original
        self.msg = msg
    
    def __str__(self):
        return "\nTa7rif in Holy Quran :\n\tType:" + str(self.type) + "\n\tvalue:" + str(self.value) + "\n\toriginalvalue:" + str(self.original) + "\n\taya_gid:" + str(self.aya_gid) + "\n\n" + str(self.msg)
         
 
class NotImplemented(Exception):
    """raise when a methode is not implemented
    
    example:
    ========
        >>> raise NotImplemented(message="waiting a good stemmer",methode="derivation",developper="assem.ch@gmail.com",date="01/02/10")
        
    @param message:the message of error
    @type message:unicode 
    
    
    """ 
    def __init__(self, message="", methode="undefined", developper="", date=""):
        self.methode = methode
        self.developper = developper
        self.message = message
        self.date = date
        
    def __str__(self):
        return "\nthis  :\n\tType:" + str(self.type) + "\n\tvalue:" + str(self.value) + "\n\toriginalvalue:" + str(self.original) + "\n\taya_gid:" + str(self.aya_gid) + "\n\n" + str(self.msg)
    

class FeedBack(Exception):
    """ declare an empty case in an index 
    
    example:
    ========
        >>>
    
    
    """
    def __init__(self, table, value):
        self.table = table
        self.value = value
        
    def __str__(self):
        return "\n\ttable:" + self.table + "\n\tvalue:" + self.value
    
    

    
    
