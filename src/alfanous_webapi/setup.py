#!/usr/bin/env python
# coding: utf-8

"""
Alfanous Web API Setup Script
"""

from setuptools import setup, find_packages
import os


def read_readme():
    """Read README file with proper resource cleanup."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            return f.read()
    return ""


setup(
    name='alfanous-webapi',
    version='0.7.33',
    
    packages=find_packages(),
    
    install_requires=[
        'alfanous3',
        'fastapi>=0.104.0',
        'uvicorn[standard]>=0.24.0',
        'pydantic>=2.0.0'
    ],
    
    author="Assem Chelli",
    author_email="assem.ch@gmail.com",
    
    description="FastAPI web interface for Alfanous Quranic search API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    keywords="quran search api fastapi alfanous web rest",
    url="https://github.com/Alfanous-team/alfanous",
    
    entry_points={
        'console_scripts': [
            'alfanous-server = alfanous_webapi.web_api:main',
        ]
    },
    
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: FastAPI",
    ],
)
