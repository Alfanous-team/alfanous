#
# This is Alfanous Makefile
#

## Global Version of the project, must be updated in each significant change in 
## the API & Desktop Gui
VERSION=0.7.30

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

## Databases file, the databases mainly store the Quranic data in a middle 
## structure before indexing it  
DB_PATH="./resources/databases/"

## Store is the place where we're storing the Quranic data in its original 
## structure (raw data)
STORE_PATH="./store/"

## Index path, is where we put the generated indexes
INDEX_PATH=$(API_PATH)"alfanous/indexes/"



PYTHON_COMMAND="python"


## default target, it's what to do if you typed "make" without target
default: 
	@echo "choose a target:"
	@echo "edit_all \n\t to edit all resources that should humanly edited " 
	@echo "download_all \n\t to download all Quranic resources that we can't \n\t include in Git or tarball because of license or huge size" 
	@echo "build \n\t to build all indexes, update all resources, qt files, \n\t localization files"
	@echo "dist \n\t to generate all distribution files for the API and \n\t the Desktop interface"


##  This target is to edit text resources before building, which are:
# 1. api information, see update_information
# 2. globl hints (deprecated), see update_hints
# 3. List of translations to be downloaded, see  update_translations_to_download_list
edit_all:  edit_information edit_hints edit_translations_to_download_list

# update information manually 
edit_information:
	nano $(RESOURCES_PATH)information.json

# update hints manually
edit_hints:
	nano $(CONFIGS_PATH)hints.json


# update downloading translation list manually
edit_translations_to_download_list:
	nano $(STORE_PATH)translations/translations.list



## this target is to build all what have to be built:
# 1. Update Quranic resources needed for indexing phase, see update_pre_build
# 2. Generate all Indexes, see  index_all
# 4. Update all resources that must be updated after indexing phase or independently, see  update_post_build
build: update_pre_build index_all  update_post_build




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
download_all: download_translations   download_tanzil

download_translations:
	#  download from  http://zekr.org/resources.html to ./store/traductions
	cd $(STORE_PATH)translations;  wget -i translations.list


download_tanzil:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -d tanzil_simple_clean $(STORE_PATH)tanzil_simple_clean.xml
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -d tanzil_uthmani $(STORE_PATH)tanzil_uthmani.xml



##  update resources that must be updated after (or independent to) indexing phase, which are:
# 1. list of indexed translations, see update_translations_indexed_list
# 2. list of offline recitations, see update_recitations_offline_list
# 3. list of online recitations, see update_recitations_online_list  
update_post_build:  update_dynamic_resources_postbuild update_recitations_offline_list #update_recitations_online_list   

##  update resources that must be updated before indexing phase, which are:
# 1. Quranic Arabic Corpus, see update_quranic_corpus
# 2. Linguistic resources on the form of python dictionarries to accelerate the loading , see update_dynamic_resources

update_pre_build:  construct_database update_translations_indexed_list update_dynamic_resources_prebuild   #update_quranic_corpus

# Construct database from dump file
construct_database:
	cd $(DB_PATH); rm main.db || true ; cat main.sql | sqlite3 main.db
	perl -p -w -e 's|alfanous.release|$(RELEASE)|g;s|alfanous.version|$(VERSION)|g;' $(API_PATH)alfanous/resources/information.json.in > $(API_PATH)alfanous/resources/information.json

# update list of indexed translations automatically using Importer
update_translations_indexed_list:
	echo "{}" > $(CONFIGS_PATH)translations.json
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -u translations $(INDEX_PATH)extend/  $(CONFIGS_PATH)translations.json

# update quranic corpus in the database automatically using Importer
update_quranic_corpus:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -u wordqc $(STORE_PATH)quranic-corpus-morpology.xml $(DB_PATH)main.db

# update recitations offline list TODO
update_recitations_offline_list:
	@echo "todo"

# update recitations online list automatically from the project every ayah
update_recitations_online_list:
	cd $(CONFIGS_PATH); wget http://www.everyayah.com/data/recitations.js; mv recitations.js recitations.json

# update dynamic resources automatically , see transfer_prebuild, transfer_postbuild
update_dynamic_resources_prebuild: transfer_prebuild
update_dynamic_resources_postbuild: transfer_postbuild
	
## build dynamic_resources by transferring the data from database (or indexes) to python modules, this include:
# 1. [prebuild] arabic stop words, see transfer_stopwords
# 2. [prebuild] Quranic words synonyms, see transfer_synonyms
# 3. [prebuild] Word properties [root,type], see transfer_word_props
# 4. [prebuild] Derivtion levels of Qurnic words, see transfer_derivations
# 5. [prebuild] Field names mapping Arabic to English, see transfer_ara2eng_names
# 6. [prebuild] Quranic words mapping Standard to Uthmani, see transfer_standard2uthmani
# 7. [postbuild] Different vocalizations of each quranic word, see transfer_vocalizations
transfer_all: transfer_prebuild transfer_postbuild
transfer_prebuild: transfer_stopwords transfer_synonyms transfer_word_props transfer_derivations transfer_ara2eng_names transfer_standard2uthmani
transfer_postbuild: transfer_vocalizations
	
transfer_stopwords:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -t stopwords $(DB_PATH)main.db $(RESOURCES_PATH)
	
transfer_synonyms:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -t synonyms $(DB_PATH)main.db $(RESOURCES_PATH)

transfer_word_props:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -t word_props $(DB_PATH)main.db $(RESOURCES_PATH)

transfer_derivations:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -t derivations $(DB_PATH)main.db $(RESOURCES_PATH)

transfer_vocalizations:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -t vocalizations $(DB_PATH)main.db $(INDEX_PATH)main/ $(RESOURCES_PATH)

transfer_ara2eng_names:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -t ara2eng_names $(DB_PATH)main.db $(RESOURCES_PATH)
	
transfer_standard2uthmani:
	export PYTHONPATH=$(API_PATH) ;	$(PYTHON_COMMAND) $(QIMPORT) -t std2uth_words $(DB_PATH)main.db $(RESOURCES_PATH)
	


## build all indexes:
# 1. Main index that contains all information related to Ayah or Surah, see index_main
# 2. Extended index that contains Quranic translations and offline recitations, see index_extend
# 3. Word index, contains all information related to Word, see index_word
index_all: index_main index_extend #index_word 
	@echo "done;"

index_main:
	export PYTHONPATH=$(API_PATH) ;	rm -r $(INDEX_PATH)main/; $(PYTHON_COMMAND) $(QIMPORT) -x main $(DB_PATH)main.db $(INDEX_PATH)main/

index_extend:
	export PYTHONPATH=$(API_PATH) ;	rm -r $(INDEX_PATH)extend/; $(PYTHON_COMMAND) $(QIMPORT) -x extend $(STORE_PATH)translations/ $(INDEX_PATH)extend/
index_word:
	export PYTHONPATH=$(API_PATH) ;	rm -r $(INDEX_PATH)word/; $(PYTHON_COMMAND) $(QIMPORT) -x word $(DB_PATH)main.db $(INDEX_PATH)word/


install:
	perl -p -w -e 's|alfanous.release|$(RELEASE)|g;s|alfanous.version|$(VERSION)|g;' $(API_PATH)alfanous/resources/information.json.in > $(API_PATH)alfanous/resources/information.json
	cd   "$(API_PATH)alfanous" ; $(PYTHON_COMMAND) setup.py install

# python egg for API
dist:
	perl -p -w -e 's|alfanous.release|$(RELEASE)|g;s|alfanous.version|$(VERSION)|g;' $(API_PATH)alfanous/resources/information.json.in > $(API_PATH)alfanous/resources/information.json
	cd $(API_PATH)alfanous ; rm -r dist; $(PYTHON_COMMAND) setup.py sdist bdist_wheel; twine upload dist/* -u assemch
	mkdir -p output/$(VERSION) ; mv $(API_PATH)alfanous/dist/*.egg ./output/$(VERSION)
	@echo  "NOTE: you can find the generated egg in ./output"


release: dist

