# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'geocoder_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_QuickGeocoderDockWidgetBase(object):
    def setupUi(self, QuickGeocoderDockWidgetBase):
        QuickGeocoderDockWidgetBase.setObjectName("QuickGeocoderDockWidgetBase")
        QuickGeocoderDockWidgetBase.resize(378, 598)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.apiKeyEdit = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.apiKeyEdit.setObjectName("apiKeyEdit")
        self.gridLayout.addWidget(self.apiKeyEdit, 2, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tabDirect = QtWidgets.QWidget()
        self.tabDirect.setObjectName("tabDirect")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tabDirect)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.tabDirect)
        self.label_2.setMinimumSize(QtCore.QSize(180, 0))
        self.label_2.setMaximumSize(QtCore.QSize(180, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.layersComboBox = gui.QgsMapLayerComboBox(self.tabDirect)
        self.layersComboBox.setObjectName("layersComboBox")
        self.horizontalLayout.addWidget(self.layersComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.tabDirect)
        self.label_3.setMinimumSize(QtCore.QSize(180, 0))
        self.label_3.setMaximumSize(QtCore.QSize(180, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.newAttributeEdit = QtWidgets.QLineEdit(self.tabDirect)
        self.newAttributeEdit.setObjectName("newAttributeEdit")
        self.horizontalLayout_2.addWidget(self.newAttributeEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.tabWidget.addTab(self.tabDirect, "")
        self.tabReverse = QtWidgets.QWidget()
        self.tabReverse.setObjectName("tabReverse")
        self.tabWidget.addTab(self.tabReverse, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.geocodeButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.geocodeButton.setObjectName("geocodeButton")
        self.gridLayout.addWidget(self.geocodeButton, 3, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        QuickGeocoderDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(QuickGeocoderDockWidgetBase)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(QuickGeocoderDockWidgetBase)

    def retranslateUi(self, QuickGeocoderDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        QuickGeocoderDockWidgetBase.setWindowTitle(_translate("QuickGeocoderDockWidgetBase", "Bing Geocoder"))
        self.label_2.setText(_translate("QuickGeocoderDockWidgetBase", "Select layer"))
        self.label_3.setText(_translate("QuickGeocoderDockWidgetBase", "Addresses\' new attribute name"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDirect), _translate("QuickGeocoderDockWidgetBase", "Direct"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabReverse), _translate("QuickGeocoderDockWidgetBase", "Reverse"))
        self.geocodeButton.setText(_translate("QuickGeocoderDockWidgetBase", "Geocode"))
        self.label.setText(_translate("QuickGeocoderDockWidgetBase", "Bing Maps API key - Get one here: http://bingmapsportal.com"))

from qgis import gui
