# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layerselector.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel

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

class Ui_LayerSelector(object):
    def setupUi(self, LayerSelector):
        LayerSelector.setObjectName(_fromUtf8("LayerSelector"))
        LayerSelector.resize(400, 153)
        self.verticalLayout = QtGui.QVBoxLayout(LayerSelector)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(LayerSelector)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.layerCombo = QgsMapLayerComboBox(LayerSelector)
        self.layerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.layerCombo.setObjectName(_fromUtf8("layerCombo"))
        self.verticalLayout.addWidget(self.layerCombo)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(LayerSelector)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LayerSelector)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LayerSelector.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LayerSelector.reject)
        QtCore.QMetaObject.connectSlotsByName(LayerSelector)

    def retranslateUi(self, LayerSelector):
        LayerSelector.setWindowTitle(_translate("LayerSelector", "Selecionar camada", None))
        self.label.setText(_translate("LayerSelector", "Selecione a camada para traçar o perfil", None))
