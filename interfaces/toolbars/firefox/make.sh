#!/bin/sh




# 	make file 
#	created on Wednsday, August 15th, 2012 at 13:00
#	by SMAHI Zakaria
#	zakaria08esi@gmail.com

cd chrome
zip -r alfanoustoolbar.jar content/* skin/*
cd ..
zip alfanoustoolbar.xpi install.rdf chrome.manifest chrome/alfanoustoolbar.jar

