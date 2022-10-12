# -*- coding: UTF-8 -*-
import os
import processing
from qgis.PyQt import QtGui, uic, QtCore, QtWidgets
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsCoordinateTransform, QgsProject, QgsRasterLayer, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from .interface_dialog import InterfaceDialog

GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'window.ui'))

class Interface(QtWidgets.QDockWidget, GUI):
    def __init__(self, iface):
        super(Interface, self).__init__()
        self.setupUi(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.clickedPoint = ''
        self.dialog = InterfaceDialog()
        self.myTool = QgsMapToolEmitPoint(self.canvas)
        self.initSignals()
	
    def initSignals(self):
        self.ativarButton.toggled.connect(self.getPoint)
        self.myTool.canvasClicked.connect(self.openDialog)
        self.dialog.finished.connect(self.doWork)
        self.canvas.mapToolSet.connect(self.verifyTool) 		

    def verifyTool(self, tool):
        if tool != self.myTool:
            self.ativarButton.setChecked(False)
        
    def createVertexMarker(self):
        self.clickedPoint = QgsVertexMarker(self.canvas)
        self.clickedPoint.setIconSize(15)
        self.clickedPoint.setPenWidth(3)
		
    def getPoint(self, state):
        if state:
            self.canvas.setMapTool(self.myTool)
            self.createVertexMarker()
        else:
            self.canvas.unsetMapTool(self.myTool)
            self.canvas.scene().removeItem(self.clickedPoint)

    def openDialog(self, point, button):
        self.clickedPoint.setCenter(point)
        params = []
        params.append(point.x())
        params.append(point.y())
        params.append(self.canvas.mapSettings().destinationCrs())
        self.dialog.setCoords(params)
        self.dialog.exec_()

    def setRasterStyle(self, raster_layer):
        shaderType = QgsColorRampShader()
        shaderType.setColorRampType(QgsColorRampShader.Discrete)
        item_list = []
        item_list.append(QgsColorRampShader.ColorRampItem(0, QColor(0, 0, 0), lbl = "Sem visada"))
        item_list.append(QgsColorRampShader.ColorRampItem(1, QColor(0, 255, 0), lbl = "Visível"))
        shaderType.setColorRampItemList(item_list)
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(shaderType)
        renderer = QgsSingleBandPseudoColorRenderer(raster_layer.dataProvider(), 1, shader)
        raster_layer.setRenderer(renderer)
        raster_layer.triggerRepaint()

    def doWork(self, inputPoint, pointCrs):
        if not self.layerCombo.currentLayer():
            QMessageBox.critical(self, u"Erro", u"Nenhuma camada raster selecionada. Selecione uma camada.")
            return

        workingLayer = self.layerCombo.currentLayer()
        outputpath = self.outputFile.filePath()

        if not outputpath:
            QMessageBox.critical(self, u"Erro", u"Nenhum arquivo de saída definido. Escolha um arquivo de saída.")
            return
        if not outputpath.endswith(".tif"):
            outputpath = outputpath + '.tif'

        transformer = QgsCoordinateTransform(pointCrs, workingLayer.crs(), QgsProject.instance())
        workPoint = transformer.transform(inputPoint)

        processing.run("grass7:r.viewshed", {'input': workingLayer.dataProvider().dataSourceUri(),
        'coordinates': (str(workPoint.x()) + ',' + str(workPoint.y())),
        'observer_elevation': self.heightSpinBox.value(),
        'target_elevation': 0,
        'max_distance': self.rangeSpinBox.value(),
        'refraction_coeff': 0.14286,
        '-c': True,
        '-r': True,
        '-b': True,
        'output': outputpath})

        visibLayer = QgsRasterLayer(outputpath, "Mapa de visibilidade")
        QgsProject.instance().addMapLayer(visibLayer)
        self.setRasterStyle(visibLayer)
        return
