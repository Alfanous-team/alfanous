#!/usr/bin/env python
#coding=utf-8

from setuptools import setup


setup( 
	name = "Qimport",
	description = "Importing system for quranic indexes",
	version = 0.1,
	platforms = "ALL",
	license = "AGPL",
	packages = ["Qimport"],
	install_requires = ["whoosh", "PyCorpus"],

	author = "Assem Chelli",
	author_email = "assem.ch@gmail.com",
	maintainer = "Assem Chelli",
	maintainer_email = "assem.ch@gmail.com",

	package_dir = {'Qimport':'.'},
	long_description = """ Importing system for Alfanous search engine""",
	keywords = "search quran islam alfanous arabic",
	url = "http://www.alfanous.org/",
	download_url = "https://sourceforge.net/projects/alfanous/files/",

	include_package_data = True,

	data_files = [ ( '.', './urls.txt' ), ( '.', './GPL.txt' ), ( '.', './config.xml' )],

	zip_safe = True,

	classifiers = [
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	"Topic :: Software Development :: Libraries :: Python Modules",
	]
 )
