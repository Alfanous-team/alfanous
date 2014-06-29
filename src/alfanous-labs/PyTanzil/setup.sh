#!/bin/sh

(python setup.py sdist --format=zip
python setup.py bdist_egg
python setup.py bdist_rpm 
python setup.py bdist_wininst
python setup.py register
python setup.py  upload)>>test.text

