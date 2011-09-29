#!python
#coding=utf-8


        
        
from setuptools import setup, find_packages
try:
	import py2exe
except:
	pass
#import py2app
import glob

setup(
	name="alfanousDesktop",
	version=0.1,
	package_dir={'alfanousDesktop':'.'},
	packages=["alfanousDesktop"],
	#data_files=[("install","files")],
	author="Assem Chelli",
	author_email="assem.ch@gmail.com",
	description="a desktop interface for alfanous Quranic search engine API",
    long_description="""""",
	license="GPL",
	keywords="quran search indexing engine alfanous",
	url="http://alfanous.sourceforge.net/cms",
	download_url="https://sourceforge.net/projects/alfanous/files",
	install_requires=['alfanous','configobj','pyqt'],#,''
	entry_points={
        'gui_scripts': [
            'alfanousQT = alfanousDesktop.Gui:main',
        ]
       },

    
	include_package_data=True,
  #data_files=[('.','config.ini'),('index',glob.glob('resources/*.*'))    ],
   
   windows = [
        {
            "script": "Gui.py",
            "icon_resources": [(1, "resources/Alfanous.ico")]
			
        }
    ],
     options={"py2exe" : {"includes" : ["sip"]}},
    
    app=["Gui.py"],

	zip_safe=True,

	
	classifiers=[
	"Development Status :: 4 - Beta",
	"Intended Audience :: Users",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Natural Language :: Arabic",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	],
	
)
