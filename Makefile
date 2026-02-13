#
# This is Alfanous Makefile
#

## Global Version of the project, must be updated in each significant change in 
## the API
VERSION=0.7.33
## Next releases:
RELEASE=$(VERSION)Kahraman

## API path, API contains all python packages 
API_PATH="./src/"

## Importer package path, the importer is the responsible of downloading quranic
## resources, updating them , indexing them.
QIMPORT=$(API_PATH)"alfanous_import/cli.py"
	
## resources & configuration files
CONFIGS_PATH=$(API_PATH)"alfanous/configs/"
RESOURCES_PATH=$(API_PATH)"alfanous/resources/"


## Store is the place where we're storing the Quranic data in its original 
## structure (raw data)
STORE_PATH="./store/"

## Index path, is where we put the generated indexes
INDEX_PATH=$(API_PATH)"alfanous/indexes/"



PYTHON_COMMAND="python"


## default target, it's what to do if you typed "make" without target
default: 
	@echo "choose a target:"
	@echo "edit \n\t to edit all resources that should humanly edited "
	@echo "download \n\t to download all Quranic resources that we can't \n\t include in Git or tarball because of license or huge size"
	@echo "build \n\t to build all indexes, update all resources, qt files, \n\t localization files"
	@echo "dist \n\t to generate all distribution files for the API and \n\t the Desktop interface"


##  This target is to edit text resources before building, which are:
# 1. api information, see update_information
# 2. globl hints (deprecated), see update_hints
# 3. List of translations to be downloaded, see  update_translations_to_download_list
edit:  edit_information edit_hints edit_translations_to_download_list

# update information manually 
edit_information:
	nano $(RESOURCES_PATH)information.json

# update hints manually
edit_hints:
	nano $(CONFIGS_PATH)hints.json


# update downloading translation list manually
edit_translations_to_download_list:
	nano $(STORE_PATH)Translations/translations.list



## this target is to build all what have to be built:
# 1. Update Quranic resources needed for indexing phase, see update_pre_build
# 2. Generate all Indexes, see  index_all
build: update_pre_build index_all




## clean temporary files after a building operation
# TODO	add all what has to be cleaned!
clean: clean_all

clean_all: clean_deb
	@echo "Cleaning..." 
	rm -rf `find . -type f -name Thumbs.db`
	rm -rf `find . -name *.pyc`
	rm -rf `find . -name *.pyo`
	rm -rf `find . -type d -name *.egg-info`
	find . -type f -iname \*.mo -exec rm {} \;
	find . -type f -iname \*.qm -exec rm {} \;


## download Quranic resources needed for Alfanous project, which are:
# 1. Quran translations from zekr.org, see download_translations
# 2. 
download: download_translations   download_tanzil

download_translations:
	#  download from  http://zekr.org/resources.html to ./store/Translations
	cd $(STORE_PATH)Translations;  wget -i translations.list


download_tanzil:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -d tanzil_simple_clean $(STORE_PATH)tanzil_simple_clean.xml
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -d tanzil_uthmani $(STORE_PATH)tanzil_uthmani.xml



##  update resources that must be updated before indexing phase, which are:
# 1. Quranic Arabic Corpus, see update_quranic_corpus
# 2. Linguistic resources on the form of python dictionarries to accelerate the loading , see update_dynamic_resources

update_pre_build:  update_translations_indexed_list

# update list of indexed translations automatically using Importer
update_translations_indexed_list:
	echo "{}" > $(CONFIGS_PATH)translations.json
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -u translations $(INDEX_PATH)extend/  $(CONFIGS_PATH)translations.json

# update quranic corpus in the database automatically using Importer
update_quranic_corpus:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -u wordqc $(STORE_PATH)quranic-corpus-morpology.xml $(DB_PATH)main.db



# update recitations online list automatically from the project every ayah
update_recitations_online_list:
	cd $(CONFIGS_PATH); wget http://www.everyayah.com/data/recitations.js; mv recitations.js recitations.json


## build all indexes:
# 1. Main index that contains all information related to Ayah or Surah, see index_main
# 2. Extended index that contains Quranic translations and offline recitations, see index_extend
# 3. Word index, contains all information related to Word, see index_word
index_all: index_main index_extend #index_word 
	@echo "done;"

index_main:
	export PYTHONPATH=$(API_PATH) ;	rm -r $(INDEX_PATH)main/; $(PYTHON_COMMAND) $(QIMPORT) -x main $(RESOURCES_PATH) $(INDEX_PATH)main/

index_extend:
	export PYTHONPATH=$(API_PATH) ;	rm -r $(INDEX_PATH)extend/; $(PYTHON_COMMAND) $(QIMPORT) -x extend $(STORE_PATH)Translations/ $(INDEX_PATH)extend/


install:
	perl -p -w -e 's|alfanous.release|$(RELEASE)|g;s|alfanous.version|$(VERSION)|g;' $(API_PATH)alfanous/resources/information.json.in > $(API_PATH)alfanous/resources/information.json
	cd   "$(API_PATH)alfanous" ; $(PYTHON_COMMAND) setup.py install

# python egg for API
dist: download build
	perl -p -w -e 's|alfanous.release|$(RELEASE)|g;s|alfanous.version|$(VERSION)|g;' $(API_PATH)alfanous/resources/information.json.in > $(API_PATH)alfanous/resources/information.json
	cd $(API_PATH)alfanous ; rm -r dist; $(PYTHON_COMMAND) setup.py  bdist_wheel; twine upload dist/* -u assemch

release: dist

