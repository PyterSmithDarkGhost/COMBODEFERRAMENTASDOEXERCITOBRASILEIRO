# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from qgis.gui import QgsProjectionSelectionWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(373, 186)
        Dialog.setMinimumSize(QtCore.QSize(373, 186))
        Dialog.setMaximumSize(QtCore.QSize(373, 186))
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(True)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_2.addWidget(self.label_3)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_2.addWidget(self.label_4)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.latitudeEdit = QtGui.QLineEdit(Dialog)
        self.latitudeEdit.setPlaceholderText(_fromUtf8(""))
        self.latitudeEdit.setObjectName(_fromUtf8("latitudeEdit"))
        self.verticalLayout.addWidget(self.latitudeEdit)
        self.longitudeEdit = QtGui.QLineEdit(Dialog)
        self.longitudeEdit.setObjectName(_fromUtf8("longitudeEdit"))
        self.verticalLayout.addWidget(self.longitudeEdit)
        self.projectionCombo = QgsProjectionSelectionWidget(Dialog)
        self.projectionCombo.setMinimumSize(QtCore.QSize(129, 0))
        self.projectionCombo.setObjectName(_fromUtf8("projectionCombo"))
        self.verticalLayout.addWidget(self.projectionCombo)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Mover ponto", None))
        self.label.setText(_translate("Dialog", "Digite as novas coordenadas do ponto", None))
        self.label_2.setText(_translate("Dialog", "Latitude (Y)", None))
        self.label_3.setText(_translate("Dialog", "Longitude (X)", None))
        self.label_4.setText(_translate("Dialog", "SRC", None))
        self.latitudeEdit.setInputMask(_translate("Dialog", "########.######; ", None))
        self.longitudeEdit.setInputMask(_translate("Dialog", "########.######; ", None))


