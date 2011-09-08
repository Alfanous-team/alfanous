#!python
#coding=utf-8


from setuptools import setup


setup(
	name="PyAyaByAya",
	version=0.1,
	package_dir={'PyAyaByAya':'.'},
	packages=["PyAyaByAya"],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="VerseByVerse project python API",
    long_description="""a python api for the project versebyverse""",
	license="GPL",
	keywords="aya verse versebyverse everyayah recitation alfanous",
	url="alfanous.sf.net/cms",
	download_url="",
	install_requires=[],
	include_package_data=True,
	
	#data_files=[ ('.','GPL.txt')],
   
    
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
