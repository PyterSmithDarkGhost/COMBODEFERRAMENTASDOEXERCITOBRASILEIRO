# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *
from .interface import Interface
from .vertexfindertool import VertexFinderTool
import os, sys
from . import resources

class NumericalVertexEdit:

  def __init__(self, iface):
    self.iface = iface
    self.canvas = self.iface.mapCanvas()
      
  def initGui(self):
    
    mc = self.canvas
    layer = mc.currentLayer()
      
    self.dialog = Interface()
    self.dialog.finished.connect(self.moveVertex2)
    
    self.tool = VertexFinderTool(self.iface)

  def unload(self):
    pass
     
  def run(self):
    self.canvas.setMapTool(self.tool)
    self.tool.pointFound.connect(self.moveVertex)
        
  def moveVertex(self,feature,layerCrs):
    self.feature = feature
    oldpoint = feature.geometry().asPoint()
    params = []
    params.append(oldpoint.x())
    params.append(oldpoint.y())
    params.append(layerCrs)
    
    self.layerCrs = layerCrs
    
    self.dialog.setCoords(params)
    self.dialog.exec_()
    
  def moveVertex2(self, newpoint, newcrs):
    transformer = QgsCoordinateTransform(newcrs, self.layerCrs, QgsProject.instance())
    newPt = transformer.transform(newpoint)
    
    layer = self.iface.activeLayer()
    
    geom = QgsGeometry.fromPointXY(newPt)
    layer.startEditing()
    layer.changeGeometry(self.feature.id(), geom)
    
    layer.triggerRepaint()
