#!/usr/bin/env python
# coding: utf-8
'''
Created on 18 févr. 2010

a specific crawler to find ayates in the web,authentificate them and then index them 

@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL

@todo: a deep study how to represent or how to find ayas inside documents
@todo: a deep study how to authentificate  extracted ayas

'''

import sys
import os
import re
from os import makedirs, path 
from types import StringTypes

from whoosh.index import create_in
from whoosh.fields import * 
from whoosh import index
from whoosh.index import open_dir

from harvestman.apps.spider import HarvestMan
from harvestman.lib.common.common import objects

from sgmllib import SGMLParser


spanreg = re.compile('"class=\"aya\"""')





# You can write a variety of custom crawlers by combining
# different events and writing handlers for them...

def info(S):print "info>", S
def extrainfo(S, T): print "extrainfo>", S, ">>", T





            

class QCrawler(HarvestMan):
    """ A text indexing crawler using PyLucene """

    # NOTE: This class performs work equivalent to the lucene plugin ...

    def __init__(self):
        super(QCrawler, self).__init__()

    def Authent(self, aya):
    """ 
    a methode that test the probanility of an aya to be wrong(ta7rif)
    and take to decision to accept it or reject it 
    
    @todo:  invent the algorithme!!
    """
    
    return True


    def parse_ayas(self, data):
        """ a methode that locate the ayas in an webdocuments 
        @todo:  all types parsing
        """
        return [{"title":"foo page", "aya_gid":1, "text":u"sqfsqd", "auth":False}]
        
    def create_index(self):
        """ Post download setup callback for creating a whoosh index """

        info("Creating whoosh index")

        count = 0

        urllist = []

        urldb = objects.datamgr.get_urldb()

        storeDir = "./urllist"

        ix = UrlList(storeDir).index
        writer = ix.writer()

       
        for node in urldb.preorder():
            urlobj = node.get()

            # Only index if web-page or document
            #if not urlobj.is_webpage() and not urlobj.is_document(): continue

            filename = urlobj.get_full_filename()
            url = urlobj.get_full_url()

            try:
                urllist.index(urlobj.index)
                continue
            except ValueError:
                urllist.append(urlobj.index)

            if not os.path.isfile(filename): continue

            data = ''

            extrainfo('Adding index for URL', url)

            try:
                data = unicode(open(filename).read(), 'iso-8859-1')
            except UnicodeDecodeError, e:
                data = ''

            try:
                print ">>>...",
                writer.add_document(title=u"First document", aya=u"12", file=u"file://" + unicode(filename), url=unicode(url), content=unicode(data))
                
                print "<<<"
            except Exception as e:
                print e
            count += 1


        writer.commit()
         
    def post_download_cb(self, event, *args, **kwargs):
        self.create_index()





class UrlList:
    """ Urllist index Class """
    def __init__(self, path="./urllist"):
        if not index.exists_in(path):
            
            schema = Schema(title=TEXT(stored=True), aya=KEYWORD(stored=True), url=ID(stored=True), file=ID(stored=True, unique=True), content=TEXT(stored=True))
            makedirs(path)
            ix = create_in(path, schema)
        else:
            ix = open_dir(path)
        
        self.index = ix
        
    def find(self, defaultfield="title", query=u"*"):
        return self.index.searcher().find(defaultfield, query)
        
    
            




def start():
    """  start crawling now!!         """
    spider = QCrawler()
    spider.initialize()
    config = spider.get_config()
    config.verbosity = 3
    config.localise = 0
    config.images = 0
    config.pagecache = 0

    spider.register('post_crawl_complete', spider.post_download_cb)
    spider.main()


if __name__ == "__main__":
    #start()
    
    import urllib
    usock = urllib.urlopen("http://diveintopython.org/")
    parser = AyaLister()
    parser.feed(usock.read())
    parser.close()
    usock.close()

    
    """
    U = UrlList()
    for res in U.find():
        print res
    """



    
    
    
    
