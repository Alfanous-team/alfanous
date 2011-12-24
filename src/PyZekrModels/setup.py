#!/usr/bin/env python
# coding = utf-8


from setuptools import setup


setup(
	name="PyZekrModels",
	description="A python script to read Zekr translations models",
	version=0.1,
	platforms="ALL",
	license="AGPL",
	packages=["PyZekrModels"],
	install_requires=[],

	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	maintainer="Assem Chelli",
	maintainer_email="assem.ch@gmail.com",

	package_dir={'PyZekrModels':'.'},
	long_description="""A python script to read Zekr translations models""",
	keywords="quran zekr translation model quranic alfanous",
	url="http://www.alfanous.org/",
	download_url="https://sourceforge.net/projects/alfanous/files/",

	include_package_data=True,

	

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
