#!python
# -*- coding: utf-8 -*-
#coding=utf-8


from setuptools import setup, find_packages

try:
	import py2app
except ImportError:
	pass


import glob

setup(
	name="alfanousDesktop",
	version=0.4,
	package_dir={'alfanousDesktop':'.'},
	packages=["alfanousDesktop"],
	#data_files=[("install","files")],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="a desktop interface for alfanous Quranic search engine API",
    	long_description="""""",
	license="GPL",
	keywords="quran search indexing engine alfanous",
	url="http://alfanous.org",
	install_requires=['alfanous','configobj'],#,'pyqt',
	#entry_points={
        #'gui_scripts': [
        #    'alfanous-desktop = alfanousDesktop.Gui:main',
        #]
        #},


	
  
    
   	#app=["Gui.py"],
	
	classifiers=[
	"Development Status :: 4 - Beta",
	"Intended Audience :: Users",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	],
	
)
