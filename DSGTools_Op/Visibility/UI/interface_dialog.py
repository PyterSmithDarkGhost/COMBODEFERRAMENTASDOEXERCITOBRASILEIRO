import os
from math import copysign
from qgis.PyQt import uic, QtGui, QtCore, QtWidgets
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY, QgsProject
from qgis.PyQt.QtWidgets import QDialogButtonBox
from qgis.utils import iface

currentPath = os.path.dirname(__file__)
GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog.ui'))

class InterfaceDialog(QtWidgets.QDialog, GUI):
    
    finished = QtCore.pyqtSignal(QgsPointXY, QgsCoordinateReferenceSystem)
    
    def __init__(self):
        super(InterfaceDialog, self).__init__()
        self.setupUi(self)
        self.initVariables()
        self.initSignals()

    def initVariables(self):
        self.iface = iface
    
    def initSignals(self):
        self.buttonBox.accepted.connect(self.sendCoords)
        self.buttonBox.rejected.connect(self.cancelButton)
    
    def setCoords(self, coords):
        self.coords = coords
        if self.coords[2].isGeographic() == True:
            self.coords[1] = self.conv_dec_gms(float(str(self.coords[1])))
            self.coords[0] = self.conv_dec_gms(float(str(self.coords[0])))
        self.latitudeEdit.setText(str(self.coords[1]))
        self.longitudeEdit.setText(str(self.coords[0]))
        self.projectionCombo.setCrs(self.coords[2])
        
    def conv_dec_gms(self, base_coord):
        self.basecoord = base_coord
        xdeg = int(abs(self.basecoord))
        xmin = int(((abs(self.basecoord) - xdeg)*60))
        xseg = int(((abs(self.basecoord) - xdeg - xmin/60)*3600))
        xdeg = int(copysign(xdeg,self.basecoord))
        conv_exp_str = u"{}º {}' {}\" ".format(str(xdeg), str(xmin).rjust(2,'0'), str(xseg).rjust(2,'0'))
        return conv_exp_str

    def conv_gms_dec(self, base_coord):
        self.basecoord = base_coord
        if self.basecoord.rfind(".") == -1:
            self.basecoord += "."
        if self.basecoord.rfind("'") == -1 and len(self.basecoord[0:self.basecoord.rfind(".")]) < 4:
            conv_exp_str = self.basecoord
        elif self.basecoord.rfind("'") == -1 and len(self.basecoord[0:self.basecoord.rfind(".")]) > 4:
            xdeg = float(self.basecoord[0:self.basecoord.rfind(".")-4])
            xmin = float(self.basecoord[self.basecoord.rfind(".")-4:self.basecoord.rfind(".")-2])
            xseg = float(self.basecoord[self.basecoord.rfind(".")-2:])
            conv_exp_str = str(copysign((abs(xdeg) + xmin/60 + xseg/3600),xdeg))
        else:
            xdeg = float(self.basecoord[0:self.basecoord.rfind("º")])
            xmin = float(self.basecoord[self.basecoord.rfind("º")+1:self.basecoord.rfind("'")])
            xseg = float(self.basecoord[self.basecoord.rfind("'")+1:self.basecoord.rfind("\"")])
            conv_exp_str = str(copysign((abs(xdeg) + xmin/60 + xseg/3600),xdeg))
        return conv_exp_str

    def sendCoords(self):
        if self.projectionCombo.crs().isGeographic() == True:
            self.longitudeEdit.setText(self.conv_gms_dec(self.longitudeEdit.text()))
            self.latitudeEdit.setText(self.conv_gms_dec(self.latitudeEdit.text()))
        x = float(self.longitudeEdit.text())
        y = float(self.latitudeEdit.text())
        point = QgsPointXY(x, y)
        newCrs = self.projectionCombo.crs()
        transformer = QgsCoordinateTransform(newCrs, self.coords[2], QgsProject.instance())
        newPoint = transformer.transform(point)
        self.finished.emit(newPoint, newCrs)
        
    def cancelButton(self):
        self.close()