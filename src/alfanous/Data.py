'''
Created on Jun 15, 2012

TODO build paths based on running platform
'''
import os
import json
from pkg_resources import resource_filename

from alfanous.main import QuranicSearchEngine, FuzzyQuranicSearchEngine
from alfanous.main import TraductionSearchEngine, WordSearchEngine



# default paths
class Paths:
    """ """
    ROOT = os.path.dirname( __file__ )   + "/"
    HOME = ( os.getenv( 'USERPROFILE' ) or os.getenv( 'HOME' ) or "." ) + "/"
    # base paths
    ROOT_INDEX = ROOT + "indexes/"
    ROOT_CONFIG = ROOT + "configs/"
    HOME_CONFIG = HOME + ".alfanous/"
    ROOT_RESOURCE = ROOT + "resources/"
    # indexes paths
    QSE_INDEX = ROOT_INDEX + "main/"
    TSE_INDEX = ROOT_INDEX + "extend/"
    WSE_INDEX = ROOT_INDEX + "word/"
    # resources paths
    INFORMATION_FILE = ROOT_RESOURCE + "information.json"
    # configs path suffixes
    RECITATIONS_LIST_FILE = ROOT_CONFIG + "recitations.json"
    TRANSLATIONS_LIST_FILE = ROOT_CONFIG + "translations.json"
    HINTS_FILE = ROOT_CONFIG + "hints.json"
    STATS_FILE = HOME_CONFIG + "stats.json"
    STATS_REFERENCE_FILE = ROOT_CONFIG + "stats.json"



class Configs:

    @staticmethod
    def recitations( path = Paths.RECITATIONS_LIST_FILE ):
        myfile = open( path )
        return json.loads( myfile.read() ) if myfile else {}
        myfile.close()

    @staticmethod
    def translations( path = Paths.TRANSLATIONS_LIST_FILE ):
        myfile = open( path )
        return json.loads( myfile.read() ) if myfile else {}
        myfile.close()


    @staticmethod
    def hints( path = Paths.HINTS_FILE ):
        myfile = open( path )
        return json.loads( myfile.read() ) if myfile else {}

    @staticmethod
    def stats( path = Paths.STATS_FILE, ref_path = Paths.STATS_REFERENCE_FILE ):
        if os.path.exists( path ):
            myfile = open( path )
        else:
            path_dirpart = os.path.dirname( path )
            if not os.path.exists( path_dirpart ):
                os.makedirs( path_dirpart )

            ref_file = open( ref_path, "r" )
            myfile = open( path , "w+" )
            myfile.write( ref_file.read() )
            myfile.seek( 0 )
        return json.loads( myfile.read() ) if myfile else {}


class Resources:
    @staticmethod
    def information( path = Paths.INFORMATION_FILE ):
        myfile = open( path )
        return json.loads( myfile.read() ) if myfile else {}



class Indexes:
    @staticmethod
    def QSE( path = Paths.QSE_INDEX ):
        return QuranicSearchEngine( path )

    @staticmethod
    def FQSE( path = Paths.QSE_INDEX ):
        return FuzzyQuranicSearchEngine( path )

    @staticmethod
    def TSE( path = Paths.TSE_INDEX ):
        return TraductionSearchEngine( path )

    @staticmethod
    def WSE( path = Paths.WSE_INDEX ):
        return WordSearchEngine( path )


