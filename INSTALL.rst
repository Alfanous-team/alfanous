========
Install
========

#. **Windows XP/VISTA/SEVEN**: 

	Download the installer from sourceforge: `last version <https://sourceforge.net/projects/alfanous/files/latest/download?source=files>`_

#. **Ubuntu-Based**:  
	you can add Alfanous ppa repo on Launchpad and install alfanous from it:
	  .. code-block:: sh
	
	        add-apt-repository ppa:team4alfanous/alfanous && sudo apt-get -q update
	        apt-get install alfanous

#. **Fedora-Based**: 

	For Fedora 21 run the following as root:
	
	  .. code-block:: sh
	
		cd /etc/yum.repos.d/
		wget http://download.opensuse.org/repositories/home:Kenzy:tahadz/Fedora_21/home:Kenzy:tahadz.repo
		yum install alfanous
		
	For Fedora 20 run the following as root:
	
	  .. code-block:: sh
	  
		cd /etc/yum.repos.d/
		wget http://download.opensuse.org/repositories/home:Kenzy:tahadz/Fedora_20/home:Kenzy:tahadz.repo
		yum install alfanous


#. **OpenSuse-Based**: 

	For openSUSE 13.2 run the following as root:
	
	  .. code-block:: sh
	  
		zypper addrepo http://download.opensuse.org/repositories/home:Kenzy:tahadz/openSUSE_13.2/home:Kenzy:tahadz.repo
		zypper refresh
		zypper install alfanous

#. **Archlinux-Based**: 

	  .. code-block:: sh
		
		yaourt alfanous
		yaourt alfanous-git  # nightly build


#. **Other**: 
	Install from the source by downloading the tarbal and executing those commands carefully:
	  
	  .. code-block:: sh
	
	        $ make build
	        $ sudo make install_api_no_arguments # to install the api and alfanous-console.
	        $ sudo make install_desktop_no_arguments # to install alfanous-desktop.



