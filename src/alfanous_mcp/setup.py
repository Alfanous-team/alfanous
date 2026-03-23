#!/usr/bin/env python
# coding = utf-8

"""
Alfanous MCP Server Setup Script

Publishes alfanous3-mcp as an independent package on PyPI.
"""

import os
from pathlib import Path

from setuptools import setup

DEFAULT_VERSION = "1.0"
DEFAULT_DESCRIPTION = (
    "An MCP (Model Context Protocol) server that exposes the Alfanous "
    "Quranic search engine as tools and resources for AI assistants."
)


def read_readme():
    """Read README.md from the alfanous_mcp directory."""
    readme_path = Path(__file__).resolve().parent / "README.md"
    try:
        return readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return DEFAULT_DESCRIPTION


current_version = os.environ.get('VERSION') or DEFAULT_VERSION

setup(
    name='alfanous3-mcp',
    version=current_version,

    packages=['alfanous_mcp'],

    install_requires=['alfanous3>=1.0.0', 'mcp>=1.0.0'],

    author="Assem Chelli",
    author_email="assem.ch@gmail.com",

    package_dir={'alfanous_mcp': '.'},
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    description=DEFAULT_DESCRIPTION,
    keywords="quran search mcp model-context-protocol alfanous",
    url="https://github.com/Alfanous-team/alfanous",
    include_package_data=True,

    entry_points={'console_scripts': [
        'alfanous-mcp = alfanous_mcp.mcp_server:main',
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
