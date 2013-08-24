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

"""
TODO use Table grid for view results , use CSS good schema instead
TODO relate to PreferenceDlg / Hints dialog
TODO use css and simplify texts to make a good localization
TODO sura's name also in English
TODO add qurany project for Subjects in english
TODO use QT Localization instead of gettext
TODO printing
"""

## Importing modules
import sys
import os
import gettext
from re import compile

from pyparsing import ParseException
from configobj import ConfigObj


from PyQt4 import  QtGui, QtCore, uic
from PyQt4.QtCore import QRect

from alfanous.Outputs import Raw
## Specification of resources paths
from alfanous.Data import Paths

## Importing Qt forms
from mainform_ui import Ui_MainWindow
from preferencesDlg_ui import Ui_preferencesDlg
from aboutDlg_ui import Ui_Dialog as Ui_aboutDlg
from Templates import AYA_RESULTS_TEMPLATE 

## Localization using gettext
_ = gettext.gettext
n_ = gettext.ngettext
gettext.bindtextdomain( "alfanousQT" );
gettext.textdomain( "alfanousQT" );

## Localization using QT way
tr = QtCore.QCoreApplication.translate

## Initialize search engines
RAWoutput = Raw() # default paths

## STATIC GLOBAL variables
CONFIGPATH = ( os.getenv( 'USERPROFILE' ) or os.getenv( 'HOME' ) or "." ) + "/"
PERPAGE = 10 #results per page
DIR = _( "ltr" ) #direction: default
RELATIONS = ["", "", u"|", u"+", u"-"]

SAJDA_TYPE = {u"مستحبة":_( u"recommended" ), u"واجبة":_( u"obliged" )}
SURA_TYPE = {u"مدنية":_( u"medina" ), u"مكية":_( u"mekka" )}

## Some functions
relate = lambda query, filter, index:"( " + unicode( query ) + " ) " + RELATIONS[index] + " ( " + filter + " ) " if  index > 1 else filter if index == 1 else unicode( query ) + " " + filter

class QUI( Ui_MainWindow ):
    """ the main UI """

    def __init__( self ):
        self.last_results = None
        self.currentQuery = 0
        self.Queries = []
        self.history = []

    def exit( self ):
        self.save_config()
        sys.exit()

    def load_config( self ):
        """load configuration"""
        config = ConfigObj( CONFIGPATH + "/config.ini" )
        boolean = lambda s:True if s == "True" else False
        self.o_query.clear()
        self.o_query.addItems( map( lambda x:x.decode( "utf-8" ), config["history"] ) if config.has_key( "history" ) else [u"الحمد لله"] )
        self.o_limit.setValue( int( config["options"]["limit"] ) if config.has_key( "options" ) else 100 )
        self.o_perpage.setValue( int( config["options"]["perpage"] ) if config.has_key( "options" ) else 10 )

        self.o_sortedbyscore.setChecked( boolean( config["sorting"]["sortedbyscore"] ) if config.has_key( "sorting" ) else True )
        self.o_sortedbymushaf.setChecked( boolean( config["sorting"]["sortedbymushaf"] ) if config.has_key( "sorting" ) else False )
        self.o_sortedbytanzil.setChecked( boolean( config["sorting"]["sortedbytanzil"] ) if config.has_key( "sorting" ) else False )
        self.o_sortedbysubject.setChecked( boolean( config["sorting"]["sortedbysubject"] ) if config.has_key( "sorting" ) else False )
        self.o_sortedbyfield.setChecked( boolean( config["sorting"]["sortedbyfield"] ) if config.has_key( "sorting" ) else False )

        self.o_field.setCurrentIndex( int( config["sorting"]["field"] ) if config.has_key( "sorting" ) else 0 )
        self.o_reverse.setChecked( boolean( config["sorting"]["reverse"] )if config.has_key( "sorting" ) else False )

        self.o_prev.setChecked( boolean( config["extend"]["prev"] ) if config.has_key( "extend" ) else False )
        self.o_suiv.setChecked( boolean( config["extend"]["suiv"] ) if config.has_key( "extend" ) else False )

        self.o_word_stat.setChecked( boolean( config["extend"]["word_stat"] )if config.has_key( "extend" ) else False )
        self.o_aya_info.setChecked( boolean( config["extend"]["aya_info"] )if config.has_key( "extend" ) else False )
        self.o_sura_info.setChecked( boolean( config["extend"]["sura_info"] )if config.has_key( "extend" ) else False )

        self.o_traduction.setCurrentIndex( int( config["extend"]["traduction"] ) if config.has_key( "extend" ) else 0 )
        self.o_recitation.setCurrentIndex( int( config["extend"]["recitation"] ) if config.has_key( "extend" ) else 0 )

        self.o_script_uthmani.setChecked( boolean( config["script"]["uthmani"] ) if config.has_key( "script" ) else False )
        self.o_script_standard.setChecked( boolean( config["script"]["standard"] ) if config.has_key( "script" ) else True )

        self.w_features.setHidden( not boolean( config["widgets"]["features"] ) if config.has_key( "widgets" ) else True )
        self.w_options.setHidden( not boolean( config["widgets"]["options"] ) if config.has_key( "widgets" ) else True )
        self.m_options.setChecked ( boolean( config["widgets"]["options"] ) if config.has_key( "widgets" ) else False )
        self.m_features.setChecked ( boolean( config["widgets"]["features"] ) if config.has_key( "widgets" ) else False )

    def save_config( self ):
        """save configuration """
        if not os.path.isdir( CONFIGPATH ):
            os.makedirs( CONFIGPATH )
        config = ConfigObj( CONFIGPATH + "/config.ini" )
        config["history"] = map( lambda x:x, config["history"] ) if config.has_key( "history" ) else ["الحمد لله"]

        config["options"] = {}
        config["options"]["limit"] = self.o_limit.value()
        config["options"]["perpage"] = self.o_perpage.value()
        config["options"]["highlight"] = self.o_highlight.isChecked()

        config["sorting"] = {}
        config["sorting"]["sortedbyscore"] = self.o_sortedbyscore.isChecked()
        config["sorting"]["sortedbymushaf"] = self.o_sortedbymushaf.isChecked()
        config["sorting"]["sortedbytanzil"] = self.o_sortedbytanzil.isChecked()
        config["sorting"]["sortedbysubject"] = self.o_sortedbysubject.isChecked()
        config["sorting"]["sortedbyfield"] = self.o_sortedbyfield.isChecked()
        config["sorting"]["field"] = self.o_field.currentIndex()
        config["sorting"]["reverse"] = self.o_reverse.isChecked()

        config["extend"] = {}
        config["extend"]["prev"] = self.o_prev.isChecked()
        config["extend"]["suiv"] = self.o_suiv.isChecked()
        config["extend"]["traduction"] = self.o_traduction.currentIndex()
        config["extend"]["recitation"] = self.o_recitation.currentIndex()
        config["extend"]["word_stat"] = self.o_word_stat.isChecked()
        config["extend"]["aya_info"] = self.o_aya_info.isChecked()
        config["extend"]["sura_info"] = self.o_sura_info.isChecked()

        config["script"] = {}
        config["script"]["uthmani"] = self.o_script_uthmani.isChecked()
        config["script"]["standard"] = self.o_script_standard.isChecked()

        config["widgets"] = {}
        config["widgets"]["features"] = not self.w_features.isHidden()
        config["widgets"]["options"] = not self.w_options.isHidden()
        config.write()


    def setupUi( self, MainWindow ):
        super( QUI, self ).setupUi( MainWindow )

        # make sorted_by menu items as a group of radio buttons
        sorted_by_group = QtGui.QActionGroup( MainWindow )
        sorted_by_group.addAction( self.actionRelevance )
        sorted_by_group.addAction( self.actionRevelation )
        sorted_by_group.addAction( self.actionPosition_in_Mus_haf )
        sorted_by_group.addAction( self.actionSubject )
        sorted_by_group.addAction( self.actionRevelation )
        for v in RAWoutput._fields.values(): #x.keys() for Arabic
            self.menuFields.addAction( v )

        if DIR == "rtl":
            MainWindow.setLayoutDirection( QtCore.Qt.RightToLeft )
        self.o_query.setLayoutDirection( QtCore.Qt.RightToLeft )
        QtCore.QObject.connect( self.o_search, QtCore.SIGNAL( "clicked()" ), self.search_all )
        QtCore.QObject.connect( self.o_page, QtCore.SIGNAL( "valueChanged(int)" ), self.search_all )
        QtCore.QObject.connect( self.o_chapter, QtCore.SIGNAL( "activated(QString)" ), self.topics )
        QtCore.QObject.connect( self.o_topic, QtCore.SIGNAL( "activated(QString)" ), self.subtopics )
        QtCore.QObject.connect( self.o_sajdah_exist, QtCore.SIGNAL( "activated(int)" ), self.sajda_enable )
        QtCore.QObject.connect( self.o_struct_as, QtCore.SIGNAL( "activated(QString)" ), self.setstructborn )
        QtCore.QObject.connect( self.o_perpage, QtCore.SIGNAL( "valueChanged(int)" ), self.changePERPAGE )
        QtCore.QObject.connect( self.o_struct_from, QtCore.SIGNAL( "valueChanged(int)" ), self.struct_to_min )
        QtCore.QObject.connect( self.o_stat_from, QtCore.SIGNAL( "valueChanged(int)" ), self.stat_to_min )
        QtCore.QObject.connect( self.m_exit, QtCore.SIGNAL( "clicked()" ), self.exit )
        QtCore.QObject.connect( self.m_help, QtCore.SIGNAL( "clicked()" ), self.help )
        QtCore.QObject.connect( self.m_about, QtCore.SIGNAL( "triggered(bool)" ), self.about )
        QtCore.QObject.connect( self.action_Send_Feedback, QtCore.SIGNAL( "triggered(bool)" ), self.send_feedback )

        QtCore.QObject.connect( self.a_save, QtCore.SIGNAL( "clicked()" ), self.save_results )
        QtCore.QObject.connect( self.a_print, QtCore.SIGNAL( "clicked()" ), self.print_results )

        QtCore.QObject.connect( self.o_add2query_advanced, QtCore.SIGNAL( "clicked()" ), self.add2query_advanced )
        QtCore.QObject.connect( self.o_add2query_struct, QtCore.SIGNAL( "clicked()" ), self.add2query_struct )
        QtCore.QObject.connect( self.o_add2query_stat, QtCore.SIGNAL( "clicked()" ), self.add2query_stat )
        QtCore.QObject.connect( self.o_add2query_subject, QtCore.SIGNAL( "clicked()" ), self.add2query_subject )
        QtCore.QObject.connect( self.o_add2query_word, QtCore.SIGNAL( "clicked()" ), self.add2query_word )
        QtCore.QObject.connect( self.o_add2query_misc, QtCore.SIGNAL( "clicked()" ), self.add2query_misc )

        self.o_chapter.addItems( RAWoutput._chapters )
        self.o_sura_name.addItems( RAWoutput._surates )
        self.o_field.addItems( RAWoutput._fields.values() )# x.keys() for Arabic
        self.o_traduction.addItems( RAWoutput._translations.values() )
        self.load_config()


    def search_all( self, page = 1 ):
        """
        The main search function
        """
        # add to history
        if self.o_query.currentText() in self.history:
            self.history.remove( self.o_query.currentText() )
        self.history.insert( 0, self.o_query.currentText() )
        self.o_query.clear()
        self.o_query.addItems( self.history )
        self.o_query.setCurrentIndex( 0 )

        limit = self.o_limit.value()


        suggest_flags = {
                "action":"suggest",
                "query": self.o_query.currentText()
                }
        suggestion_output = RAWoutput.do( suggest_flags )

        #search
        results, terms = None, []
        search_flags = {"action":"search",
                 "query": unicode( self.o_query.currentText() ),
                 "sortedby":"score" if self.o_sortedbyscore.isChecked() \
                        else "mushaf" if self.o_sortedbymushaf.isChecked() \
                        else "tanzil" if self.o_sortedbytanzil.isChecked() \
                        else "subject" if self.o_sortedbysubject.isChecked() \
                        else unicode( self.o_field.currentText() ), # ara2eng_names[self.o_field.currentText()] for Arabic,
                 "page": self.o_page.value(),
                 "reverse_order": self.o_reverse.isChecked(),
                 "word_info":self.o_word_stat.isChecked(),
                 "highlight": "html" if self.o_highlight.isChecked() else None,
                 "script": "uthmani" if self.o_script_uthmani.isChecked()
                            else "standard",
                 "prev_aya":self.o_prev.isChecked(),
                 "next_aya": self.o_suiv.isChecked(),
                 "sura_info": self.o_sura_info.isChecked(),
                 "aya_position_info":  self.o_aya_info.isChecked(),
                 "aya_theme_info":  self.o_aya_info.isChecked(),
                 "aya_stat_info":  self.o_aya_info.isChecked(),
                 "aya_sajda_info":  self.o_aya_info.isChecked(),
                 "translation":self.o_traduction.currentText(),
                 "word_info": self.o_word_stat.isChecked(),
                 }
        self.Queries.insert( 0, search_flags )
        results = RAWoutput.do( search_flags )

        #if self.o_filter.isChecked() and self.last_results:
        #    results = QFilter( self.last_results, results )
        self.last_results = results
        ayas = results["search"]["ayas"]
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
						   "_": lambda x:x 
						}

        self.o_results.setText( AYA_RESULTS_TEMPLATE.render(template_vars) )

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

    def changePERPAGE( self, perpage ):
        global PERPAGE
        PERPAGE = perpage


    def add2query_advanced( self ):
        """
        """
        filter = ""

        text = unicode( self.o_feature_text.text() )
        word_re = compile( "[^ \n\t]+" )
        words = word_re.findall( text )
        if text:
            if self.o_synonyms.isChecked():
                for word in words:filter += " ~" + word
            elif self.o_antonyms.isChecked():
                for word in words:filter = " #" + word
            elif self.o_orthograph.isChecked():
                for word in words: filter = " %" + word
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
        filter = u""

        if self.o_sura_name.currentIndex() != 0:
            filter += u"  سورة:\"" + unicode( sura_reallist[self.o_sura_name.currentIndex() - 1] ) + "\""

        sura_types = [u"", u"مدنية", u"مكية"]
        if self.o_tanzil.currentIndex() != 0:
            filter += u"  نوع_السورة:" + unicode( sura_types[self.o_tanzil.currentIndex()] )


        yes_no = ["", u"لا", u"نعم"]
        sajdah_types = ["", u"مستحبة", u"واجبة"]
        if self.o_sajdah_exist.currentIndex() != 0:
            if self.o_sajdah_type.currentIndex() == 0:
                filter += u"  سجدة:" + unicode( yes_no[self.o_sajdah_exist.currentIndex()] )
            else:
                filter += u"  نوع_السجدة:" + unicode( sajdah_types[self.o_sajdah_type.currentIndex()] )

        index = self.o_relation_misc.currentIndex()
        newquery = relate( self.o_query.currentText(), filter, index )
        if filter:self.o_query.setEditText( newquery )


    def add2query_word( self ):
        filter = ""
        root = unicode( self.o_word_root.text() )

        type_values = [u"اسم", u"فعل", u"أداة"]
        type = type_values[self.o_word_type.currentIndex()]
        filter = u" {" + root + u"،" + type + u"}"

        index = self.o_relation_word.currentIndex()
        newquery = relate( self.o_query.currentText(), filter, index )
        if root:self.o_query.setEditText( newquery )

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
        filenames = ["./results.html    "]
        if ( diag.exec_() ):
            filenames = diag.selectedFiles();

        path = unicode( filenames[0] )
        file = open( path, "w" )
        file.write( self.o_results.toHtml() + "<br><br>CopyRights(c)<a href='http://www.alfanous.org'>Alfanous</a>  " )
        file.close()

    def print_results( self ):
        printer = QtGui.QPrinter()
        printer.setCreator( self.o_results.toHtml() )
        printer.setDocName( _( u"Results" ) + "-" + str( self.o_page.value() ) )
        printer.setPageSize( printer.A4 )


        dialog = QtGui.QPrintDialog( printer, None )
        if dialog.exec_():
            pass

        painter = QtGui.QPainter( printer )

        painter.drawText( 10, 10, _( "This is not a bug,Printing will be available in next releases insha'allah" ) )
        painter.setFont( QtGui.QFont( "Arabeyesqr" ) )
        metrics = ( painter.device().width(), painter.device().height() )
        marginHeight = 6
        marginWidth = 8
        body = QRect( marginWidth, marginHeight, metrics[0] - 2 * marginWidth, metrics[1] - 2 * marginHeight )
        #painter.drawRect(body)
        i = 0
        for line in self.o_results.toPlainText().split( "\n" ):
            i += 1
            if "[" not in line:
                painter.drawText( 10, 30 + 10 * i, line )


        painter.end()


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


def main():
    """ the main function"""
    app = QtGui.QApplication( sys.argv )

    #app.setStyle()
    MainWindow = QtGui.QMainWindow()
    ui = QUI()
    ui.setupUi( MainWindow )

    MainWindow.show()
    app.exec_()

    ui.exit()

if __name__ == "__main__":
    main()
