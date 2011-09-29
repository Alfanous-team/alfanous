#!/bin/sh
cd chrome
zip -r alfanoustoolbar.jar content/* skin/*
cd ..
zip alfanoustoolbar.xpi install.rdf chrome.manifest chrome/alfanoustoolbar.jar

