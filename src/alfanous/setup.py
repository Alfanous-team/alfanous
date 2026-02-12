#!/usr/bin/env python
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
current_version = information.get("version") or 0.7
current_description = information.get("description") or """ Alfanous is a search engine provide the simple and advanced search in the Holy Qur'an and more features.."""
current_lib_usage = information.get("lib_usage") or "    $ sudo pip install alfanous"


setup(

    version=current_version,

    packages=['alfanous',  'alfanous.Support', 'alfanous.Support.pyarabic', ],

    install_requires=['pyparsing', 'whoosh'],

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
