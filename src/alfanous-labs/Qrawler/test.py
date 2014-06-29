#!/usr/bin/env python

"""
indexingcrawler.py - Demonstrating custom crawler writing by
subscribing to events. This is a crawler which crawls a given
URL and indexes documents at the end of the crawl.

Created by Anand B Pillai <abpillai at gmail dot com>

Copyright (C) 2008 Anand B Pillai
"""

import __init__
import sys, os

from whoosh.index import create_in
from whoosh.fields import * 
from whoosh import index
from whoosh.index import open_dir
from os import makedirs, path

from harvestman.apps.spider import HarvestMan
from harvestman.lib.common.common import *
from types import StringTypes

# You can write pretty crazy custom crawlers by combining
# different events and writing handlers for them ! :)

class IndexingCrawler(HarvestMan):
    """ A text indexing crawler using PyLucene """

    # NOTE: This class performs work equivalent to the lucene plugin ...

    def __init__(self):
        super(IndexingCrawler, self).__init__()

    def create_index(self):
        """ Post download setup callback for creating a lucene index """

        info("Creating lucene index")

        count = 0

        urllist = []

        urldb = objects.datamgr.get_urldb()

        storeDir = "index"
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = PyLucene.FSDirectory.getDirectory(storeDir, True)
        lucene_writer = PyLucene.IndexWriter(store, PyLucene.StandardAnalyzer(), True)    
        lucene_writer.setMaxFieldLength(1048576)
       
       
        for node in urldb.preorder():
            urlobj = node.get()

            # Only index if web-page or document
            if not urlobj.is_webpage() and not urlobj.is_document(): continue

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
                doc = PyLucene.Document()
                doc.add(PyLucene.Field("name", 'file://' + filename,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.UN_TOKENIZED))
                doc.add(PyLucene.Field("path", url,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.UN_TOKENIZED))
                if data and len(data) > 0:
                    doc.add(PyLucene.Field("contents", data,
                                           PyLucene.Field.Store.YES,
                                           PyLucene.Field.Index.TOKENIZED))
                else:
                    warning("warning: no content in %s" % filename)

                lucene_writer.addDocument(doc)
            except PyLucene.JavaError, e:
                print e
                continue
           
            count += 1

        info('Created lucene index for %d documents' % count)
        info('Optimizing lucene index')
        lucene_writer.optimize()
        lucene_writer.close()
   
    def post_download_cb(self, event, *args, **kwargs):
        self.create_index()

class UrlList:
    """ Urllist index Class """
    def __init__(self, path="./urllist"):
        if not index.exists_in(path):
            schema = Schema(title=TEXT(stored=True), aya=KEYWORD(stored=True), url=ID(stored=True), cache=ID(stored=True))
            makedirs(path)
            ix = create_in(path, schema)
        else:
            ix = open_dir(path)
        
        self.index = ix
        
    def find(self, defaultfield="aya", query=u"*"):
        return self.index.searcher().find(defaultfield, query)

if __name__ == "__main__":
    spider = IndexingCrawler()
    spider.initialize()
    config = spider.get_config()
    config.verbosity = 3
    config.localise = 0
    config.images = 0
    config.pagecache = 0

    spider.bind_event('save_url_data', spider.post_download_cb)
    spider.main()


