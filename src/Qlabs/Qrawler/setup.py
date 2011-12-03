#!python
#coding=utf-8


from setuptools import setup


setup(
	name="Qrawl",
	version=0.1,
	package_dir={'Qrawl':'.'},
	packages=["Qrawl"],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="a crawling system for quranic and islamic sites",
    long_description="""""",
	license="GPL",
	keywords="search quran islam alfanous arabic",
	url="",
	download_url="",
	install_requires=[],
	include_package_data=True,
	data_files=[ ('.','main.db'),('.','GPL.txt')],
	zip_safe=True,
	classifiers=[
	"Development Status :: 3 - Alpha",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	"Topic :: Software Development :: Libraries :: Python Modules"
	],
	
)
