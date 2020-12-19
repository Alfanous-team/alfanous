#!/usr/bin/env python2
# coding = utf-8

"""
Alfanous Setup Script
TODO pure python building & installing system
TODO include resources in installation
XXX Index building pre-install script?
"""

import json

from setuptools import setup

information_file = open("./resources/information.json")
information = json.loads(information_file.read()) if information_file else {}
current_version = information["version"] if information.has_key("version") \
    else 0.7
current_description = information["description"] if information.has_key("description") \
    else """ Alfanous is a search engine provide the simple and advanced search in the Holy Qur'an and more features.."""
current_lib_usage = information["lib_usage"] if information.has_key("lib_usage") \
    else "    $ sudo pip install alfanous"

# TODO may add pre-install code here

setup(

    version=current_version,

    packages=['alfanous', 'alfanous.dynamic_resources', 'alfanous.Support',
              'alfanous.Support.whoosh', 'alfanous.Support.whoosh.filedb',
              'alfanous.Support.whoosh.lang', 'alfanous.Support.whoosh.qparser',
              'alfanous.Support.whoosh.support', 'alfanous.Support.PyArabic', ],

    install_requires=['pyparsing'],

    author="Assem Chelli",
    author_email="assem.ch@gmail.com",

    package_dir={'alfanous': '.'},
    long_description=current_description + current_lib_usage,
    keywords="quran search indexing engine alfanous",
    url="https://github.com/Alfanous-team/alfanous",
    include_package_data=True,

    package_data={'alfanous': ['configs/*',
                               'indexes/main/*',
                               'indexes/extend/*',
                               'indexes/word/*',
                               'resources/*']},

    # data_files = [
    #			 ( 'indexes/main', glob.glob( '../../indexes/main/*' ) ),
    #			 ( 'indexes/extend', glob.glob( '../../indexes/extend/*' ) ),
    #			 ( 'indexes/word', glob.glob( '../../indexes/word/*' ) ),
    #			 ( 'resources/configs', glob.glob( '../../resources/configs/*' ) )
    #			 ] ,

    entry_points={'console_scripts': ['alfanous-console = alfanous.console:main', ]},

    zip_safe=False,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: Arabic",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
