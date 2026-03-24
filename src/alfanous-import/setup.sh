#!/bin/sh

NAME=Qimport

python setup.py bdist_wininst
python setup.py bdist_egg
python setup.py register
#python setup.py  upload
epydoc   --html -v --graph all --no-sourcecode  --show-imports  -n $NAME -u alfanous.sourceforge.com/cms  .
7z a -tzip  $NAME-html.zip ./html/* 
mv -f $NAME-html.zip ./dist
