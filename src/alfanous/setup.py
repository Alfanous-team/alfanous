#!/usr/bin/env python
# coding = utf-8

"""
Alfanous Setup Script
TODO pure python building & installing system
TODO include resources in installation
XXX Index building pre-install script?
"""

import json
import os

from setuptools import setup

# Default values when information.json is missing or incomplete
DEFAULT_DESCRIPTION = """ Alfanous is a search engine that provides simple and advanced search in the Holy Qur'an and more features.."""
DEFAULT_LIB_USAGE = "    $ sudo pip install alfanous"
DEFAULT_VERSION = "1.0"


def load_information():
    """Load description and metadata from information.json.
    
    Returns:
        tuple: (information dict, description string, lib_usage string)
    """
    try:
        with open("./resources/information.json", encoding='utf-8') as f:
            information = json.load(f)
        current_description = information.get("description") or DEFAULT_DESCRIPTION
        current_lib_usage = information.get("lib_usage") or DEFAULT_LIB_USAGE
        return information, current_description, current_lib_usage
    except (FileNotFoundError, json.JSONDecodeError):
        # Fall back to default values if file is missing or invalid
        return {}, DEFAULT_DESCRIPTION, DEFAULT_LIB_USAGE


# Get version from environment variable (set during CI/CD) or fall back to information.json
current_version = os.environ.get('VERSION') or None
if not current_version:
    information, current_description, current_lib_usage = load_information()
    current_version = information.get("version") or DEFAULT_VERSION
else:
    # When VERSION is provided via environment, still read description from information.json
    _, current_description, current_lib_usage = load_information()


setup(

    name='alfanous3',
    version=current_version,

    packages=['alfanous',  'alfanous.Support', 'alfanous.Support.pyarabic', ],

    install_requires=['pyparsing', 'whoosh', 'PyStemmer'],

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

    entry_points={'console_scripts': [
        'alfanous-console = alfanous.console:main',
    ]},

    zip_safe=False,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: Arabic",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
