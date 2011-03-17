#!python
#coding=utf-8


from setuptools import setup


setup(
	name="alfanouS60",
	version=0.1,
	package_dir={'alfanouS60':'.'},
	packages=["alfanouS60"],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="alfanous for Nokia S60 mobiles",
    long_description="""""",
	license="GPL",
	keywords="alfanous mobile nokia",
	url="",
	download_url="",
	install_requires=[],
	include_package_data=True,
	data_files=[ ('.','GPL.txt')],

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
