# -*- coding: utf-8 -*-
from math import copysign
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QDialog, QHeaderView, QMessageBox, QDialogButtonBox, QFileDialog, QTableWidgetItem
from qgis.core import *
from qgis.gui import *
import webbrowser, os
from qgis.PyQt import uic

currentPath = os.path.dirname(__file__)
GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'nd_addfeature.ui'))
        
class NdAddFeatureGui(QDialog, GUI):

    numericalFeature = pyqtSignal(list)
    transformOTF_CRS = pyqtSignal(bool)
    transformFromCrs = pyqtSignal(long)
      
    def __init__(self, iface, layertype):
        self.layertype = layertype
        QDialog.__init__(self, iface)
        self.iface = iface
        self.setupUi(self)
        
        self.twPoints.setColumnWidth(0,self.twPoints.width()/2)
        self.twPoints.setColumnWidth(1,self.twPoints.width()/2)
        self.twPoints.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.twPoints.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        
        self.twPoints.cellChanged.connect( self.cellChanged )
        self.buttonBox.accepted.connect( self.onOK )
        self.addFromFileButton.clicked.connect( self.addFromFile )
        
        self.buttonBox.button(QDialogButtonBox.Ok ).setEnabled(False)
        
        self.pb_ChooseCrs.setEnabled(False)
        self.l_OtherCrsName.setEnabled(False)
        
        self.rb_OtherCrs.toggled.connect(self.selectOtherCrs)
        self.pb_ChooseCrs.clicked.connect(self.chooseOtherCrs)
        
        settings = QSettings()
        self.featureCrsId = settings.value("numericDigitize/featureCrsId", -1, type=long)
        rb_checked = settings.value("numericDigitize/checked", "rb_ProjectCrs", type=unicode)
        if rb_checked == "rb_ProjectCrs":
            self.rb_ProjectCrs.setChecked(True)
        elif rb_checked == "rb_LayerCrs":
            self.rb_LayerCrs.setChecked(True)
        else:
            self.rb_OtherCrs.setChecked(True)
        self.__displayAuthid()
    
    def addFromFile(self):
        fileDlg = QFileDialog()
        filePath = fileDlg.getOpenFileName(None, u"Selecionar arquivo CSV", "", u"Comma-separated values file (*.csv)")[0]
        lineIdx = self.twPoints.rowCount() - 1
        if filePath:
            csvFile = open(filePath, "r")
            for l in csvFile:
                line = l.rstrip().replace('\n','').split(";")
                self.twPoints.setItem(lineIdx, 0, QTableWidgetItem(line[0]))
                self.twPoints.setItem(lineIdx, 1, QTableWidgetItem(line[1]))
                lineIdx += 1
            csvFile.close()
    
    def selectOtherCrs(self, checked):
        if checked == True:
            self.pb_ChooseCrs.setEnabled(True)
            self.l_OtherCrsName.setEnabled(True)
        else:
            self.pb_ChooseCrs.setEnabled(False)
            self.l_OtherCrsName.setEnabled(False)

    def chooseOtherCrs(self):
        crsSelector = QgsProjectionSelectionDialog()
        if crsSelector.exec_():
            self.featureCrsId = crsSelector.crs().srsid()
            self.__displayAuthid()
    
    def __displayAuthid(self):
        if self.featureCrsId == -1:
            self.l_OtherCrsName.setText("[%s]"%self.tr(u"Sistema de coordenadas não selecionado"))
        else:
            self.l_OtherCrsName.setText(
                "[%s]"%QgsCoordinateReferenceSystem(self.featureCrsId, QgsCoordinateReferenceSystem.InternalCrsId).authid()
                )
            
    def cellChanged (self, currentRow, currentColumn):
        theValue = self.twPoints.item(currentRow, currentColumn)

        if((self.twPoints.rowCount() == currentRow+1)) :
          try:
            self.twPoints.item(currentRow, 0).text() != ""
            xok = True
          except AttributeError:
            xok = False
          try:
            self.twPoints.item(currentRow, 1).text() != ""
            yok = True
          except AttributeError:
            yok = False

          if(xok and yok):
            self.twPoints.setRowCount(self.twPoints.rowCount())
            self.twPoints.insertRow(self.twPoints.rowCount())
            if(self.layertype == 0):
               if(self.twPoints.rowCount()-1)>=1:
                 self.buttonBox.button(QDialogButtonBox.Ok ).setEnabled(True)
            elif(self.layertype == 1):
               if(self.twPoints.rowCount()-1)>=2:
                 self.buttonBox.button(QDialogButtonBox.Ok ).setEnabled(True)
            elif(self.layertype == 2):
               if(self.twPoints.rowCount()-1)>=3:
                 self.buttonBox.button(QDialogButtonBox.Ok ).setEnabled(True)
        
      
    def is_number(self, s):
      try:
          float(s)
          return True
      except ValueError:
          return False

    def conv_gms_dec(self, base_coord):
        self.basecoord = base_coord
        if self.basecoord.rfind(".") == -1:
            self.basecoord += "."
        if self.basecoord.rfind("'") == -1 and len(self.basecoord[0:self.basecoord.rfind(".")]) < 4:
            conv_exp_str = self.basecoord
        elif self.basecoord.rfind("'") == -1 and len(self.basecoord[0:self.basecoord.rfind(".")]) > 4 and (len(self.basecoord[0:self.basecoord.rfind(".")]) < 8 and self.basecoord.rfind("-") != -1):
            xdeg = float(self.basecoord[0:self.basecoord.rfind(".")-4])
            xmin = float(self.basecoord[self.basecoord.rfind(".")-4:self.basecoord.rfind(".")-2])
            xseg = float(self.basecoord[self.basecoord.rfind(".")-2:])
            conv_exp_str = str(copysign((abs(xdeg) + xmin/60 + xseg/3600),xdeg))
        elif self.basecoord.rfind("'") != -1:
            xdeg = float(self.basecoord[0:self.basecoord.rfind("º")])
            xmin = float(self.basecoord[self.basecoord.rfind("º")+1:self.basecoord.rfind("'")])
            xseg = float(self.basecoord[self.basecoord.rfind("'")+1:self.basecoord.rfind("\"")])
            conv_exp_str = str(copysign((abs(xdeg) + xmin/60 + xseg/3600),xdeg))
        else:
            conv_exp_str = self.basecoord
        return conv_exp_str

    def onOK(self):
      settings = QSettings()
      if self.rb_ProjectCrs.isChecked():
        self.transformOTF_CRS.emit(self.rb_ProjectCrs.isChecked())
        settings.setValue("numericDigitize/checked", "rb_ProjectCrs")
      elif self.rb_OtherCrs.isChecked():
        self.transformFromCrs.emit(self.featureCrsId)
        settings.setValue("numericDigitize/checked", "rb_OtherCrs")
        settings.setValue("numericDigitize/featureCrsId", self.featureCrsId)
      else:
        settings.setValue("numericDigitize/checked", "rb_LayerCrs")
        
      coords = []
      for i in range(self.twPoints.rowCount()-1):
        x = self.conv_gms_dec(self.twPoints.item(i, 0).text())
        y = self.conv_gms_dec(self.twPoints.item(i, 1).text())
        pt = QgsPointXY(float(x), float(y))
        coords.append(pt)
      self.numericalFeature.emit(coords)
