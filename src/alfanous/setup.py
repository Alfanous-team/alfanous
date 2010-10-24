#!python
#coding=utf-8

import glob


from setuptools import setup,find_packages



setup(
	name="alfanous",
	version=0.2,
	package_dir={'alfanous':'.'},
	packages=["alfanous", "alfanous.dynamic_ressources", "alfanous.Support"],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="Quranic search engine API",
    long_description="""Alfanous is a search engine provide the simple and advanced search in the Holy Qur'an and more features...""",
	license="GPL",
	keywords="quran search indexing engine alfanous",
	url="http://alfanous.sourceforge.net/cms",
	download_url="https://sourceforge.net/projects/alfanous/files",
	install_requires=['whoosh >= 0.3.18'],

	include_package_data=True,

    #data_files=[ ('indexes/main',glob.glob('indexes/main/*')),('indexes/extend',glob.glob('indexes/extend/*'))],#,('indexes/extend',glob.glob('indexes/extend/*'))
   
    
	zip_safe=True,

	
	classifiers=[
	"Development Status :: 3 - Alpha",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	"Topic :: Software Development :: Libraries :: Python Modules",
	],
	
)
