# -*- coding: utf-8 -*-
from qgis.PyQt import uic, QtCore, QtGui, QtWidgets
from qgis.core import QgsCoordinateReferenceSystem
from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog
from qgis.gui import QgsProjectionSelectionDialog
from qgis.PyQt.QtCore import pyqtSlot, pyqtSignal, Qt, QObject
from ..model.baseDeDados import BaseDeDados
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'createDataBaseInterface.ui'))

class CreateDataBaseInterface(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, militarySimbologyInterface):
        super(CreateDataBaseInterface, self).__init__()
        self.setupUi(self)
        self.fileNameLineEdit.textEdited.connect(self.setNameFile)
        self.initVariables()
        self.militarySimbologyInterface = militarySimbologyInterface

    def initVariables(self):
        self.name = None
        self.folder = None
        self.epsg = None
        self.militarySimbologyInterface = None
        self.baseDeDados = BaseDeDados()

    def showDialog(self):
        self.show()

    def setNameFile(self, n):
        self.name = n

    def setFolder(self):
        path = QFileDialog.getExistingDirectory(self, 'Selecione Pasta:', '')
        if path:
            self.folder = path
            self.folderDestinyLineEdit.setText(self.folder)
        else:
            QMessageBox.warning(self, u"Aviso:", u"Selecione Pasta para criar banco")

    def closeEvent(self, e):
        self.name = None
        self.folder = None
        self.folderDestinyLineEdit.clear()
        self.fileNameLineEdit.clear()

    def doCreateDataBase(self):
        if self.folder and self.name:
            path = os.path.join(self.folder, self.name)+'.gpkg'
            self.baseDeDados.createDataBase(path)
            if os.path.isfile(path):
                QMessageBox.warning(self, u"Aviso:", u'Arquivo de simbologia militar criado com sucesso!\nAguarde o carregamento automático')
                self.baseDeDados.setCurrentDatabase(path)
                if self.baseDeDados.loadDatabase():
                    QMessageBox.warning(self, u"Aviso:", u'Arquivo de simbologia militar carregado com sucesso!')
                    return 1
                else:
                    QMessageBox.warning(self, u"Aviso:", u'Erro ao carregar o arquivo de simbologia militar.')
                    return 0
            else:
                QMessageBox.warning(self, u"Aviso:", u'Erro na criação do arquivo de simbologia militar!')
                return 1
        else:
            QMessageBox.warning(self, u"Aviso:", u"Preencha todos os campos !")
            return 0

    @pyqtSlot(bool)
    def on_selectFolderButton_clicked(self):
        self.setFolder()

    @pyqtSlot(bool)
    def on_createDataBaseButton_clicked(self):
        if self.doCreateDataBase():
            self.close()
