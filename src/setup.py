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
from pathlib import Path

from setuptools import setup

# Default values when information.json is missing or incomplete
DEFAULT_DESCRIPTION = """ Alfanous is a search engine that provides simple and advanced search in the Holy Qur'an and more features.."""
DEFAULT_LIB_USAGE = "    $ sudo pip install alfanous"
DEFAULT_VERSION = "1.0"


def read_readme():
    """Read the top-level README.md for use as long_description."""
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    try:
        return readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return DEFAULT_DESCRIPTION


def load_information():
    """Load description and metadata from information.json.
    
    Returns:
        tuple: (information dict, description string, lib_usage string)
    """
    try:
        with open("./alfanous/resources/information.json", encoding='utf-8') as f:
            information = json.load(f)
        current_description = information.get("description") or DEFAULT_DESCRIPTION
        current_lib_usage = information.get("lib_usage") or DEFAULT_LIB_USAGE
        return information, current_description, current_lib_usage
    except (FileNotFoundError, json.JSONDecodeError):
        # Fall back to default values if file is missing or invalid
        return {}, DEFAULT_DESCRIPTION, DEFAULT_LIB_USAGE


def get_version(information):
    """Extract a valid version string, falling back to DEFAULT_VERSION for placeholders."""
    version = information.get("version", "")
    if not version or version == "-":
        return DEFAULT_VERSION
    return version


# Get version from environment variable (set during CI/CD) or fall back to information.json
current_version = os.environ.get('VERSION')
if not current_version:
    information, current_description, current_lib_usage = load_information()
    current_version = get_version(information)
else:
    # When VERSION is provided via environment, still read description from information.json
    _, current_description, current_lib_usage = load_information()


setup(

    name='alfanous3',
    version=current_version,

    packages=['alfanous', 'alfanous.Support', 'alfanous.Support.pyarabic'],

    install_requires=['pyparsing', 'whoosh', 'pystemmer'],

    author="Assem Chelli",
    author_email="assem.ch@gmail.com",

    package_dir={'alfanous': 'alfanous'},
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    keywords="quran search indexing engine alfanous",
    url="https://github.com/Alfanous-team/alfanous",
    include_package_data=True,

    package_data={'alfanous': [
                               'configs/*',
                               'indexes/main/*',
                               'indexes/extend/*',
                               # Runtime-only resources (excludes build-time data files
                               # aya.json and fields.json which are only needed by
                               # alfanous_import when building the search index).
                               'resources/information.json',
                               'resources/arabic_names.json',
                               'resources/stop_words.json',
                               'resources/synonyms.json',
                               'resources/antonyms.json',
                               'resources/derivations.json',
                               'resources/vocalizations.json',
                               'resources/standard_to_uthmani.json',
                               'resources/word_props.json',
                               'resources/word.json',
                               'resources/ai_query_translation_rules.txt',
                           ]},

    entry_points={'console_scripts': [
        'alfanous-console = alfanous.console:main',
    ]},

    zip_safe=False,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
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
