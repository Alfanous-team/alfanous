#!python
#coding=utf-8


from setuptools import setup

setup(
	name="alfanousMIN",
	version=0.1,
	package_dir={'alfanous':'.'},
	packages=["alfanous","alfanous.dynamic_ressources", "alfanous.Support"],
	#data_files=[("install","files")],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="Quranic search engine API",
 	license="GPL",
	keywords="quran search indexing engine alfanous",
	
	install_requires=['whoosh >= 0.3.12'],

    
	package_data={
        '': ['*.txt'],
       'alfanous': ['indexes/main/*.*']
        },
        
    exclude_package_data = { '': ['*.xls']},
    
	zip_safe=True,
	#test_suite = "tests",

)
