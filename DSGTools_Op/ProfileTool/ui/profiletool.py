# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'profiletool.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui
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

class Ui_ProfileTool(object):
    def setupUi(self, ProfileTool):
        ProfileTool.setObjectName(_fromUtf8("ProfileTool"))
        ProfileTool.resize(897, 356)
        self.dockWidgetContents = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.activateButton = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.activateButton.sizePolicy().hasHeightForWidth())
        self.activateButton.setSizePolicy(sizePolicy)
        self.activateButton.setMaximumSize(QtCore.QSize(25, 16777215))
        self.activateButton.setAutoFillBackground(False)
        self.activateButton.setCheckable(False)
        self.activateButton.setFlat(False)
        self.activateButton.setObjectName(_fromUtf8("activateButton"))
        self.horizontalLayout_2.addWidget(self.activateButton)
        self.splitter = QtGui.QSplitter(self.dockWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.frame = QtGui.QFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_3 = QtGui.QGridLayout(self.frame)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.sbMaxVal = QtGui.QDoubleSpinBox(self.frame)
        self.sbMaxVal.setKeyboardTracking(False)
        self.sbMaxVal.setMinimum(-99999.0)
        self.sbMaxVal.setMaximum(99999.0)
        self.sbMaxVal.setObjectName(_fromUtf8("sbMaxVal"))
        self.verticalLayout_5.addWidget(self.sbMaxVal)
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_5.addWidget(self.label_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_5.addWidget(self.label_3)
        self.sbMinVal = QtGui.QDoubleSpinBox(self.frame)
        self.sbMinVal.setKeyboardTracking(False)
        self.sbMinVal.setMinimum(-99999.0)
        self.sbMinVal.setMaximum(99999.0)
        self.sbMinVal.setObjectName(_fromUtf8("sbMinVal"))
        self.verticalLayout_5.addWidget(self.sbMinVal)
        self.gridLayout_3.addLayout(self.verticalLayout_5, 0, 1, 1, 1)
        self.frame_for_plot = QtGui.QFrame(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame_for_plot.sizePolicy().hasHeightForWidth())
        self.frame_for_plot.setSizePolicy(sizePolicy)
        self.frame_for_plot.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_for_plot.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_for_plot.setObjectName(_fromUtf8("frame_for_plot"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.frame_for_plot)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.gridLayout_3.addWidget(self.frame_for_plot, 0, 0, 1, 1)
        self.widget_save_buttons = QtGui.QWidget(self.frame)
        self.widget_save_buttons.setObjectName(_fromUtf8("widget_save_buttons"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget_save_buttons)
        self.horizontalLayout_3.setMargin(2)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.pushButton_reinitview = QtGui.QPushButton(self.widget_save_buttons)
        self.pushButton_reinitview.setObjectName(_fromUtf8("pushButton_reinitview"))
        self.horizontalLayout_3.addWidget(self.pushButton_reinitview)
        spacerItem1 = QtGui.QSpacerItem(0, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.stackedWidget = QtGui.QStackedWidget(self.widget_save_buttons)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.page)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.stackedWidget.addWidget(self.page)
        self.horizontalLayout_3.addWidget(self.stackedWidget)
        spacerItem2 = QtGui.QSpacerItem(1, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.cbxSaveAs = QtGui.QComboBox(self.widget_save_buttons)
        self.cbxSaveAs.setObjectName(_fromUtf8("cbxSaveAs"))
        self.cbxSaveAs.addItem(_fromUtf8(""))
        self.cbxSaveAs.addItem(_fromUtf8(""))
        self.cbxSaveAs.addItem(_fromUtf8(""))
        self.cbxSaveAs.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.cbxSaveAs)
        self.butSaveAs = QtGui.QPushButton(self.widget_save_buttons)
        self.butSaveAs.setObjectName(_fromUtf8("butSaveAs"))
        self.horizontalLayout_3.addWidget(self.butSaveAs)
        self.gridLayout_3.addWidget(self.widget_save_buttons, 1, 0, 1, 2)
        self.frame_for_plot.raise_()
        self.widget_save_buttons.raise_()
        self.frame_2 = QtGui.QFrame(self.splitter)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_4 = QtGui.QLabel(self.frame_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_2.addWidget(self.label_4)
        self.layerCombo = QgsMapLayerComboBox(self.frame_2)
        self.layerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.layerCombo.setObjectName(_fromUtf8("layerCombo"))
        self.verticalLayout_2.addWidget(self.layerCombo)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.tableView = QtGui.QTableView(self.frame_2)
        self.tableView.setMinimumSize(QtCore.QSize(1, 1))
        self.tableView.setMaximumSize(QtCore.QSize(1, 1))
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout_2.addWidget(self.tableView)
        self.groupBox = QtGui.QGroupBox(self.frame_2)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setFrame(True)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.checkBox_mpl_tracking = QtGui.QCheckBox(self.frame_2)
        self.checkBox_mpl_tracking.setEnabled(True)
        self.checkBox_mpl_tracking.setChecked(True)
        self.checkBox_mpl_tracking.setObjectName(_fromUtf8("checkBox_mpl_tracking"))
        self.verticalLayout_2.addWidget(self.checkBox_mpl_tracking)
        self.scrollArea = QtGui.QScrollArea(self.frame_2)
        self.scrollArea.setMaximumSize(QtCore.QSize(1, 1))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 16, 16))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.horizontalLayout_2.addWidget(self.splitter)
        ProfileTool.setWidget(self.dockWidgetContents)

        self.retranslateUi(ProfileTool)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ProfileTool)

    def retranslateUi(self, ProfileTool):
        ProfileTool.setWindowTitle(_translate("ProfileTool", "Perfil do Terreno", None))
        self.activateButton.setText(_translate("ProfileTool", "A\n"
"t\n"
"i\n"
"v\n"
"a\n"
"r", None))
        self.label_2.setText(_translate("ProfileTool", "m??ximo", None))
        self.label_3.setText(_translate("ProfileTool", "m??nimo", None))
        self.pushButton_reinitview.setText(_translate("ProfileTool", "Reenquadrar", None))
        self.cbxSaveAs.setItemText(0, _translate("ProfileTool", "PDF", None))
        self.cbxSaveAs.setItemText(1, _translate("ProfileTool", "PNG", None))
        self.cbxSaveAs.setItemText(2, _translate("ProfileTool", "SVG", None))
        self.cbxSaveAs.setItemText(3, _translate("ProfileTool", "print (PS)", None))
        self.butSaveAs.setText(_translate("ProfileTool", "Salvar como", None))
        self.label_4.setText(_translate("ProfileTool", "Camada com altimetria", None))
        self.groupBox.setTitle(_translate("ProfileTool", "Op????es", None))
        self.label.setText(_translate("ProfileTool", "Modo de tra??ado", None))
        self.comboBox.setItemText(0, _translate("ProfileTool", "Linha tempor??ria", None))
        self.comboBox.setItemText(1, _translate("ProfileTool", "Linha selecionada", None))
        self.checkBox_mpl_tracking.setText(_translate("ProfileTool", "Conectar posi????o do cursor \n"
"com perfil tra??ado no mapa", None))
