# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

from qgis.core import *
from qgis.gui import *
import qgis

from .selectlinetool import SelectLineTool

class ProfiletoolMapToolRenderer():

    def __init__(self, profiletool):
        self.profiletool = profiletool
        self.iface = self.profiletool.iface
        self.canvas = self.profiletool.iface.mapCanvas()
        self.tool = ProfiletoolMapTool(self.canvas)
        self.pointstoDraw = []
        self.pointstoCal = []
        self.dblclktemp = None
        self.lastFreeHandPoints = []
        
        self.textquit0 = u"Botão esquerdo para traçar linha. Duplo-clique para finalizar. Botão direito para cancelar."
        self.textquit1 = u"Selecione uma linha em uma camada vetorial. Clique com botão direito para cancelar."
        
        self.layerindex = None
        self.previousLayer = None
    
    def moved(self,position):
        if self.profiletool.dockwidget.selectionmethod == 0:
            if len(self.pointstoDraw) > 0:
                #Get mouse coords
                mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
                #Draw on temp layer
                self.profiletool.rubberband.reset(qgis.core.QgsWkbTypes.LineGeometry)
                for i in range(0,len(self.pointstoDraw)):
                     self.profiletool.rubberband.addPoint(QgsPointXY(self.pointstoDraw[i][0],self.pointstoDraw[i][1]))
                self.profiletool.rubberband.addPoint(QgsPointXY(mapPos.x(),mapPos.y()))
        if self.profiletool.dockwidget.selectionmethod == 1:
            return

    def rightClicked(self,position):
        if self.profiletool.dockwidget.selectionmethod == 0:
            mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
            newPoints = [[mapPos.x(), mapPos.y()]]
            if len(self.pointstoDraw) > 0:
                self.pointstoDraw = []
                self.pointstoCal = []
                self.profiletool.rubberband.reset(self.profiletool.polygon)
                self.profiletool.rubberbandbuf.reset()
                self.profiletool.rubberbandpoint.hide()
            else:
                self.cleaning()
        if self.profiletool.dockwidget.selectionmethod == 1:
            try:
                self.previousLayer.removeSelection( False )
            except:
                self.iface.mainWindow().statusBar().showMessage(u"erro no clique direito")
            self.cleaning()

    def leftClicked(self,position):
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
        newPoints = [[mapPos.x(), mapPos.y()]]
        if self.profiletool.doTracking :
            self.profiletool.rubberbandpoint.hide()
            
        if self.profiletool.dockwidget.selectionmethod == 0:
            if newPoints == self.dblclktemp:
                self.dblclktemp = None
                return
            else :
                if len(self.pointstoDraw) == 0:
                    self.profiletool.rubberband.reset(self.profiletool.polygon)
                    self.profiletool.rubberbandbuf.reset()
                self.pointstoDraw += newPoints
            QgsMessageLog.logMessage(str(mapPos.x())+'***'+str(mapPos.y()), level=Qgis.Warning )

        if self.profiletool.dockwidget.selectionmethod == 1:
            result = SelectLineTool().getPointTableFromSelectedLine(self.iface, self.tool, newPoints, self.layerindex, self.previousLayer , self.pointstoDraw)
            self.pointstoDraw = result[0]
            self.layerindex = result[1]
            self.previousLayer = result[2]
            self.profiletool.calculateProfil(self.pointstoDraw, False)
            self.lastFreeHandPoints = self.pointstoDraw
            self.pointstoDraw = []
            self.iface.mainWindow().statusBar().showMessage(self.textquit1)

    def doubleClicked(self,position):
        if self.profiletool.dockwidget.selectionmethod == 0:
            #Validation of line
            mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
            newPoints = [[mapPos.x(), mapPos.y()]]
            self.pointstoDraw += newPoints
            #launch analyses
            self.iface.mainWindow().statusBar().showMessage(str(self.pointstoDraw))
            self.profiletool.calculateProfil(self.pointstoDraw)
            #Reset
            self.lastFreeHandPoints = self.pointstoDraw
            self.pointstoDraw = []
            #temp point to distinct leftclick and dbleclick
            self.dblclktemp = newPoints
            self.iface.mainWindow().statusBar().showMessage(self.textquit0)
        if self.profiletool.dockwidget.selectionmethod == 1:
            return
            
    def cleaning(self):
        try:
            self.previousLayer.removeSelection(False)
        except:
            pass
        self.profiletool.rubberbandpoint.hide()
        self.canvas.unsetMapTool(self.tool)
        self.canvas.setMapTool(self.profiletool.saveTool)
        self.profiletool.rubberband.reset(self.profiletool.polygon)
        self.profiletool.rubberbandbuf.reset()
        self.iface.mainWindow().statusBar().showMessage( "" )
        
    def connectTool(self):
        self.tool.moved.connect(self.moved)
        self.tool.rightClicked.connect(self.rightClicked)
        self.tool.leftClicked.connect(self.leftClicked)
        self.tool.doubleClicked.connect(self.doubleClicked)
        self.tool.desactivate.connect(self.deactivate)
        
        if self.profiletool.dockwidget.selectionmethod == 0:
            self.iface.mainWindow().statusBar().showMessage(self.textquit0)
        elif self.profiletool.dockwidget.selectionmethod == 1:
            self.iface.mainWindow().statusBar().showMessage(self.textquit1)

    def deactivate(self):
        self.tool.moved.disconnect(self.moved)
        self.tool.rightClicked.disconnect(self.rightClicked)
        self.tool.leftClicked.disconnect(self.leftClicked)
        self.tool.doubleClicked.disconnect(self.doubleClicked)
        self.tool.desactivate.disconnect(self.deactivate)
        self.profiletool.rubberbandpoint.hide()
        #self.profiletool.rubberband.reset(self.profiletool.polygon)
        self.iface.mainWindow().statusBar().showMessage("")

class ProfiletoolMapTool(QgsMapTool):
    moved = pyqtSignal(dict)
    rightClicked = pyqtSignal(dict)
    leftClicked = pyqtSignal(dict)
    doubleClicked = pyqtSignal(dict)
    desactivate = pyqtSignal()

    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)

    def canvasMoveEvent(self,event):
        self.moved.emit({'x': event.pos().x(), 'y': event.pos().y()})

    def canvasReleaseEvent(self,event):
        if event.button() == Qt.RightButton:
            self.rightClicked.emit({'x': event.pos().x(), 'y': event.pos().y()})
        else:
            self.leftClicked.emit( {'x': event.pos().x(), 'y': event.pos().y()} )

    def canvasDoubleClickEvent(self,event):
        self.doubleClicked.emit( {'x': event.pos().x(), 'y': event.pos().y()} )

    def activate(self):
        QgsMapTool.activate(self)
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.desactivate.emit()
        QgsMapTool.deactivate(self)

    def isZoomTool(self):
        return False

    def setCursor(self,cursor):
        self.cursor = QCursor(cursor)
