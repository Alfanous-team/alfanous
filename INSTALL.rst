AlfanousDesktop
===============

* **Windows XP/VISTA/SEVEN**: Download the installer from sourceforge: `last version <https://sourceforge.net/projects/alfanous/files/latest/download?source=files>`_
* **Ubuntu-Based**:  you can add Sabily repository and install alfanous from it (`more <http://ubuntuforums.org/showthread.php?t=1370001>`_):

  .. code-block:: sh

        $ sudo add-apt-repository ppa:sabily.team/ppa && sudo apt-get -q update
        $ sudo apt-get install alfanous

* **Other Linux distros**:  There is no available package yet for other distros such as redhat-based.  If you are a developer you can follow the advancement of Alfanous packaging to most of linux distributions through those github issues:

  - https://github.com/Alfanous-team/alfanous/issues/111
  - https://github.com/Alfanous-team/alfanous/issues/27
  
  We appreciate any help to achieve those issues :).  




Testers
=======
Try these commands carfully :
.. code-block:: sh

        $ sudo make install_api # to install the api and alfanous-console.
        $ sudo make install_desktop # to install alfanous-desktop.
        $ sudo make install_wui # to install the web user interface.