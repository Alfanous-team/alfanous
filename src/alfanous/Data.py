'''
Created on Jun 15, 2012

TODO build paths based on running platform
'''
from alfanous.main import QuranicSearchEngine, FuzzyQuranicSearchEngine, \
                         TraductionSearchEngine, WordSearchEngine
import os, json


# default paths
class Paths:
    """ """
    ROOT = os.path.dirname( __file__ ) + "/"
    HOME = os.getenv( 'USERPROFILE' ) or os.getenv( 'HOME' ) + "/"
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
    def stats( path = Paths.STATS_FILE ):
        if os.path.exists( path ):
            myfile = open( path )
        else:
            myfile = open( path , "w+" )
            myfile.write( "{}" )
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


