#
# This is Alfanous Makefile
#
# Contributors:   
#	Assem chelli <assem.ch@gmail.com>
#
##  TODO: Must follow the standards!
##  TODO: Check installation scripts



VERSION="0.5.0"

API_PATH="./src/"
QIMPORT=$(API_PATH)"alfanous-import/main.py"
DYNAMIC_RESOURCES_PATH=$(API_PATH)"alfanous/dynamic_resources/"

CONFIG_PATH="./resources/configs/"
DB_PATH="./resources/databases/"
QT_UI_PATH="./resources/UI/"

STORE_PATH="./store/"
INDEX_PATH=$(API_PATH)"alfanous/indexes/"

DESKTOP_INTERFACE_PATH=$(API_PATH)"alfanous-desktop/"
MOBILE_WUI_PATH=./interfaces/web/mobile_wui/
WUI_PATH=./interfaces/web/wui/

PREFIX?=/usr
CONFIG_INSTALL_PATH="$(DESTDIR)$(PREFIX)/share/alfanous-config/"
INDEX_INSTALL_PATH="$(DESTDIR)$(PREFIX)/share/alfanous-indexes/"
WEB_INSTALL_PATH=$(DESTDIR)/var/www/alfanous-web/
WEB_CGI_INSTALL_PATH=$(WEB_INSTALL_PATH)cgi/


default: 
	@echo "choose a target!"
	
## Kaboom! @TODO: must test this well
all:  download_all   build   tarball_data  dist_all  clean  #tarball_minimal #install_all	 


##
build:  update_pre_build index_all speller_all update_post_build qt_all local_pot_all help_all

	
clean:
	@echo "Cleaning" 
	rm -rf `find . -type f -name Thumbs.db`
	#rm -rf `find . -name *~`
	rm -rf `find . -name *.pyc`
	rm -rf `find . -name *.pyo`
	rm -rf `find . -type d -name *.egg-info`
	


##  update store  & dynamic_ressources & qt forms scripts & qt resources
update_post_build:  update_information update_hints update_translations_indexed_list update_recitations_offline_list update_recitations_online_list    

update_pre_build:  update_quranic_corpus update_dynamic_resources update_translations_to_download_list

update_information:
	nano $(CONFIG_PATH)information.js

update_hints:
	nano $(CONFIG_PATH)hints.js

update_stats:
	nano $(CONFIG_PATH)stats.js # create an empty file {}
	chmod 777 $(CONFIG_PATH)stats.js 

update_translations_to_download_list:
	nano $(STORE_PATH)Translations/translations.list

update_translations_indexed_list:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -u translations.js  $(INDEX_PATH)extend/ $(CONFIG_PATH)translations.js

update_quranic_corpus:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -u wordqc $(STORE_PATH)quranic-corpus-morpology.xml $(DB_PATH)main.db

update_recitations_offline_list:
	@echo "todo"

update_recitations_online_list:
	cd $(CONFIG_PATH); wget http://www.everyayah.com/data/recitations.js

update_dynamic_resources: transfer_all
	
## build dynamic_resources 
transfer_all: transfer_stopwords transfer_synonyms transfer_word_props transfer_derivations transfer_ara2eng_names transfer_standard2uthmani
	@echo "done;"
	
	
transfer_stopwords:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -t stopwords $(DB_PATH)main.db $(DYNAMIC_RESOURCES_PATH)
	
transfer_synonyms:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -t synonyms $(DB_PATH)main.db $(DYNAMIC_RESOURCES_PATH)

transfer_word_props:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -t word_props $(DB_PATH)main.db $(DYNAMIC_RESOURCES_PATH)

transfer_derivations:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -t derivations $(DB_PATH)main.db $(DYNAMIC_RESOURCES_PATH)

transfer_vocalizations:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -t vocalizations $(DB_PATH)main.db $(DYNAMIC_RESOURCES_PATH)

transfer_ara2eng_names:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -t ara2eng_names $(DB_PATH)main.db $(DYNAMIC_RESOURCES_PATH)
	
transfer_standard2uthmani:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -t std2uth_words $(DB_PATH)main.db $(DYNAMIC_RESOURCES_PATH)
	


## download resources
download_all: download_translations download_recitations download_quranic_corpus download_tanzil local_mo_download

download_translations:
	#  download from  http://zekr.org/resources.html to ./store/traductions
	cd $(STORE_PATH)Translations;  wget -i translations.list



download_recitations:
	#  auto download from  http://zekr.org/resources.html to ./store/recitations  + VerseByVerse recitations list
	@echo "todo"

download_quranic_corpus:
	# Qimport.Downloader
	@echo "todo"

download_tanzil:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -d tanzil_simple_clean $(STORE_PATH)
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -d tanzil_uthmani $(STORE_PATH)
	

##  build indexes 
index_all: index_main index_extend index_word 
	@echo "done;"

index_main:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -x main $(DB_PATH)main.db $(INDEX_PATH)main/

index_extend:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -x extend $(STORE_PATH)Translations/ $(INDEX_PATH)extend/
	
index_word:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -x word $(DB_PATH)main.db $(INDEX_PATH)word/
	
## build spellers
speller_all: speller_aya speller_subject speller_word
	@echo "done;"

speller_aya:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -p aya  $(INDEX_PATH)main/

speller_subject:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -p subject  $(INDEX_PATH)main/

speller_word:
	export PYTHONPATH=$(API_PATH) ;	python $(QIMPORT) -p word  $(INDEX_PATH)word/
	


## build help
help_all: help_epydoc help_sphinx

help_epydoc:
	mkdir -p output/$(VERSION);cd $(API_PATH); epydoc   --html -v --graph all --no-sourcecode     --show-imports  -n alfanous -u alfanous.org  . ;  zip -9   alfanous-epydoc.zip ./html/* ;	mv -f alfanous-epydoc.zip ../output/$(VERSION)/ ; rm -r ./html
	
help_sphinx:
	mkdir -p output/$(VERSION);cd ./docs ; make dirhtml;  zip -9   alfanous-sphinx-doc.zip ./_build/dirhtml/* ; mv -f alfanous-sphinx-doc.zip ../output/$(VERSION)/ ; rm -r  ./_build/dirhtml

## Qt forms ,dialogs and resources compilation  
# PyQt is needed  
# apt-get install pyqt4-dev-tools  pyqt-tools  
qt_all:	 qt_rcc
	
qt_rcc:
	pyrcc4 ./resources/images/main.qrc -o $(DESKTOP_INTERFACE_PATH)main_rc.py

# localization files
local_pot_all: local_desktop_pot local_mobile_pot

local_desktop_pot:
	xgettext $(DESKTOP_INTERFACE_PATH)*.py  --default-domain=alfanousQT --language=Python --keyword=n_ 
	mkdir localization/pot_files/alfanousQTv$(VERSION)
	mv alfanousQT.po localization/pot_files/alfanousQTv$(VERSION)/alfanousQTv$(VERSION).pot
	
local_mobile_pot:
	@if [ ! -d "./localization/pot_files/alfanousMWUIv$(VERSION)/" ]; then mkdir ./localization/pot_files/alfanousMWUIv$(VERSION)/; fi
	xgettext -kT_ --from-code utf-8 -L PHP --no-wrap --package-name="AlfanousMobileWUI" --package-version=$(VERSION) -d alfanousMWUI -o ./localization/pot_files/alfanousMWUIv$(VERSION)/alfanousMWUIv$(VERSION).pot $(MOBILE_WUI_PATH)*.php

local_mo_download:
	@echo "todo"
	#wget ; mv to /localization/locale

##   make packages
dist_all: dist_egg_all dist_deb dist_rpm dist_sis dist_xpi  dist_app

# generate all extentions and API's eggs
dist_egg_all: dist_egg_api  dist_egg_pycorpus  dist_egg_pyzekr dist_egg_qimport dist_egg_desktop
 

# python egg for API
dist_egg_api: 
	cd $(API_PATH)alfanous ; python setup.py bdist_egg 
	mkdir -p output/$(VERSION) ; mv $(API_PATH)alfanous/dist/*.egg ./output/$(VERSION)
	@echo  "NOTE: you can find the generated egg in ./output"
	
# python egg for PyCorpus extension
dist_egg_pycorpus: 
	cd $(API_PATH)PyCorpus ; python setup.py bdist_egg 
	mkdir -p output/$(VERSION) ; mv $(API_PATH)PyCorpus/dist/*.egg ./output/$(VERSION)
	@echo  "NOTE: you can find the generated egg in ./output"
	

# python egg for PyZekrModels extension
dist_egg_pyzekr: 
	cd $(API_PATH)PyZekrModels ; python setup.py bdist_egg 
	mkdir -p output/$(VERSION) ; mv $(API_PATH)PyZekrModels/dist/*.egg ./output/$(VERSION)
	@echo  "NOTE: you can find the generated egg in ./output"
	
# python egg for Qimport extension
dist_egg_qimport: 
	cd $(API_PATH)alfanous-import ; python setup.py bdist_egg 
	mkdir -p output/$(VERSION) ; mv $(API_PATH)alfanous-import/dist/*.egg ./output/$(VERSION)
	@echo  "NOTE: you can find the generated egg in ./output"

# python egg for alfanousDesktop interface
dist_egg_desktop: 
	cd $(DESKTOP_INTERFACE_PATH) ; python setup.py bdist_egg 
	mkdir -p output/$(VERSION) ; mv $(DESKTOP_INTERFACE_PATH)dist/*.egg ./output/$(VERSION)
	@echo  "NOTE: you can find the generated egg in ./output"
 
# Debian package for AlfanousDesktop
dist_deb: 
	dpkg-buildpackage
	

# Redhat package for AlfanousDesktop
dist_rpm:  
	@echo "todo"
	#cd $(DESKTOP_INTERFACE_PATH) ; python setup.py bdist_rpm
	#cd $(DESKTOP_INTERFACE_PATH) ; python setup.py bdist_rpm 
	
# MacOs application 
## need distutils  and py2app 
## apt-get install python-distutils*
## easy_install py2app
dist_app:  
	@echo "todo using py2app"
	# cd $(DESKTOP_INTERFACE_PATH) ; python setup.py py2app

# Nokia symbian package for alfanousPyS60 #required python2.5 
dist_sis: 
	 #work only with python2.5
	 #cd ./interfaces/mobile/Nokia\ S60/alfanousS60 ; python2.5 ensymble.py py2sis --uid=0x07342651 --appname=AlfanousS60 --version=$(VERSION) --lang=EN  --caption="Alfanous - Quranic Search Engine" --vendor="Alfanous.org" main.py AlfanousS60.sis #--icon=icon.svg  --cert=mycert.cer --privkey=mykey.key  
	 @echo "todo"
	
	
# Firefox toolbar
dist_xpi:
	cd ./interfaces/toolbars/firefox/chrome ; zip -r alfanoustoolbar.jar content/* skin/*
	cd ./interfaces/toolbars/firefox ; zip alfanous_toolbar_$(VERSION).xpi install.rdf chrome.manifest chrome/alfanoustoolbar.jar
	mkdir output/$(VERSION) ; mv ./interfaces/toolbars/firefox/alfanous_toolbar_$(VERSION).xpi ./output/$(VERSION)


## installation
	
install_all: install_api install_desktop install_web
	

install_api: 
	cd   "$(API_PATH)alfanous" ; python setup.py  install
	
install_desktop:  install_api qt_all  local_mo_download
	cd  $(DESKTOP_INTERFACE_PATH); sudo python setup.py install
	cp ./resources/launchers/alfanousDesktop $(DESTDIR)$(PREFIX)/bin/
	cp ./resources/launchers/alfanous.desktop $(DESTDIR)$(PREFIX)/share/applications/
	cp ./resources/AlFanous.png  $(DESTDIR)$(PREFIX)/share/pixmaps/
	cp ./resources/fonts/* $(DESTDIR)$(PREFIX)/share/fonts/
	#test installation
	alfanousDesktop &
	

##  don't use it!!
install_json2: install_api #install_index install_config 
	cd $(API_PATH)alfanous-cgi ;  mkdir -p $(WEB_CGI_INSTALL_PATH); cp  -r alfanous_json2.py $(WEB_CGI_INSTALL_PATH);
	#cd ./interfaces/web/ ;  cp  htaccess $(WEB_INSTALL_PATH)".htaccess"
	#cd ./interfaces/web/ ;  vi alfanous ; cp alfanous /etc/apache2/sites-available/ #configure well this file 

	chmod +x $(WEB_CGI_INSTALL_PATH)alfanous_json2.py 
	sed -i 's/\"cgitb.enable\(\)\"/cgitb.enable\(\)/g' "$(WEB_CGI_INSTALL_PATH)alfanous_json2.py"
	sed -i 's/\.\/indexes/\/usr\/share\/alfanous\-indexes/g' "$(WEB_CGI_INSTALL_PATH)alfanous_json2.py"	
	sed -i 's/\.\/configs/\/usr\/share\/alfanous\-config/g' "$(WEB_CGI_INSTALL_PATH)alfanous_json2.py"	
   
	#a2dissite alfanous
	#a2ensite alfanous
	#service apache2 reload
	#echo "127.0.0.1 alfanous.local" >> /etc/hosts ## must check existance first!!
	#xdg-open http://alfanous.local/ &  ##launch default browser for test

##  don't use it!!
install_wui: #install_json
	#rm -r  $(WEB_INSTALL_PATH)
	mkdir -p $(WEB_INSTALL_PATH)
	#cd ./interfaces/web/ ;  cp ./AGPL $(WEB_INSTALL_PATH)
	cd ./interfaces/web/ ;  cp  -r wui  $(WEB_INSTALL_PATH) 
	#cd ./interfaces/web/ ;  vi alfanous ; cp alfanous /etc/apache2/sites-available/ #configure well this file 
	#chmod 755 -R $(WEB_INSTALL_PATH)
	cd $(WEB_INSTALL_PATH);  cd wui; sed -i 's/www\.alfanous\.org\/json/alfanous\.local\/cgi\-bin\/alfanous\_json\.py/g' index.*
	#echo "127.0.0.1 alfanous.local" >> /etc/hosts ## must check existance first!!
	#xdg-open http://alfanous.local/ &  ##launch default browser for test
