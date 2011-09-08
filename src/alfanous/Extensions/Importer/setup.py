#!python
#coding=utf-8


from setuptools import setup


setup(
	name="Qimport",
	version=0.1,
	package_dir={'Qimport':'.'},
	packages=["Qimport"],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="importing system for quranic indexes",
    long_description=""" Importing System for alfanous Search engine""",
	license="GPL",
	keywords="search quran islam alfanous arabic",
	url="alfanous.sf.net/cms",
	download_url="",
	install_requires=["whoosh","PyCorpus"],
	include_package_data=True,
	
	data_files=[ ('.','./urls.txt'),('.','./GPL.txt'),('.','./config.xml')],
    
	zip_safe=True,

	

	
)
