#!/usr/bin/env python
# coding = utf-8


from setuptools import setup


setup(
	name="PyAyaByAya",
	description="VerseByVerse project python API",
	version=0.1,
	platforms="ALL",
	license="GPL",
	packages=["PyAyaByAya"],
	install_requires=[],

	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	maintainer="Assem Chelli",
	maintainer_email="assem.ch@gmail.com",

	package_dir={"PyAyaByAya":"."},
	long_description="""A python api for the project versebyverse""",
	keywords="quran aya verse versebyverse everyayah recitation alfanous",
	url="http://www.alfanous.org/",
	download_url="https://sourceforge.net/projects/alfanous/files/",

	include_package_data=True,

	#data_files=[ ('.','GPL.txt')],

	zip_safe=True,

	classifiers=[
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	"Topic :: Software Development :: Libraries :: Python Modules",
	],
)
