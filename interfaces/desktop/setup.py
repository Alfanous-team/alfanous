#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

try:
	import py2app
except ImportError:
	pass

import glob


setup(
	name="alfanousDesktop",
	description="Desktop interface for alfanous Quranic search engine API",
	version=0.4,
	platforms="ALL",
	license="GPL",
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
	#entry_points={
		#'gui_scripts': [
		#	'alfanous-desktop = alfanousDesktop.Gui:main',
		#]
		#},

	#app=["Gui.py"],
	
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
