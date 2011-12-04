#!/usr/bin/env python
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
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''


HowTo
=====
      >>> from everyayah import API 
      >>> A=API()
      >>> A.recitations_list()[0]
  	  {u'Folder': u'http://www.versebyversequran.com/data/Abdul_Basit_Murattal', u'bitrate': u'64', u'name': u'AbdulBasit AbdusSamad (Murattal style)', u'Description': ''} 
      
      >>> print A.recitation_link("AbdulBasit AbdusSamad (Murattal style)", sura=2, aya=1)
      http://www.versebyversequran.com/data/Abdul_Basit_Murattal/002001.mp3
      
      >>> A.list_it("name")[:3]
      [u'AbdulBasit AbdusSamad (Murattal style)', u'AbdulBasit AbdusSamad (From QuranExplorer.com)', u'Abu Bakr Ash-Shaatree']
        
@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL      

'''

import urllib2  
import xml.dom.minidom as dom    
import os
             
class API:
    """    Recitation AyaByAya project reader     """
    
    
    def __init__(self, root="http://www.everyayah.com/", temppath="/tmp/Recitations.xml"):
            """ 
            @param root: the root of AyaByAya project site      
            @param temppath: the temporary file path   
            @attention: add the last slash
            
            """
            self.root = root
            self.lastlist = None
            self.temppath = temppath
            self.xmlurl = root + "data/Recitations.xml"

    def _parse_xml(self, data):
        base = dom.parseString(data)
        list = []
        for recitations in base.childNodes:
            if recitations.localName == u"Recitations":
                for recitation in recitations.childNodes:
                    if recitation.localName == u"Recitation":
                        item = {}
                        for attrib in recitation.attributes.values():
                            item[attrib.localName] = attrib.value
                        for child in recitation.childNodes:
                            if child.localName != None:
                                item[child.localName] = child.childNodes[0].data if len(child.childNodes) == 1 else ""
                        yield item

          
    def update_online(self):
            """ download the xml file to temp folder for new uses """
            xmldata = urllib2.urlopen(self.xmlurl).read()
            list = [item for item in self._parse_xml(xmldata)]
            if self.temppath:
                file = open(self.temppath, "w+")
                file.write(xmldata)
                file.close()
            self.lastlist = list
            return list

               
            
    def recitations_list(self):
        """ 
        load the list of available recitations found on the site (online)
        @return: [{},{}...]
        """
        if not self.lastlist:
            if self.temppath :
                if os.path.exists(self.temppath):
                    xmlfile = open(self.temppath, "r")
                    self.lastlist = [item for item in self._parse_xml(xmlfile.read())]
            else:
                self.lastlist = self.update_online()    
   
        return self.lastlist
    


    
      

        
    def list_it(self, info="name"):
            return [recit[info] for recit in self.recitations_list()]

    
    def name_mp3(self, sura=1, aya=1):    
        return "%03d%03d.mp3" % (sura, aya)
    
    def get_folder(self, name):
        for recit in self.recitations_list():
            if recit["name"] == name:
                return recit["Folder"]
                break
            
    def recitation_link(self, name, sura, aya):
        return self.get_folder(name) + "/" + self.name_mp3(sura, aya)
        
        
    def build_dict(self,key="name",value="Folder"):
        """ return a python dictionary as a string  """
        D={}
        list1 = A.list_it(key)
        list2 = A.list_it(value)
        for i in range(len(list1)):
            D[list1[i]]=list2[i] 
        
        return str(D).replace(",",",\n")
        


if __name__ == "__main__":
    A = API(temppath="")
    print A.recitations_list()
    list = A.list_it("name")
    for item in list:
        print A.recitation_link(item, 2, 1)
