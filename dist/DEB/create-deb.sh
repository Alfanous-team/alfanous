#!/bin/sh


echo "remove these" `find .  -name *~`
sudo rm -rf `find .  -name *~`;


sudo nano  alfanous/DEBIAN/changelog
sudo nano alfanous/DEBIAN/control

dpkg-deb -D --build alfanous alfanous-$1.deb



