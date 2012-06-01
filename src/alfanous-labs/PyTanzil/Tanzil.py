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
Created on 21 mars 2010


HowTo
=====


@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL



@todo: load the tanzil xml files





'''


from elementtree.ElementTree import parse


class API:
    """ the api """
    def __init__( self, textxml = "quran-uthmani.xml", propxml = "quran-uthmani.xml" ):
        """ init the API based on XMLfile

        @param source: the path of the xml file

        """
        self.mushaf = parse( textxml ).getroot()
        self.info = parse( propxml ).getroot()



    def buildtheGiant( self ):
        """ build the Giant index for alfanous project"""
        pass


if __name__ == "__main__":
    A = API( textxml = "../../../store/quran-uthmani.xml", propxml = "../../../store/quran-uthmani.xml" )



