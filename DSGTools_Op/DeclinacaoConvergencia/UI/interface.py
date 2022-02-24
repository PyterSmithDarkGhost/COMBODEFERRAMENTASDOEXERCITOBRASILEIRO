# -*- coding: UTF-8 -*-
import os
from qgis.PyQt import QtGui, uic, QtCore, QtWidgets
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsExpressionContextUtils
from ...auxiliar import geomag  # @UnresolvedImport
import math

GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'window.ui'))

class Interface(QtWidgets.QDockWidget, GUI):
    def __init__(self, canvas, auxi):
        super(Interface, self).__init__()
        self.setupUi(self)
        self.canvas = canvas
        self.auxiliar = auxi
        self.initVariables()
        self.initSignals()
        self.widget().setMinimumSize(QSize(262,160))
    
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
            self.setConvergencia(0.0)
            self.setDeclinacao(0)
            self.createVertexMarker()
        else:
            self.canvas.unsetMapTool(self.myTool)
            self.canvas.scene().removeItem(self.clickedPoint)
    
    def doWork(self, point, button):
        if button == QtCore.Qt.LeftButton:
            wgsPoint = self.getWGSPoint(point)
            
            conv = self.auxiliar.calculateConvergence(wgsPoint)
            decl = geomag.declination(wgsPoint.y(), wgsPoint.x())
            
            self.setConvergencia(conv)
            self.setDeclinacao(decl)
            
            self.clickedPoint.setCenter(point)
            
    def getWGSPoint(self, pt):
        crsSrc  = self.canvas.mapSettings().destinationCrs()
        crsDest = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        
        coordinateTransformer = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        wgsPt = coordinateTransformer.transform(pt)
        return wgsPt
    
    def setConvergencia(self, conv):
        convergencia = self.generateDMS(conv)
        self.convergenciaEdit.setText(convergencia)

        proj = QgsProject.instance()
        QgsExpressionContextUtils.setProjectVariable(proj,'convergenciaGMS',convergencia)
        QgsExpressionContextUtils.setProjectVariable(proj,'convergenciaGD', conv)


    def setDeclinacao(self, decl):
        declinacao = self.generateDMS(decl)
        self.declinacaoEdit.setText(declinacao)

        proj = QgsProject.instance()
        QgsExpressionContextUtils.setProjectVariable(proj,'declinacaoGMS',declinacao)
        QgsExpressionContextUtils.setProjectVariable(proj,'declinacaoGD', decl)
        
    def generateDMS(self, ang):
        xg = format( math.modf( ang )[1], '.0f' )
        
        sign = -1 if ang < 0 else 1
        
        xm = format( sign * math.modf( math.modf( ang )[0] * 60 )[1], '.0f' )
        xs = format( sign * math.modf( math.modf( ang )[0] * 60 )[0] * 60, '.3f' )
        
        gms = str(xg) + u"° " + str(xm) + "' " + str(xs) + '"'
        gms = gms.encode('utf8')
        return gms.decode('utf8')
    
    def showMessage(self,text):
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setWindowTitle(u"Aviso")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.setText(text)
        self.msgBox.exec_()
    
    def closeMsgBox(self):
        self.msgBox.close()