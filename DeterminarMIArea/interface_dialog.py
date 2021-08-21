import os
from math import copysign
from qgis.PyQt import uic, QtGui, QtCore, QtWidgets
from qgis.core import QgsCoordinateTransform, QgsPointXY, QgsProject
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.utils import iface

GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog.ui'))

class InterfaceDialog(QtWidgets.QDialog, GUI):
    
    finished = QtCore.pyqtSignal(int, str, bool)
    
    def __init__(self):
        super(InterfaceDialog, self).__init__()
        self.setupUi(self)
        self.initVariables()
        self.initSignals()

    def initVariables(self):
        self.iface = iface
    
    def initSignals(self):
        self.buttonBox.accepted.connect(self.selectOutputFolder)
        self.buttonBox.rejected.connect(self.cancelButton)
    
    def selectOutputFolder(self):
        fileDlg = QFileDialog()
        self.outputFolder = fileDlg.getExistingDirectory(None, u"Selecionar pasta de saída das imagens", "", QFileDialog.ShowDirsOnly)
        self.sendData()
    
    def sendData(self):
        if self.scaleMulti.isChecked():
            multiScale = True
        else:
            multiScale = False

        if self.scale25.isChecked():
            selection = 1
        elif self.scale50.isChecked():
            selection = 2
        elif self.scale100.isChecked():
            selection = 3
        elif self.scale250.isChecked():
            selection = 4
        
        self.finished.emit(selection, self.outputFolder, multiScale)
        
    def cancelButton(self):
        self.close()
