# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI/preferencesDlg.ui'
#
# Created: Fri Jul 29 08:38:22 2011
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_preferencesDlg(object):
    def setupUi(self, preferencesDlg):
        preferencesDlg.setObjectName("preferencesDlg")
        preferencesDlg.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(preferencesDlg)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_12 = QtGui.QGroupBox(preferencesDlg)
        self.groupBox_12.setGeometry(QtCore.QRect(70, 30, 241, 111))
        self.groupBox_12.setObjectName("groupBox_12")
        self.verticalLayout_22 = QtGui.QVBoxLayout(self.groupBox_12)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.horizontalLayout_35 = QtGui.QHBoxLayout()
        self.horizontalLayout_35.setObjectName("horizontalLayout_35")
        self.label_34 = QtGui.QLabel(self.groupBox_12)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_34.sizePolicy().hasHeightForWidth())
        self.label_34.setSizePolicy(sizePolicy)
        self.label_34.setObjectName("label_34")
        self.horizontalLayout_35.addWidget(self.label_34)
        self.o_limit = QtGui.QSpinBox(self.groupBox_12)
        self.o_limit.setStyleSheet("None")
        self.o_limit.setReadOnly(False)
        self.o_limit.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.o_limit.setAccelerated(True)
        self.o_limit.setKeyboardTracking(True)
        self.o_limit.setPrefix("")
        self.o_limit.setMinimum(25)
        self.o_limit.setMaximum(6236)
        self.o_limit.setSingleStep(25)
        self.o_limit.setProperty("value", 1000)
        self.o_limit.setObjectName("o_limit")
        self.horizontalLayout_35.addWidget(self.o_limit)
        self.verticalLayout_22.addLayout(self.horizontalLayout_35)
        self.horizontalLayout_36 = QtGui.QHBoxLayout()
        self.horizontalLayout_36.setObjectName("horizontalLayout_36")
        self.label = QtGui.QLabel(self.groupBox_12)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout_36.addWidget(self.label)
        self.o_perpage = QtGui.QSpinBox(self.groupBox_12)
        self.o_perpage.setStyleSheet("None")
        self.o_perpage.setReadOnly(False)
        self.o_perpage.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.o_perpage.setAccelerated(True)
        self.o_perpage.setKeyboardTracking(False)
        self.o_perpage.setPrefix("")
        self.o_perpage.setMinimum(5)
        self.o_perpage.setMaximum(6236)
        self.o_perpage.setSingleStep(5)
        self.o_perpage.setProperty("value", 10)
        self.o_perpage.setObjectName("o_perpage")
        self.horizontalLayout_36.addWidget(self.o_perpage)
        self.verticalLayout_22.addLayout(self.horizontalLayout_36)
        self.o_highlight = QtGui.QCheckBox(self.groupBox_12)
        self.o_highlight.setChecked(True)
        self.o_highlight.setObjectName("o_highlight")
        self.verticalLayout_22.addWidget(self.o_highlight)
        self.textEdit = QtGui.QTextEdit(preferencesDlg)
        self.textEdit.setGeometry(QtCore.QRect(110, 150, 104, 92))
        self.textEdit.setObjectName("textEdit")
        self.label_34.setBuddy(self.o_perpage)
        self.label.setBuddy(self.o_perpage)

        self.retranslateUi(preferencesDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), preferencesDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), preferencesDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(preferencesDlg)

    def retranslateUi(self, preferencesDlg):
        preferencesDlg.setWindowTitle(QtGui.QApplication.translate("preferencesDlg", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_12.setTitle(QtGui.QApplication.translate("preferencesDlg", "Misc", None, QtGui.QApplication.UnicodeUTF8))
        self.label_34.setText(QtGui.QApplication.translate("preferencesDlg", "Limit ", None, QtGui.QApplication.UnicodeUTF8))
        self.o_limit.setSuffix(QtGui.QApplication.translate("preferencesDlg", " results", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("preferencesDlg", "Results/Page", None, QtGui.QApplication.UnicodeUTF8))
        self.o_perpage.setSuffix(QtGui.QApplication.translate("preferencesDlg", " results", None, QtGui.QApplication.UnicodeUTF8))
        self.o_highlight.setText(QtGui.QApplication.translate("preferencesDlg", "Highlight keywords", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit.setHtml(QtGui.QApplication.translate("preferencesDlg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">To do :</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Choose language</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Choose Font for Quran</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Choose Font for Recitation</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Choose general Font </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

