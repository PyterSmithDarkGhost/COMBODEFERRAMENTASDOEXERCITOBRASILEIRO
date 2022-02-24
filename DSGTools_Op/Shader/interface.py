# -*- coding: UTF-8 -*-
import os
import processing
from qgis.PyQt import QtGui, uic, QtCore, QtWidgets
from qgis.PyQt.QtCore import QDateTime
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsMapLayerProxyModel, QgsRasterLayer
from qgis.PyQt.QtWidgets import QMessageBox
from ..auxiliar.sunposition.sunposition import sunpos

GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'window.ui'))

class Interface(QtWidgets.QDockWidget, GUI):
    def __init__(self, canvas):
        super(Interface, self).__init__()
        self.setupUi(self)
        self.canvas = canvas
        self.initVariables()
        self.initSignals()
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.layerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.outputFile.setFilter(".tif")
    
    def initVariables(self):
        self.myTool = QgsMapToolEmitPoint(self.canvas)
        self.currentTool = self.canvas.mapTool()
        self.clickedPoint = ''

    def createVertexMarker(self):
        self.clickedPoint = QgsVertexMarker(self.canvas)
        self.clickedPoint.setIconSize(15)
        self.clickedPoint.setPenWidth(3)
    
    def initSignals(self):
        self.ativarButton.toggled.connect(self.getPoint)
        self.myTool.canvasClicked.connect(self.doWork)
        self.canvas.mapToolSet.connect(self.verifyTool)        
        
    def verifyTool(self, tool):
        if tool != self.myTool:
            self.ativarButton.setChecked(False)
    
    def getPoint(self, state):
        if state:
            self.canvas.setMapTool(self.myTool)
            self.createVertexMarker()
        else:
            self.canvas.unsetMapTool(self.myTool)
            self.canvas.scene().removeItem(self.clickedPoint)
    
    def doWork(self, point, button):
        if button == QtCore.Qt.LeftButton:
            wgsPoint = self.getWGSPoint(point)
            now = self.dateTimeEdit.dateTime().toPyDateTime()
            az,zen = sunpos(now, wgsPoint.y(), wgsPoint.x(), 0)[:2]
            if not self.layerCombo.currentLayer():
                QMessageBox.critical(self, u"Erro", u"Nenhuma camada raster selecionada. Selecione uma camada.")
                return
            workingLayerFile = self.layerCombo.currentLayer().dataProvider().dataSourceUri()
            outputpath = self.outputFile.filePath()
            if not outputpath:
                QMessageBox.critical(self, u"Erro", u"Nenhum arquivo de saída definido. Escolha um arquivo de saída.")
                return
            if not outputpath.endswith(".tif"):
                outputpath = outputpath + '.tif'
            processing.run("gdal:hillshade", {'INPUT': workingLayerFile,
            'BAND': 1,
            'AZIMUTH': float(az),
            'ALTITUDE': 90 - float(zen),
            'OUTPUT': outputpath})
			
            shadedlayer = QgsRasterLayer(outputpath, "Raster sombreado")
            QgsProject.instance().addMapLayer(shadedlayer)
            self.clickedPoint.setCenter(point)
            
    def getWGSPoint(self, pt):
        crsSrc  = self.canvas.mapSettings().destinationCrs()
        crsDest = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        
        coordinateTransformer = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        wgsPt = coordinateTransformer.transform(pt)
        return wgsPt
