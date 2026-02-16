#!/usr/bin/env python
# coding: utf-8

"""
Alfanous Web API Package

A FastAPI web application that exposes the Alfanous Quranic search API
through RESTful endpoints.
"""

__version__ = "0.7.33"
__author__ = "Assem Chelli"

from alfanous_webapi.web_api import app, main

__all__ = ["app", "main"]
