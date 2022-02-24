# -*- coding: utf-8 -*-

#Qt import
from qgis.PyQt import uic, QtCore, QtGui
try:
    from qgis.PyQt.QtGui import QWidget
except:
    from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtSvg import * # required in some distros
#qgis import
import qgis
from qgis.core import *
from qgis.gui import *
#other
import platform
import sys
from math import sqrt
import numpy as np
#plugin import
from .dataReaderTool import DataReaderTool
from .plottingtool import PlottingTool
from .ptmaptool import ProfiletoolMapTool, ProfiletoolMapToolRenderer
from ..ui.ptdockwidget import PTDockWidget

class ProfileToolCore(QWidget):

    def __init__(self, iface,plugincore, parent = None):
        QWidget.__init__(self, parent)
        self.iface = iface
        self.plugincore = plugincore
        #the rubberband
        self.polygon = False
        self.rubberband = QgsRubberBand(self.iface.mapCanvas(), self.polygon)
        self.rubberband.setWidth(2)
        self.rubberband.setColor(QtGui.QColor(QtCore.Qt.red))
        self.rubberbandpoint = QgsVertexMarker(self.iface.mapCanvas())
        self.rubberbandpoint.setColor(QtGui.QColor(QtCore.Qt.red))
        self.rubberbandpoint.setIconSize(5)
        self.rubberbandpoint.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        self.rubberbandpoint.setPenWidth(3)
        
        self.rubberbandbuf = QgsRubberBand(self.iface.mapCanvas())
        self.rubberbandbuf.setWidth(1)
        self.rubberbandbuf.setColor(QtGui.QColor(QtCore.Qt.blue))

        if QtCore.QSettings().value("profiletool/lastdirectory") != '':
            self.loaddirectory = QtCore.QSettings().value("profiletool/lastdirectory")       
        else:
            self.loaddirectory = ''
        
        #mouse tracking
        self.doTracking = False
        #the dockwidget
        self.dockwidget = PTDockWidget(self.iface,self)     
        #dockwidget graph zone
        self.dockwidget.changePlotLibrary( 'PyQtGraph' )
        #the data / results
        self.profiles = None
        #The line information
        self.pointstoDraw = None
        #he renderer for temporary polyline
        self.toolrenderer = None
        #the maptool previously loaded
        self.saveTool = None
        
    def activateProfileMapTool(self):
        self.saveTool = self.iface.mapCanvas().mapTool()
        #Listeners of mouse
        self.toolrenderer = ProfiletoolMapToolRenderer(self)
        self.toolrenderer.connectTool()
        #init the mouse listener comportement and save the classic to restore it on quit
        self.iface.mapCanvas().setMapTool(self.toolrenderer.tool)
        self.dockwidget.selectionMethod(self.dockwidget.comboBox.currentIndex())

    def calculateProfil(self, points1,  vertline = True):
        self.disableMouseCoordonates()
        self.rubberbandbuf.reset()
        self.pointstoDraw = points1
        
        self.removeClosedLayers(self.dockwidget.mdl)
        if self.pointstoDraw == None:
            return
        
        PlottingTool().clearData(self.dockwidget, self.profiles, self.dockwidget.plotlibrary)
        
        self.profiles = []
        
        if vertline:
            PlottingTool().drawVertLine(self.dockwidget, self.pointstoDraw, self.dockwidget.plotlibrary)

        #calculate profiles
        for i in range(0 , self.dockwidget.mdl.rowCount()):
            self.profiles.append( {"layer": self.dockwidget.mdl.item(i,5).data(QtCore.Qt.EditRole) } )
            self.profiles[i]["band"] = self.dockwidget.mdl.item(i,3).data(QtCore.Qt.EditRole)
            if self.dockwidget.mdl.item(i,5).data(QtCore.Qt.EditRole).type() == qgis.core.QgsMapLayer.VectorLayer :
                self.profiles[i], buffer, multipoly = DataReaderTool().dataVectorReaderTool(self.iface, self.toolrenderer.tool, self.profiles[i], self.pointstoDraw, float(self.dockwidget.mdl.item(i,4).data(QtCore.Qt.EditRole)) )
                self.rubberbandbuf.addGeometry(buffer,None)
                self.rubberbandbuf.addGeometry(multipoly,None)
                
            else:
                self.profiles[i] = DataReaderTool().dataRasterReaderTool(self.iface, self.toolrenderer.tool, self.profiles[i], self.pointstoDraw, True)
            
        #plot profiles
        PlottingTool().attachCurves(self.dockwidget, self.profiles, self.dockwidget.mdl, self.dockwidget.plotlibrary)
        PlottingTool().reScalePlot(self.dockwidget, self.profiles, self.dockwidget.plotlibrary)
        self.dockwidget.updateCoordinateTab()
        #Mouse tracking
        if self.doTracking :
            self.rubberbandpoint.show()
        self.enableMouseCoordonates(self.dockwidget.plotlibrary)
        
    def removeClosedLayers(self, model1):
        qgisLayerNames = []
        if int(QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
            qgisLayerNames = [  layer.name()    for layer in self.iface.legendInterface().layers()]
        elif int(QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
            qgisLayerNames = [  layer.name()    for layer in qgis.core.QgsProject().instance().mapLayers().values()]
            
        for i in range(0 , model1.rowCount()):
            layerName = model1.item(i,2).data(QtCore.Qt.EditRole)
            if not layerName in qgisLayerNames:
                self.dockwidget.removeLayer(i)
                self.removeClosedLayers(model1)
                break
    
    def getProfileCurve(self,nr):
        try:
            return self.profiles[nr]["curve"]
        except:
            return None
            
    def activateMouseTracking(self,int1):

        if self.dockwidget.TYPE == 'PyQtGraph':
            
            if int1 == 2 :
                self.doTracking = True
                self.rubberbandpoint.show()
            elif int1 == 0 :
                self.doTracking = False
                self.rubberbandpoint.hide()
    
                   
    def mouseevent_mpl(self,event):
        if event.xdata:
            try:
                if self.vline:
                    self.dockwidget.plotWdg.figure.get_axes()[0].lines.remove(self.vline)
            except Exception as e:
                pass
            xdata = float(event.xdata)
            self.vline = self.dockwidget.plotWdg.figure.get_axes()[0].axvline(xdata,linewidth=2, color = 'k')
            self.dockwidget.plotWdg.draw()
            if not self.pointstoDraw is None:
                geom =  qgis.core.QgsGeometry.fromPolyline([QgsPoint(point[0], point[1]) for point in self.pointstoDraw])
                pointprojected = geom.interpolate(xdata)
                self.rubberbandpoint.show() 
                self.rubberbandpoint.setCenter(pointprojected.asPoint())
            
    def enableMouseCoordonates(self,library):
        if library == "PyQtGraph":
            self.dockwidget.plotWdg.scene().sigMouseMoved.connect(self.mouseMovedPyQtGraph)
            self.dockwidget.plotWdg.getViewBox().autoRange( items=self.dockwidget.plotWdg.getPlotItem().listDataItems())
            self.dockwidget.connectPlotRangechanged()
         
            
    def disableMouseCoordonates(self):
        try:
            self.dockwidget.plotWdg.scene().sigMouseMoved.disconnect(self.mouseMovedPyQtGraph)
        except:
            pass
            
        self.dockwidget.disconnectPlotRangechanged()
        
    def mouseMovedPyQtGraph(self, pos):
            roundvalue = 3

            if self.dockwidget.plotWdg.sceneBoundingRect().contains(pos):
            
                if self.dockwidget.showcursor :
                    range = self.dockwidget.plotWdg.getViewBox().viewRange()
                    mousePoint = self.dockwidget.plotWdg.getViewBox().mapSceneToView(pos)
                    
                    datas = []
                    pitems = self.dockwidget.plotWdg.getPlotItem()
                    ytoplot = None
                    xtoplot = None
                    
                    if len(pitems.listDataItems())>0:
                        #get data and nearest xy from cursor
                        compt = 0
                        for  item in pitems.listDataItems():
                            if item.isVisible() :
                                x,y = item.getData()
                                nearestindex = np.argmin( abs(np.array(x)-mousePoint.x()) )
                                if compt == 0:
                                    xtoplot = np.array(x)[nearestindex]
                                    ytoplot = np.array(y)[nearestindex]
                                else:
                                    if abs( np.array(y)[nearestindex] - mousePoint.y() ) < abs( ytoplot -  mousePoint.y() ):
                                        ytoplot = np.array(y)[nearestindex]
                                        xtoplot = np.array(x)[nearestindex]
                                compt += 1
                        #plot xy label and cursor
                        if not xtoplot is None and not ytoplot is None:
                            for item in self.dockwidget.plotWdg.allChildItems():
                                if str(type(item)) == "<class 'profiletool.pyqtgraph.graphicsItems.InfiniteLine.InfiniteLine'>":
                                    if item.name() == 'cross_vertical':
                                        item.show()
                                        item.setPos(xtoplot)
                                    elif item.name() == 'cross_horizontal':
                                        item.show()
                                        item.setPos(ytoplot)
                                elif str(type(item)) == "<class 'profiletool.pyqtgraph.graphicsItems.TextItem.TextItem'>":
                                    if item.textItem.toPlainText()[0] == 'X':
                                        item.show()
                                        item.setText('X : '+str(round(xtoplot,roundvalue)))
                                        item.setPos(xtoplot,range[1][0] )
                                    elif item.textItem.toPlainText()[0] == 'Y':
                                        item.show()
                                        item.setText('Y : '+str(round(ytoplot,roundvalue)))
                                        item.setPos(range[0][0],ytoplot )
                                    
                    #tracking part
                    if self.doTracking and not xtoplot is None and not ytoplot is None:
                        geom =  qgis.core.QgsGeometry.fromPolyline([QgsPoint(point[0], point[1]) for point in self.pointstoDraw])
                        pointprojected = geom.interpolate(xtoplot)
                        self.rubberbandpoint.show() 
                        #self.rubberbandpoint.setCenter(pointprojected.asPoint())
            
    def prepar_points(self,points1):
        self.tabmouseevent=[]
        len = 0
        for i,point in enumerate(points1):
            if i==0:
                self.tabmouseevent.append([0,point[0],point[1]])
            else:
                len = len + ( (points1[i][0] - points1[i-1][0] )**2 + (points1[i][1] - points1[i-1][1])**2 )**(0.5)
                if len ==0:
                    continue
                self.tabmouseevent.append([float(len) ,float(point[0]),float(point[1])])
        self.tabmouseevent = self.tabmouseevent[:-1]