#!/usr/bin/env python
# coding = utf-8

"""
Alfanous Setup Script
TODO pure python building & installing system
TODO include resources in installation
XXX Index building pre-install script?
"""




import json
#import glob

try:
	from setuptools import setup#,find_packages
except ImportError:
	from alfanous.ez_setup import use_setuptools
	use_setuptools()

information_file = open( "./resources/information.json" )
information = json.loads( information_file.read() ) if information_file else {}
current_version = information["version"] if information.has_key( "version" ) \
		  else 0.7
current_description = information["description"] if information.has_key( "description" ) \
		  else """ Alfanous is a search engine provide the simple and advanced search in the Holy Qur'an and more features.."""
#TODO may add pre-install code here

setup( 
	name = "alfanous",
	description = "Quranic search engine API",
	version = current_version,
	platforms = "ALL",
	license = "AGPL",
	#packages=find_packages(where='..', exclude=()),
	packages = ['alfanous', 'alfanous.dynamic_resources', 'alfanous.Support',
            'alfanous.Support.whoosh', 'alfanous.Support.whoosh.filedb',
            'alfanous.Support.whoosh.lang', 'alfanous.Support.whoosh.qparser',
            'alfanous.Support.whoosh.support'],

	install_requires = ['pyparsing'], # 'whoosh == 0.3.18',

	author = "Assem Chelli",
	author_email = "assem.ch@gmail.com",
	maintainer = "Assem Chelli",
	maintainer_email = "assem.ch@gmail.com",

	package_dir = {'alfanous':'.'},
	long_description = current_description,
	keywords = "quran search indexing engine alfanous",
	url = "http://www.alfanous.org/",
	#download_url = "https://sourceforge.net/projects/alfanous/files/",

	include_package_data = True,

	package_data = {'alfanous': ['configs/*',
								'indexes/main/*',
								'indexes/extend/*',
								'indexes/word/*',
								'resources/*']},

	#data_files = [
	#			 ( 'indexes/main', glob.glob( '../../indexes/main/*' ) ),
	#			 ( 'indexes/extend', glob.glob( '../../indexes/extend/*' ) ),
	#			 ( 'indexes/word', glob.glob( '../../indexes/word/*' ) ),
	#			 ( 'resources/configs', glob.glob( '../../resources/configs/*' ) )
	#			 ] ,

	entry_points = { 'console_scripts': ['alfanous-console = alfanous.console:main', ]},

	zip_safe = True,

	classifiers = [
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	"Topic :: Software Development :: Libraries :: Python Modules",
	],
 )
