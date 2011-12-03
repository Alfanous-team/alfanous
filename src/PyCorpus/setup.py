#!python
#coding=utf-8


from setuptools import setup


setup(
	name="PyCorpus",
	version=0.1,
	package_dir={'PyCorpus':'.'},
	packages=["PyCorpus"],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="Arabic Quranic Corpus  python API",
    long_description=""" a python api for the project   """,
	license="GPL",
	keywords="quran arabic corpus quranic alfanous",
	url="alfanous.sf.net/cms",
	download_url="",
	install_requires=['pyparsing'],
	

    #data_files=[ ('./','quranic-corpus-morpology.xml'),('./','GPL.txt')],
	zip_safe=True,

	
	classifiers=[
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
