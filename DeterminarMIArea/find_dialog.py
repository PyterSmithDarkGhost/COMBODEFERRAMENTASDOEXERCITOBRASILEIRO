import os
from math import copysign
from qgis.PyQt import uic, QtCore, QtWidgets
from qgis.utils import iface

GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog_find.ui'))

class FindDialog(QtWidgets.QDialog, GUI):
    
    finished = QtCore.pyqtSignal(str)
    
    def __init__(self):
        super(FindDialog, self).__init__()
        self.setupUi(self)
        self.initVariables()
        self.initSignals()

    def initVariables(self):
        self.iface = iface
    
    def initSignals(self):
        self.buttonBox.accepted.connect(self.sendData)
        self.buttonBox.rejected.connect(self.cancelButton)
    
    def sendData(self):
        if self.smallScale.isChecked():
            choice = 'small'
        elif self.bigScale.isChecked():
            choice = 'big'
        
        self.finished.emit(choice)
        
    def cancelButton(self):
        self.close()
