# -*- coding: utf-8 -*-

##     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

##     This program is free software: you can redistribute it and/or modify
##     it under the terms of the GNU Affero General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU Affero General Public License for more details.

##     You should have received a copy of the GNU Affero General Public License
##     along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import gettext
import re
import codecs
import webbrowser

from configobj import ConfigObj

from PySide import  QtGui, QtCore, QtWebKit
from PySide.QtCore import QRect

sys.path.insert(0, "../../src") ## a relative path, development mode
sys.path.append("alfanous.egg/alfanous") ## an egg, portable
sys.path.append("./src") ## integrated

from alfanous.Outputs import Raw
## Specification of resources paths
from alfanous.Data import Paths

## Importing Qt forms
from mainform_ui import Ui_MainWindow
from preferencesDlg_ui import Ui_preferencesDlg
from aboutDlg_ui import Ui_Dialog as Ui_aboutDlg
from Templates import AYA_RESULTS_TEMPLATE, TRANSLATION_RESULTS_TEMPLATE


## force the use of utf8
reload(sys)
sys.setdefaultencoding('utf-8')

## STATIC GLOBAL variables
CONFIGPATH = ( os.getenv( 'USERPROFILE' ) or os.getenv( 'HOME' ) or "." ) + "/"
BASEPATH  =  os.path.dirname( os.path.abspath(__file__) )
LOCALPATH = BASEPATH + "/locale" #os.getenv('TEXTDOMAINDIR')
PERPAGE = 10 #results per page
RELATIONS = ["", "", u"|", u"+", u"-"]


## Localization using gettext and Qt
# QT
tr = lambda x: QtGui.QApplication.translate("Misc", x, None, QtGui.QApplication.UnicodeUTF8)
# gettext
gettext.bind_textdomain_codeset("alfanousJinjaT", "utf-8");
gettext.bindtextdomain( "alfanousJinjaT" , LOCALPATH );
gettext.textdomain( "alfanousJinjaT" );
_ = gettext.gettext
n_ = gettext.ngettext

def get_language_from_config():
        config = ConfigObj( CONFIGPATH + "/config.ini", encoding="utf-8" )
        if config.has_key( "options" ):
            return config["options"]["language"] if config["options"].has_key( "language" ) else ""
        else:
            return ""

lang = get_language_from_config()
os.environ['LANGUAGE'] = lang
os.environ['LANG'] = lang

# Load Alfanous engi
RAWoutput = Raw() # default paths

SAJDA_TYPE = {u"مستحبة":_( u"recommended" ), u"واجبة":_( u"obliged" )}

## Some functions
relate = lambda query, filter, index:"( " + unicode( query ) + " ) " + RELATIONS[index] + " ( " + filter + " ) " if  index > 1 else filter if index == 1 else unicode( query ) + " " + filter

class QUI( Ui_MainWindow ):
    """ the main UI """

    def __init__( self ):
        self.currentQuery = 0
        self.Queries = []
        self.undo_stack = []
        self.redo_stack = []
        self.style = self.get_style_from_config()

    def exit( self ):
        self.save_config()
        sys.exit()

    def get_style_from_config(self):
        config = ConfigObj( CONFIGPATH + "/config.ini", encoding="utf-8" )
        if config.has_key( "options" ):
            return config["options"]["style"] if config["options"].has_key( "style" ) else ""
        else:
            return ""

    def load_config( self ):
        """load configuration"""
        config = ConfigObj( CONFIGPATH + "/config.ini", encoding="utf-8" )
        boolean = lambda s:True if s == "True" else False

        self.o_query.clear()
        self.o_query.addItems( config["history"] if config.has_key( "history" ) else [u"الحمد لله"] )

        if config.has_key( "options" ):
            #self.o_limit.setValue( int( config["options"]["limit"] ) if config["options"].has_key( "limit" ) else 100 )
            #self.o_perpage.setValue( int( config["options"]["perpage"] ) if config["options"].has_key( "perpage" ) else 10 )
            self.style = config["options"]["style"] if config["options"].has_key( "style" ) else ""
            self.language = config["options"]["language"] if config["options"].has_key( "language" ) else ""
            self.o_autospell.setChecked(boolean(config["options"]["fuzzy"]) if config["options"].has_key( "fuzzy" ) else False)
            self.o_search_in_trads.setChecked(config["options"]["unit"] == "translation" if config["options"].has_key( "unit" ) else False)
        else:
            self.style = ""
            self.language = ""

        styles = {"": self.actionDefaultStyle.setChecked,
                "windows": self.actionWindows.setChecked,
                "motif": self.actionMotif.setChecked,
                "cde": self.actionCDE.setChecked,
                "plastique": self.actionPlastique.setChecked,
                "windowsxp": self.actionWindowsXP.setChecked,
                "macintosh": self.actionMacintosh.setChecked}
        styles[self.style](True)

        languages = {"": self.actionSystem.setChecked,
                "en": self.actionEnglish.setChecked,
                "ar": self.actionArabic.setChecked,
                "fr": self.actionFrench.setChecked,
                "id": self.actionIndonesian.setChecked,
                "es": self.actionSpanish.setChecked,
                "ms": self.actionMalay.setChecked,
                "sq": self.actionAlbanian.setChecked
                }
        languages[self.language](True)

        if config.has_key( "sorting" ):
            self.actionRelevance.setChecked( boolean( config["sorting"]["sortedbyscore"] ) if config["sorting"].has_key( "sortedbyscore" ) else True )
            self.actionPosition_in_Mus_haf.setChecked( boolean( config["sorting"]["sortedbymushaf"] ) if config["sorting"].has_key( "sortedbymushaf" ) else False )
            self.actionRevelation.setChecked( boolean( config["sorting"]["sortedbytanzil"] ) if config["sorting"].has_key( "sortedbytanzil" ) else False )
            self.actionSubject.setChecked( boolean( config["sorting"]["sortedbysubject"] ) if config["sorting"].has_key( "sortedbysubject" ) else False )
            self.actionInverse.setChecked( boolean( config["sorting"]["reverse"] )if config["sorting"].has_key( "reverse" ) else False )
        else:
            self.actionRelevance.setChecked(True)
            self.actionPosition_in_Mus_haf.setChecked(False)
            self.actionRevelation.setChecked(False)
            self.actionSubject.setChecked(False)
            self.actionInverse.setChecked(False)

        if config.has_key( "extend" ):
            self.actionPrevios_aya.setChecked( boolean( config["extend"]["prev"] ) if config["extend"].has_key( "prev" ) else False )
            self.actionNext_aya.setChecked( boolean( config["extend"]["suiv"] ) if config["extend"].has_key( "suiv" ) else False )

            self.actionWord_Info.setChecked( boolean( config["extend"]["word_stat"] )if config["extend"].has_key( "word_stat" ) else True )
            self.actionAya_Info.setChecked( boolean( config["extend"]["aya_info"] )if config["extend"].has_key( "aya_info" ) else True )
            self.actionSura_info.setChecked( boolean( config["extend"]["sura_info"] )if config["extend"].has_key( "sura_info" ) else True )
        else:
            self.actionPrevios_aya.setChecked(True)
            self.actionNext_aya.setChecked(True)
            self.actionWord_Info.setChecked(True)
            self.actionAya_Info.setChecked(True)
            self.actionSura_info.setChecked(True)

        if config.has_key( "script" ):
            self.actionUthmani.setChecked( boolean( config["script"]["uthmani"] ) if config["script"].has_key( "uthmani" ) else False )
            self.actionStandard.setChecked( boolean( config["script"]["standard"] ) if config["script"].has_key( "standard" ) else True )
        else:
            self.actionUthmani.setChecked(False)
            self.actionStandard.setChecked(True)


        if config.has_key( "widgets" ):
            self.w_features.setHidden( not boolean( config["widgets"]["features"] ) if config["widgets"].has_key( "features" ) else True )
            self.m_features.setChecked ( boolean( config["widgets"]["features"] ) if config["widgets"].has_key( "features" ) else False )
        else:
            self.w_features.setHidden(False)
            self.m_features.setChecked (True)

    def save_config( self ):
        """save configuration """
        if not os.path.isdir( CONFIGPATH ):
            os.makedirs( CONFIGPATH )
        config = ConfigObj( CONFIGPATH + "/config.ini", encoding="utf-8" )
        config["history"] = [self.o_query.itemText(i) for i in range(self.o_query.count())]

        config["options"] = {}
        config["options"]["limit"] = self.limit_group.checkedAction().text() 
        #config["options"]["perpage"] = self.perpage_group.checkedAction().text()
        config["options"]["highlight"] = self.actionHighlight_Keywords.isChecked()
        config["options"]["style"] = self.style
        config["options"]["language"] = self.language
        config["options"]["fuzzy"] = self.o_autospell.isChecked()
        config["options"]["unit"] = "translation" if self.o_search_in_trads.isChecked() else "aya"

        config["sorting"] = {}
        config["sorting"]["sortedbyscore"] = self.actionRelevance.isChecked()
        config["sorting"]["sortedbymushaf"] = self.actionPosition_in_Mus_haf.isChecked()
        config["sorting"]["sortedbytanzil"] = self.actionRevelation.isChecked()
        config["sorting"]["sortedbysubject"] = self.actionSubject.isChecked()
        #config["sorting"]["field"] = unicode( RAWoutput._fields[self.sorted_by_group.checkedAction().text()] if self.direction == "RTL" else self.sorted_by_group.checkedAction().text() )
        config["sorting"]["reverse"] = self.actionInverse.isChecked()

        config["extend"] = {}
        config["extend"]["prev"] = self.actionPrevios_aya.isChecked()
        config["extend"]["suiv"] = self.actionNext_aya.isChecked()
        config["extend"]["translation"] = self.translation_group.checkedAction().text()
        #config["extend"]["recitation"] = self.o_recitation.currentIndex()
        config["extend"]["word_stat"] = self.actionWord_Info.isChecked()
        config["extend"]["aya_info"] = self.actionAya_Info.isChecked()
        config["extend"]["sura_info"] = self.actionSura_info.isChecked()

        config["script"] = {}
        config["script"]["uthmani"] = self.actionUthmani.isChecked()
        config["script"]["standard"] = self.actionStandard.isChecked()

        config["widgets"] = {}
        config["widgets"]["features"] = not self.w_features.isHidden()
        config.write()

    def setupWebView(self):
        self.o_results = QtWebKit.QWebView(self.frame0)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.o_results.sizePolicy().hasHeightForWidth())
        self.o_results.setSizePolicy(sizePolicy)
        self.o_results.setMinimumSize(QtCore.QSize(300, 25))
        self.o_results.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.o_results.setFont(font)
        self.o_results.setProperty("cursor", QtCore.Qt.IBeamCursor)
        self.o_results.setAutoFillBackground(False)
        self.o_results.setHtml("""""")
        self.o_results.setObjectName("o_results")
        self.verticalLayout33.addWidget(self.o_results)
        self.o_results.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)

    def setupUi( self, MainWindow ):
        super( QUI, self ).setupUi( MainWindow )
        
        # fix direction for RTL languages
        self.direction = "RTL" if _( "LTR" ) == "RTL" else "LTR";

        # prepare QwebView
        self.setupWebView()

        # make sorted_by menu items as a group of radio buttons
        self.sorted_by_group = QtGui.QActionGroup( MainWindow )
        self.sorted_by_group.addAction( self.actionRelevance )
        self.sorted_by_group.addAction( self.actionRevelation )
        self.sorted_by_group.addAction( self.actionPosition_in_Mus_haf )
        self.sorted_by_group.addAction( self.actionSubject )
        self.sorted_by_group.addAction( self.actionRevelation )
        for key, val in RAWoutput._fields.items():
            field_action = QtGui.QAction(MainWindow)
            field_action.setCheckable(True)
            field_action.setChecked(False)
            field_action.setObjectName("action_field_" + val)
            if self.direction == "RTL":
                field_action.setText( key )
            else:
                field_action.setText( val )
            self.menuFields.addAction( field_action )
            self.sorted_by_group.addAction( field_action )
        # make options->script menu as a radio button
        self.script_group = QtGui.QActionGroup( MainWindow )
        self.script_group.addAction( self.actionStandard )
        self.script_group.addAction( self.actionUthmani )
        # make options->translations as a radio button
        self.translation_group = QtGui.QActionGroup( MainWindow )
        self.translation_group.addAction(self.actionTranslationNone)
        self.translation_group.addAction(self.actionTranslationDefault)
        for key, val in sorted(RAWoutput._translations.items()):
            translation_action = QtGui.QAction(MainWindow)
            translation_action.setCheckable(True)
            translation_action.setChecked(False)
            translation_action.setObjectName("action_translation_" + key)
            translation_action.setText( val + " | " + key )
            self.menuTranslation.addAction( translation_action )
            self.translation_group.addAction( translation_action )

        # make limit menu items as a group of radio buttons
        self.limit_group = QtGui.QActionGroup( MainWindow )
        self.limit_group.addAction( self.actionlimit100 )
        self.limit_group.addAction( self.actionlimit500 )
        self.limit_group.addAction( self.actionlimit1000 )
        self.limit_group.addAction( self.actionlimit6236 )

        # make perpage menu items as a group of radio buttons
        self.perpage_group = QtGui.QActionGroup( MainWindow )
        self.perpage_group.addAction( self.actionpp1 )
        self.perpage_group.addAction( self.actionpp10 )
        self.perpage_group.addAction( self.actionpp20 )
        self.perpage_group.addAction( self.actionpp50 )
        self.perpage_group.addAction( self.actionpp100 )

        # make options->script menu as a radio button
        self.style_group = QtGui.QActionGroup( MainWindow )
        self.script_group.addAction( self.actionDefaultStyle )
        self.script_group.addAction( self.actionWindows )
        self.script_group.addAction( self.actionMotif )
        self.script_group.addAction( self.actionCDE )
        self.script_group.addAction( self.actionPlastique )
        self.script_group.addAction( self.actionWindowsXP )
        self.script_group.addAction( self.actionMacintosh )

        # make options->languages menu as a radio button
        self.language_group = QtGui.QActionGroup( MainWindow )
        self.language_group.addAction( self.actionSystem )
        self.language_group.addAction( self.actionEnglish )
        self.language_group.addAction( self.actionArabic )
        self.language_group.addAction( self.actionFrench )
        self.language_group.addAction( self.actionIndonesian )
        self.language_group.addAction( self.actionSpanish )
        self.language_group.addAction( self.actionMalay  )

        if self.direction == "RTL":
            MainWindow.setLayoutDirection( QtCore.Qt.RightToLeft )
            self.centralwidget.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.menubar.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.w_features.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.o_query.setLayoutDirection( QtCore.Qt.RightToLeft )
        QtCore.QObject.connect( self.o_search, QtCore.SIGNAL( "clicked()" ), self.search_all )
        QtCore.QObject.connect( self.actionCopy_Query, QtCore.SIGNAL( "triggered()" ), self.copy_query )
        QtCore.QObject.connect( self.actionCopy_Page, QtCore.SIGNAL( "triggered()" ), self.copy_result )
        QtCore.QObject.connect( self.actionUndo_Query, QtCore.SIGNAL( "triggered()" ), self.undo_query )
        QtCore.QObject.connect( self.actionRedo_Query, QtCore.SIGNAL( "triggered()" ), self.redo_query )
        QtCore.QObject.connect( self.a_save_txt, QtCore.SIGNAL( "triggered()" ), self.save_results_txt )
        QtCore.QObject.connect( self.o_page, QtCore.SIGNAL( "valueChanged(int)" ), self.search_all )
        QtCore.QObject.connect( self.o_chapter, QtCore.SIGNAL( "activated(QString)" ), self.topics )
        QtCore.QObject.connect( self.o_topic, QtCore.SIGNAL( "activated(QString)" ), self.subtopics )
        QtCore.QObject.connect( self.o_sajdah_exist, QtCore.SIGNAL( "activated(int)" ), self.sajda_enable )
        QtCore.QObject.connect( self.o_struct_as, QtCore.SIGNAL( "activated(QString)" ), self.setstructborn )
        QtCore.QObject.connect( self.actionDefaultStyle, QtCore.SIGNAL( "triggered()" ), lambda: self.changeStyle("") )
        QtCore.QObject.connect( self.actionWindows, QtCore.SIGNAL( "triggered()" ), lambda: self.changeStyle("windows") )
        QtCore.QObject.connect( self.actionMotif, QtCore.SIGNAL( "triggered()" ), lambda: self.changeStyle("motif") )
        QtCore.QObject.connect( self.actionCDE, QtCore.SIGNAL( "triggered()" ), lambda: self.changeStyle("cde") )
        QtCore.QObject.connect( self.actionPlastique, QtCore.SIGNAL( "triggered()" ), lambda: self.changeStyle("plastique") )
        QtCore.QObject.connect( self.actionWindowsXP, QtCore.SIGNAL( "triggered()" ), lambda: self.changeStyle("windowsxp") )
        QtCore.QObject.connect( self.actionMacintosh, QtCore.SIGNAL( "triggered()" ), lambda: self.changeStyle("macintosh") )
        QtCore.QObject.connect( self.actionSystem, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("") )
        QtCore.QObject.connect( self.actionEnglish, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("en") )
        QtCore.QObject.connect( self.actionArabic, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("ar") )
        QtCore.QObject.connect( self.actionFrench, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("fr") )
        QtCore.QObject.connect( self.actionIndonesian, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("id") )
        QtCore.QObject.connect( self.actionSpanish, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("es") )
        QtCore.QObject.connect( self.actionMalay, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("ms") )
        QtCore.QObject.connect( self.actionAlbanian, QtCore.SIGNAL( "triggered()" ), lambda: self.changeLanguage("sq") )
        
        QtCore.QObject.connect( self.actionpp10, QtCore.SIGNAL( "triggered()" ), self.changePERPAGE )
        QtCore.QObject.connect( self.actionpp20, QtCore.SIGNAL( "triggered()" ), self.changePERPAGE )
        QtCore.QObject.connect( self.actionpp50, QtCore.SIGNAL( "triggered()" ), self.changePERPAGE )
        QtCore.QObject.connect( self.actionpp100, QtCore.SIGNAL( "triggered()" ), self.changePERPAGE )
        QtCore.QObject.connect( self.actionpp1, QtCore.SIGNAL( "triggered()" ), self.changePERPAGE )
        QtCore.QObject.connect( self.o_struct_from, QtCore.SIGNAL( "valueChanged(int)" ), self.struct_to_min )
        QtCore.QObject.connect( self.o_stat_from, QtCore.SIGNAL( "valueChanged(int)" ), self.stat_to_min )
        QtCore.QObject.connect( self.m_exit, QtCore.SIGNAL( "triggered()" ), self.exit )
        QtCore.QObject.connect( self.m_help, QtCore.SIGNAL( "triggered()" ), self.help )
        QtCore.QObject.connect( self.m_about, QtCore.SIGNAL( "triggered(bool)" ), self.about )

        QtCore.QObject.connect( self.actionShare_an_Idea, QtCore.SIGNAL( "triggered()" ), self.share_an_idea )
        QtCore.QObject.connect( self.actionAsk_a_Question, QtCore.SIGNAL( "triggered()" ), self.ask_a_question)
        QtCore.QObject.connect( self.action_Say_Thanks, QtCore.SIGNAL( "triggered()" ), self.say_thanks )
        QtCore.QObject.connect( self.actionReport_a_Problem, QtCore.SIGNAL( "triggered()" ), self.report_a_problem )
        QtCore.QObject.connect( self.actionTranslate, QtCore.SIGNAL( "triggered()" ), self.contribute_translate )
        QtCore.QObject.connect( self.actionCode, QtCore.SIGNAL( "triggered()" ), self.contribute_code )

        QtCore.QObject.connect( self.a_save, QtCore.SIGNAL( "triggered()" ), self.save_results )
        QtCore.QObject.connect( self.a_print, QtCore.SIGNAL( "triggered()" ), self.print_results )

        QtCore.QObject.connect( self.o_add2query_advanced, QtCore.SIGNAL( "clicked()" ), self.add2query_advanced )
        QtCore.QObject.connect( self.o_add2query_struct, QtCore.SIGNAL( "clicked()" ), self.add2query_struct )
        QtCore.QObject.connect( self.o_add2query_stat, QtCore.SIGNAL( "clicked()" ), self.add2query_stat )
        QtCore.QObject.connect( self.o_add2query_subject, QtCore.SIGNAL( "clicked()" ), self.add2query_subject )
        QtCore.QObject.connect( self.o_add2query_word, QtCore.SIGNAL( "clicked()" ), self.add2query_word )
        QtCore.QObject.connect( self.o_add2query_misc, QtCore.SIGNAL( "clicked()" ), self.add2query_misc )
        QtCore.QObject.connect( self.o_add2query_predefined, QtCore.SIGNAL( "clicked()" ), self.add2query_predefined )

        QtCore.QObject.connect( self.o_results, QtCore.SIGNAL( "linkClicked(QUrl)" ), self.link_is_clicked )


        self.sura_list =  ["%s (%s)" % t for t in zip(RAWoutput._surates["Arabic"], RAWoutput._surates["Romanized"])] if self.direction == "RTL" \
            else  ["%s (%s)" % t for t in zip(RAWoutput._surates["Romanized"],RAWoutput._surates["English"])]
        self.o_sura_name.addItems( self.sura_list )
        self.o_predefined_sura.addItems(RAWoutput._surates["Arabic"] if self.direction == "RTL" else RAWoutput._surates["Romanized"] )
        self.o_chapter.addItems( RAWoutput._chapters )
        self.o_word_root.addItems( RAWoutput._roots )
        self.o_predefined_root.addItems(RAWoutput._roots)
        self.load_config()

    def copy_query(self):
		text_C = self.o_query.currentText()
		cb = QtGui.QApplication.clipboard()
		cb.clear(mode=cb.Clipboard )
		cb.setText(text_C, mode=cb.Clipboard)

    def copy_result(self):
		page_C = self.o_results.page()
		frame_C = page_C.mainFrame()
		text_C = frame_C.toPlainText ()
		cb = QtGui.QApplication.clipboard()
		cb.clear(mode=cb.Clipboard )
		cb.setText(text_C, mode=cb.Clipboard)
	
    def undo_query(self):
		self.o_query.setCurrentIndex(self.o_query.currentIndex ()+1)
		self.search_no_undo(log = False)

    def redo_query(self):
		self.o_query.setCurrentIndex(self.o_query.currentIndex ()-1)
		self.search_no_undo(log = False)

    def link_is_clicked(self, url):
        new_query = url.toString()
        if new_query.startswith("about:blank"): # Windows add about:blank to urls not starting by X://
            new_query = new_query.strip("about:blank")
        if new_query.startswith("#aya#"):
            self.o_search_in_ayas.setChecked(True)
            new_query = new_query.strip("#aya#")
        elif new_query.startswith("#translation#"):
            self.o_search_in_trads.setChecked(True)
            new_query = new_query.strip("#translation#")
        self.o_query.setEditText(new_query)
        self.o_page.setValue(1)
        self.search_all()

    def search_all( self, page = 1 , log = True):
        """
        The main search function
        """
        if (log):
            # add to undo stack
            if self.o_query.currentText() in self.undo_stack:
                self.undo_stack.remove( self.o_query.currentText() )
            self.undo_stack.insert( 0, self.o_query.currentText() )
        self.o_query.clear()
        self.o_query.addItems( self.undo_stack )
        self.o_query.setCurrentIndex( 0 )

        limit = int( self.limit_group.checkedAction().text() )

        suggest_flags = {
                "action":"suggest",
                "query": self.o_query.currentText()
                }
        suggestion_output = RAWoutput.do( suggest_flags )

        #search verses
        results, terms = None, []
        aya_search_flags = {"action":"search",
                 "query": unicode( self.o_query.currentText() ),
                 "sortedby":"score" if self.actionRelevance.isChecked() \
                        else "mushaf" if self.actionPosition_in_Mus_haf.isChecked() \
                        else "tanzil" if self.actionRevelation.isChecked() \
                        else "subject" if self.actionSubject.isChecked() \
                        else unicode( RAWoutput._fields[self.sorted_by_group.checkedAction().text()] if self.direction == "RTL" else self.sorted_by_group.checkedAction().text() ),
                 "page": self.o_page.value(),
                 "reverse_order": self.actionInverse.isChecked(),
                 "word_info":self.actionWord_Info.isChecked(),
                 "highlight": "css" if self.actionHighlight_Keywords.isChecked() else None,
                 "script": "uthmani" if self.actionUthmani.isChecked()
                            else "standard",
                 "prev_aya":self.actionPrevios_aya.isChecked(),
                 "next_aya": self.actionNext_aya.isChecked(),
                 "sura_info": self.actionSura_info.isChecked(),
                 "aya_position_info":  self.actionAya_Info.isChecked(),
                 "aya_theme_info":  self.actionAya_Info.isChecked(),
                 "aya_stat_info":  self.actionAya_Info.isChecked(),
                 "aya_sajda_info":  self.actionAya_Info.isChecked(),
                 "translation": "en.shakir"  if self.actionTranslationDefault.isChecked() else "" if self.actionTranslationNone.isChecked() else self.translation_group.checkedAction().text().split("|")[1][0:],
                 "fuzzy": self.o_autospell.isChecked(),
                 "word_info": self.actionWord_Info.isChecked(),
                 "romanization":"buckwalter"

                 }

        aya_results = RAWoutput.do( aya_search_flags )
        
        #search translations
        trans_search_flags = {"action":"search",
                              "unit": "translation",
                              "aya": True,
                 "query": unicode( self.o_query.currentText() ),
                 "page": self.o_page.value(),
                 "highlight": "css" if self.actionHighlight_Keywords.isChecked() else None,
                 }

        trans_results = RAWoutput.do( trans_search_flags )

        results = aya_results if self.o_search_in_ayas.isChecked() else trans_results
        extra_results =  trans_results if self.o_search_in_ayas.isChecked() else aya_results
        flags = aya_search_flags if self.o_search_in_ayas.isChecked() else trans_search_flags

        if results["error"]["code"]==0:
            #outputs
            self.o_time.display( results["search"]["runtime"] )
            self.o_resnum.display( results["search"]["interval"]["total"] )

            # get page
            numpagereal = ( results["search"]["interval"]["total"] - 1 ) / PERPAGE + 1
            numpagelimit = ( limit - 1 ) / PERPAGE + 1
            numpage = numpagelimit if numpagelimit < numpagereal else numpagereal
            self.o_numpage.display( numpage )
            self.o_page.setMinimum( 1 if numpage else 0 )
            self.o_page.setMaximum( numpage )
            #self.o_page.setValue(  )

            template_vars = {
                            "results": results, 
                            "suggestions":suggestion_output ,
                            "extra_results": extra_results,
                            "flags":flags,
                            "_": lambda x:x 
                            }
            results_template = AYA_RESULTS_TEMPLATE if self.o_search_in_ayas.isChecked() else TRANSLATION_RESULTS_TEMPLATE
            t = results_template.render(template_vars)
        else:
            t = "Error ("+ str(results["error"]["code"]) + "):" + results["error"]["msg"]
            self.o_time.display( 0 )
            self.o_resnum.display( 0 )
        self.o_results.setHtml( t )

    def topics( self, chapter ):
        first = self.o_topic.itemText( 0 )
        list = [item for item in RAWoutput.QSE.list_values( "topic", conditions = [( "chapter", unicode( chapter ) )] ) if item]
        list.insert( 0, first )
        self.o_topic.clear()
        self.o_topic.addItems( list )
        pass

    def subtopics( self, topic ):

        first = self.o_subtopic.itemText( 0 )
        list = [item for item in RAWoutput.QSE.list_values( "subtopic", conditions = [( "topic", unicode( topic ) ), ] ) if item]
        list.insert( 0, first )
        self.o_subtopic.clear()
        self.o_subtopic.addItems( list )
        pass

    def changePERPAGE( self ):
        global PERPAGE
        PERPAGE = int( self.perpage_group.checkedAction().text() )

    def changeStyle( self, style ):
        self.style = style
        mb = QtGui.QMessageBox(QtGui.QMessageBox.Warning, unicode(_(u"Applying skin")), unicode(_(u"You should restart application in order for the skin to take effect")), buttons = QtGui.QMessageBox.Ok)
        #mb.addButton(QtGui.QMessageBox.Cancel)
        #[, buttons=QMessageBox.NoButton[, parent=None[, flags=Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint]]]
        ret = mb.exec_()
        if ret == QtGui.QMessageBox.Ok:
            pass

    def changeLanguage( self, lang ):
        self.language = lang
        mb = QtGui.QMessageBox(QtGui.QMessageBox.Warning, unicode(_(u"Applying language")), unicode(_(u"You should restart application in order for the language to take effect")), buttons = QtGui.QMessageBox.Ok)
        #mb.addButton(QtGui.QMessageBox.Cancel)
        #[, buttons=QMessageBox.NoButton[, parent=None[, flags=Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint]]]
        ret = mb.exec_()
        if ret == QtGui.QMessageBox.Ok:
            pass

    def add2query_advanced( self ):
        """
        """
        filter = ""

        text = unicode( self.o_feature_text.text() )
        word_re = re.compile( "[^ \n\t]+" )
        words = word_re.findall( text )
        if text:
            if self.o_synonyms.isChecked():
                for word in words:filter += " ~" + word
            elif self.o_vocalization.isChecked():
                filter = u" آية_:'" + text + "'"
            elif self.o_phrase.isChecked():
                filter = " \"" + text + "\""
            elif self.o_partofword.isChecked():
                for word in words: filter = " *" + word + "*"
            elif self.o_allwords.isChecked():
                filter = u" + ".join( words )
            elif self.o_somewords.isChecked():
                filter = u" | ".join( words )
            elif self.o_nowords.isChecked():
                filter = u" - ".join( words )
            elif self.o_derivation_light.isChecked():
                for word in words:filter += " >" + word
            elif self.o_derivation_deep.isChecked():
                for word in words:filter += " >>" + word
            elif self.o_boost.isChecked():
                filter = " (" + text + ")^2"

        index = self.o_relation_advanced.currentIndex()
        newquery = relate( self.o_query.currentText(), filter, index )

        if text:
            self.o_query.setEditText( newquery )

    def add2query_struct( self ):
        """
         """
        filter = ""
        items_fields = [u"رقم_الآية", u"رقم", u"ركوع", u"رقم_السورة", u"صفحة", u"ربع", u"حزب", u"جزء", u"منزل"]

        index = self.o_struct_as.currentIndex()
        vfrom = self.o_struct_from.value()
        vto = self.o_struct_to.value()

        filter = u"  " + items_fields[index] + u":[" + unicode( vfrom ) + u" إلى  " + unicode( vto ) + "]"


        index = self.o_relation_struct.currentIndex()
        newquery = relate( self.o_query.currentText(), filter, index )

        self.o_query.setEditText( newquery )


    def add2query_subject( self ):
        """        """
        filter = ""
        if self.o_chapter.currentIndex() != 0:
            filter += u"  فصل:\"" + unicode( self.o_chapter.currentText() ) + "\""


        if self.o_topic.currentIndex() > 0:
            filter += u" + فرع:\"" + unicode( self.o_topic.currentText() ) + "\""


        if self.o_subtopic.currentIndex() > 0:
            filter += u" + باب:\"" + unicode( self.o_subtopic.currentText() ) + "\""

        index = self.o_relation_subject.currentIndex()
        newquery = relate( self.o_query.currentText(), filter, index )
        self.o_query.setEditText( newquery )


    def add2query_stat( self ):
        """
         """
        filter = ""
        i = self.o_stat_num.currentIndex()
        j = self.o_stat_in.currentIndex()
        vfrom = self.o_stat_from.value()
        vto = self.o_stat_to.value()

        STATIN = ["", u"آ", u"س"]
        STATNUM = ["", u"ح", u"ك", u"ج", u"آ", u"ر"]
        if i * j != 0 and i / 4 + 1 <= j:
            filter += u" " + STATNUM[i] + "_" + STATIN[j] + u":[" + str( vfrom ) + u" إلى " + str( vto ) + u"]"

        index = self.o_relation_stat.currentIndex()
        newquery = relate( self.o_query.currentText(), filter, index )
        self.o_query.setEditText( newquery )

    def add2query_misc( self ):
        """         """
        filter_ = u""

        if self.o_sura_name.currentIndex() != 0:
            if self.direction == "RTL":
                filter_ += u"  سورة:\"" + unicode( RAWoutput._surates["Arabic"][self.o_sura_name.currentIndex() - 1] ) + "\""
            else:
                filter_ += u"  sura:\"" + unicode( RAWoutput._surates["Romanized"][self.o_sura_name.currentIndex() - 1] ) + "\""

        sura_types_ar = [u"", u"مدنية", u"مكية"]
        sura_types_en = [u"", u"Medinan", u"Meccan"]
        if self.o_tanzil.currentIndex() != 0:
            if self.direction == "RTL":
                filter_ += u"  نوع_السورة:" + unicode( sura_types_ar[self.o_tanzil.currentIndex()] )
            else:
                filter_ += u"  sura_type:" + unicode( sura_types_en[self.o_tanzil.currentIndex()] )

        yes_no = ["", u"لا", u"نعم"]
        sajdah_types = ["", u"مستحبة", u"واجبة"]
        if self.o_sajdah_exist.currentIndex() != 0:
            if self.o_sajdah_type.currentIndex() == 0:
                filter_ += u"  سجدة:" + unicode( yes_no[self.o_sajdah_exist.currentIndex()] )
            else:
                filter_ += u"  نوع_السجدة:" + unicode( sajdah_types[self.o_sajdah_type.currentIndex()] )

        index = self.o_relation_misc.currentIndex()
        newquery = relate( self.o_query.currentText(), filter_, index )
        if filter_:
            self.o_query.setEditText( newquery )


    def add2query_predefined( self ):
        """ Predefined Queries in Advanced search panel """
        filter_ = u""
        if self.o_predefined_goto.isChecked():
            if self.direction == "RTL":
                filter_ = u'سورة:"%s" +  رقم_الآية:%d' % (self.o_predefined_sura.currentText() , self.o_predefined_aya.value())
            else:
                filter_ = u'sura:"%s" +  aya_id:%d' % (self.o_predefined_sura.currentText() , self.o_predefined_aya.value()) 
        elif self.o_predefined_all_deriv.isChecked():
            filter_ = ">>" + self.o_predefined_root.currentText().strip("\t ")
        elif self.o_predefined_respect_tashkeel.isChecked():
            filter_ = ( u"آية_:'" if self.direction == "RTL" else u"aya_:'" ) + self.o_predefined_vocalized_word.text() + "'"
        elif self.o_predefined_longest_words.isChecked():
            filter_ = u"؟؟؟؟؟؟؟؟؟؟؟" if self.direction == "RTL" else "???????????"
        elif self.o_predefined_shortest_words.isChecked():
            filter_ = u"؟" if self.direction == "RTL" else u"?"
        elif self.o_predefined_all_sajadate.isChecked():
            filter_ = u"سجدة:نعم" if self.direction == "RTL" else u"sajda:نعم"

        newquery = relate( self.o_query.currentText(), filter_, 1 )
        if filter_:
            self.o_query.setEditText( newquery )

    def add2query_word( self ):
        filter_ = ""
        root = unicode( self.o_word_root.currentText() )

        type_values = [u"اسم", u"فعل", u"أداة"]
        type_ = type_values[self.o_word_type.currentIndex()]
        filter_ = u" {" + root + u"،" + type_ + u"}"

        index = self.o_relation_word.currentIndex()
        newquery = relate( self.o_query.currentText(), filter_, index )
        if root:
            self.o_query.setEditText( newquery )

    def setstructborn( self ):
        items_max = [286, 6236, 565, 114, 604, 240, 60, 30, 7]
        max = items_max[self.o_struct_as.currentIndex()]
        self.o_struct_from.setMaximum( max )
        self.o_struct_to.setMaximum( max )

    def struct_to_min( self, nb ):
        self.o_struct_to.setMinimum( nb )

    def stat_to_min( self, nb ):
        self.o_stat_to.setMinimum( nb )

    def sajda_enable( self, index ):
        if index == 2:
            self.o_sajdah_type.setEnabled( True )
        else:
            self.o_sajdah_type.setDisabled( True )

    def save_results( self ):
        """save as html file"""
        diag = QtGui.QFileDialog()
        diag.setAcceptMode( diag.AcceptSave )
        diag.setFileMode( diag.AnyFile )
        diag.setFilter( "*.html" )
        #filenames = ["./results.html    "]
        if ( diag.exec_() ):
            filenames = diag.selectedFiles();
            path = unicode( filenames[0] )
            f = codecs.open( path, "w", "utf-8")
            f.write( self.o_results.page().currentFrame().toHtml().replace("<head>", "<head><meta charset=\"utf-8\">") + "<br><br>CopyRights(c)<a href='http://www.alfanous.org'>Alfanous</a>  " )
            f.close()
    
    def save_results_txt( self ):
        """save as html file"""
        diag = QtGui.QFileDialog()
        diag.setAcceptMode( diag.AcceptSave )
        diag.setFileMode( diag.AnyFile )
        diag.setLabelText (QtGui.QFileDialog.LookIn, "txt")
        diag.setFilter( "*.txt" )
        #filenames = ["./results.txt    "]
        if ( diag.exec_() ):
            filenames = diag.selectedFiles();
            path = unicode( filenames[0] )
            f = codecs.open( path, "w", "utf-8")
            f.write( self.o_results.page().currentFrame().toPlainText() + "\nCopyRights(c) Alfanous http://www.alfanous.org  " )
            f.close()

    def print_results( self ):
        printer = QtGui.QPrinter()
        printer.setDocName( unicode(_( u"Alfanous_Results_Page_" )) + unicode( self.o_page.value() ) )
        printer.setPageSize( printer.A4 )
        preview_dlg = QtGui.QPrintPreviewDialog(printer)
        preview_dlg.paintRequested.connect(self.printing_results)
        preview_dlg.exec_()

    def printing_results(self, printer):
        self.o_results.print_(printer)

    def send_feedback( self , state ):
        """ Open feedback url in an external browser """
        #QtGui.QDesktopServices.openUrl() ## How to specify the URL , feedback.alfanous.org

    def about( self , state ):
        """ Show about-dialog """
        AboutDialog = QtGui.QDialog()
        dlg = Ui_aboutDlg()
        dlg.setupUi( AboutDialog )
        AboutDialog.exec_()

    def help( self ):
        """  deprecated     """
        html = """ to replace with a hints dialog """
        self.o_results.setText( html )
    
    def share_an_idea(self):
        webbrowser.open('http://feedback.alfanous.org/response/add/idea/?text=[DESKTOP]')
    
    def ask_a_question(self):
        webbrowser.open('http://feedback.alfanous.org/response/add/question/?text=[DESKTOP]')
    
    def say_thanks(self):
        webbrowser.open('http://feedback.alfanous.org/response/add/thanks/?text=[DESKTOP]')
    
    def report_a_problem(self):
        webbrowser.open('http://feedback.alfanous.org/response/add/problem/?text=[DESKTOP]')
    
    def contribute_translate(self):
        webbrowser.open('https://www.transifex.com/projects/p/alfanous/')
    
    def contribute_code(self):
        webbrowser.open('https://github.com/Alfanous-team/alfanous')

def main():
    """ the main function"""
    ui = QUI()
    ## prepare style
    QtGui.QApplication.setStyle(ui.style)
    ## prepare localization
    translator = QtCore.QTranslator()
    local = QtCore.QLocale().name()
    if local == "C":
          lang_code, country_code = "en", "US"
    else:
        lang_code, country_code = local.split("_")
    translator.load("alfanousDesktop", BASEPATH + "/locale/%s/LC_MESSAGES/" % lang_code ) # translation
    ##
    app = QtGui.QApplication( sys.argv )
    app.installTranslator(translator)
    MainWindow = QtGui.QMainWindow()
    ui.setupUi( MainWindow )

    MainWindow.showMaximized()
    app.exec_()

    ui.exit()

if __name__ == "__main__":
    main()
