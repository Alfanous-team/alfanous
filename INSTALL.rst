========
Install
========

* **Windows XP/VISTA/SEVEN**: Download the installer from sourceforge: `last version <https://sourceforge.net/projects/alfanous/files/latest/download?source=files>`_

* **Ubuntu-Based**:  you can add Sabily repository and install alfanous from it (`more <http://ubuntuforums.org/showthread.php?t=1370001>`_):

  .. code-block:: sh

        $ add-apt-repository ppa:sabily.team/ppa && sudo apt-get -q update
        $ apt-get install alfanous

* **Fedora-Based**:  follow this  `link1 <http://software.opensuse.org/download.html?project=home:Kenzy:tahadz&package=alfanous>`_  & this `link2 <http://software.opensuse.org/download.html?project=home:Kenzy:tahadz&package=python-alfanous>`_  .

* **OpenSuse-Based**: follow this  `link1 <http://software.opensuse.org/download.html?project=home:Kenzy:tahadz&package=alfanous>`_ & this `link2 <http://software.opensuse.org/download.html?project=home:Kenzy:tahadz&package=python-alfanous>`_ .

* **Archlinux-Based**: use yaourt to install alfanous.

  .. code-block:: sh
	
	$ yaourt alfanous


* **Mac OS**:  There is no available package yet for Mac OS. 

* **Other**: Install from the source by downloading the tarbal and executing those commands carefully:
  
  .. code-block:: sh

        $ make build
        $ sudo make install_api_no_arguments # to install the api and alfanous-console.
        $ sudo make install_desktop_no_arguments # to install alfanous-desktop.


**Note**: If you are a developer you can follow the advancement of Alfanous packaging through this github issue:

- https://github.com/Alfanous-team/alfanous/issues/111
- https://github.com/Alfanous-team/alfanous/issues/26
  
We appreciate any help to achieve those issues :).  



