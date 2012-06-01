#!python
#coding=utf-8


from setuptools import setup

setup( 
	name = "PyTanzil",
	version = 0.1,
	package_dir = {'PyTanzil':'.'},
	packages = ["PyTanzil"],
	author = "PyTanzil",
	author_email = "assem.ch@gmail.com",
	description = "Tanzil project python API",
    long_description = """""",
	license = "GPL",
	keywords = "tanzil quran verse  alfanous",
	url = "",
	download_url = "",
	install_requires = ["elementtree"],
	include_package_data = True,



    data_files = [ ( '.', 'quran-uthmani.xml' ), ( '.', 'quran-properties.xml' ), ( '.', 'GPL.txt' )],
	zip_safe = True,


	classifiers = [
	"Development Status :: 3 - Alpha",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	"Topic :: Software Development :: Libraries :: Python Modules",
	],

 )
