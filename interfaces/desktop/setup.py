#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO: package for MacOS


from setuptools import setup, find_packages
import glob

try:
	import py2app  ## for MAC package
except ImportError:
	pass

try: 
	import py2exe  ## to generate an exe file
except:
	pass



setup(
	name="alfanousDesktop",
	description="Desktop interface for alfanous Quranic search engine API",
	version=0.4,
	platforms="ALL",
	license="AGPL",
	packages=["alfanousDesktop"],
	install_requires=['alfanous','configobj','pyparsing'],#,'pyqt',
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	maintainer="Assem Chelli",
	maintainer_email="assem.ch@gmail.com",

	package_dir={'alfanousDesktop':'.'},
	long_description="""A PyQt GUI interface for alfanous Quranic search engine API""",
	keywords="quran search indexing engine alfanous",
	url="http://www.alfanous.org/",
	download_url="https://sourceforge.net/projects/alfanous/files/",

	#data_files=[("install","files")],
	#data_files=[('.','config.ini'),('index',glob.glob('resources/*.*'))],

	include_package_data=True,

	
	#entry_points={ 'gui_scripts': ['alfanousQT = alfanousDesktop.Gui:main',]},
		
	windows = [{
			"script": "../../resources/launchers/alfanousDesktop-win.py",
			"icon_resources": [(1, "../../resources/Alfanous.ico")]
		}],
	
	options={"py2exe" : {"includes" : ["sip"]}},
	#app=["alfanousDesktop-win.py"],
	
	classifiers=[
	"Development Status :: 4 - Beta",
	"Intended Audience :: Users",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	]
)
