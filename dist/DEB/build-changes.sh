#!/bin/sh

cd ./alfanous
nano DEBIAN/changelog
nano DEBIAN/control

mv DEBIAN debian
dpkg-buildpackage -S -rfakeroot -k2B2B8B26
mv debian DEBIAN


