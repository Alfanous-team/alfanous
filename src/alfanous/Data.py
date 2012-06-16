'''
Created on Jun 15, 2012

@author: assem


TODO build paths based on running platform
'''
from alfanous.main import QuranicSearchEngine, FuzzyQuranicSearchEngine, \
                         TraductionSearchEngine, WordSearchEngine
import os, json


# default paths
class Paths:
    """ """
    ROOT = os.path.dirname( __file__ ) + "/"
    HOME = os.getenv( 'USERPROFILE' ) or os.getenv( 'HOME' ) + "/.alfanous/"
    ROOT_INDEX = ROOT + "indexes/"
    ROOT_CONFIG = ROOT + "configs/"
    QSE_INDEX = ROOT_INDEX + "main/"
    TSE_INDEX = ROOT_INDEX + "extend/"
    WSE_INDEX = ROOT_INDEX + "word/"
    RECITATIONS_LIST_FILE = ROOT_CONFIG + "recitations.js"
    TRANSLATIONS_LIST_FILE = ROOT_CONFIG + "translations.js"
    INFORMATION_FILE = ROOT_CONFIG + "information.js"
    HINTS_FILE = ROOT_CONFIG + "hints.js"
    STATS_FILE = HOME + "stats.js"




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


