# -*- coding: utf-8 -*-

from qgis.core import *
from qgis.gui import *
import qgis

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtSvg import *
try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

import platform
from math import sqrt

import numpy as np

from .. import pyqtgraph as pg
from ..pyqtgraph import exporters 
pg.setConfigOption('background', 'w')

class PlottingTool:

    def changePlotWidget(self, library, frame_for_plot):
        
        if library == "PyQtGraph":
            plotWdg = pg.PlotWidget()
            plotWdg.showGrid(True,True,0.5)
            datavline = pg.InfiniteLine(0, angle=90 ,pen=pg.mkPen('r',  width=1) , name = 'cross_vertical' )
            datahline = pg.InfiniteLine(0, angle=0 , pen=pg.mkPen('r',  width=1) , name = 'cross_horizontal')
            plotWdg.addItem(datavline)
            plotWdg.addItem(datahline)
            #cursor
            xtextitem = pg.TextItem('X : /', color = (0,0,0), border = pg.mkPen(color=(0, 0, 0),  width=1), fill=pg.mkBrush('w'), anchor=(0,1))
            ytextitem = pg.TextItem('Y : / ', color = (0,0,0) , border = pg.mkPen(color=(0, 0, 0),  width=1), fill=pg.mkBrush('w'), anchor=(0,0))
            plotWdg.addItem(xtextitem)
            plotWdg.addItem(ytextitem)
            
            plotWdg.getViewBox().autoRange( items=[])
            plotWdg.getViewBox().disableAutoRange()
            plotWdg.getViewBox().border = pg.mkPen(color=(0, 0, 0),  width=1)
            
            return plotWdg
        
        
        
    def drawVertLine(self,wdg, pointstoDraw, library):
        if library == "PyQtGraph":
            pass
        
    def attachCurves(self, wdg, profiles, model1, library):
    
        if library == "PyQtGraph":
            #cretae graph
            for i in range(0 , model1.rowCount()):
                tmp_name = ("%s#%d") % (profiles[i]["layer"].name(), profiles[i]["band"])
                #case line outside the raster
                y = np.array(profiles[i]["z"], dtype=np.float)  #replace None value by np.nan
                x = np.array(profiles[i]["l"])
                wdg.plotWdg.plot(x, y, pen=pg.mkPen( model1.item(i,1).data(Qt.BackgroundRole),  width=2) , name = tmp_name)
            #set it visible or not
            for i in range(0 , model1.rowCount()):
                tmp_name = ("%s#%d") % (profiles[i]["layer"].name(), profiles[i]["band"])
                for item in wdg.plotWdg.getPlotItem().listDataItems():
                    if item.name() == tmp_name:
                        item.setVisible(model1.item(i,0).data(Qt.CheckStateRole))
                        
        

    def findMin(self,profiles, nr):
        minVal = min( z for z in profiles[nr]["z"] if z is not None )
        maxVal = max( z for z in profiles[nr]["z"] if z is not None ) + 1
        d = ( maxVal - minVal ) or 1
        return minVal

    def findMax(self,profiles, nr):
        minVal = min( z for z in profiles[nr]["z"] if z is not None )
        maxVal = max( z for z in profiles[nr]["z"] if z is not None ) + 1
        d = ( maxVal - minVal ) or 1
        return maxVal
        
    def plotRangechanged(self, wdg, library):
        if library == "PyQtGraph":
            range = wdg.plotWdg.getViewBox().viewRange()
            wdg.disconnectYSpinbox()
            wdg.sbMaxVal.setValue(range[1][1])
            wdg.sbMinVal.setValue(range[1][0])
            wdg.connectYSpinbox()
         
    def reScalePlot(self, wdg, profiles, library,auto = False):
        if profiles == None:
            return
        minimumValue = wdg.sbMinVal.value()
        maximumValue = wdg.sbMaxVal.value()
        
        if minimumValue == maximumValue:
            minimumValue = 1000000000
            maximumValue = -1000000000
            for i in range(0,len(profiles)):
                if profiles[i]["layer"] != None and len([z for z in profiles[i]["z"] if z is not None]) > 0:
                    if self.findMin(profiles, i) < minimumValue:
                        minimumValue = self.findMin(profiles, i)
                    if self.findMax(profiles, i) > maximumValue:
                        maximumValue = self.findMax(profiles, i)
                    wdg.sbMaxVal.setValue(maximumValue)
                    wdg.sbMinVal.setValue(minimumValue)
                    wdg.sbMaxVal.setEnabled(True)
                    wdg.sbMinVal.setEnabled(True)

        if minimumValue < maximumValue:
            if library == "PyQtGraph":
                wdg.disconnectPlotRangechanged()
                if auto:
                    wdg.plotWdg.getViewBox().autoRange( items=wdg.plotWdg.getPlotItem().listDataItems())
                    wdg.plotRangechanged()
                else:
                    wdg.plotWdg.getViewBox().setYRange( minimumValue,maximumValue , padding = 0 )
                wdg.connectPlotRangechanged()
            
    def clearData(self, wdg, profiles, library):
        if not profiles:
            return
            
        if library == "PyQtGraph":
            pitems = wdg.plotWdg.getPlotItem().listDataItems()
            for item in pitems:
                wdg.plotWdg.removeItem(item)
            try:
                wdg.plotWdg.scene().sigMouseMoved.disconnect(self.mouseMoved)
            except:
                pass
        
        wdg.sbMaxVal.setValue(0)
        wdg.sbMinVal.setValue(0)
        
    def changeColor(self,wdg, library, color1, name):
    
        if library == "PyQtGraph":
            pitems = wdg.plotWdg.getPlotItem()
            for i, item in enumerate(pitems.listDataItems()):
                if item.name() == name:
                    item.setPen( color1,  width=2)
          
    def changeAttachCurve(self, wdg, library, bool, name):
    
        if library == "PyQtGraph":
            pitems = wdg.plotWdg.getPlotItem()
            for i, item in enumerate(pitems.listDataItems()):
                if item.name() == name:
                    if bool:
                        item.setVisible(True)
                    else:
                        item.setVisible(False)
         

    def manageMatplotlibAxe(self, axe1):
        axe1.grid()
        axe1.tick_params(axis = "both", which = "major", direction= "out", length=10, width=1, bottom = True, top = False, left = True, right = False)
        axe1.minorticks_on()
        axe1.tick_params(axis = "both", which = "minor", direction= "out", length=5, width=1, bottom = True, top = False, left = True, right = False)


    def outSVG(self, iface, wdg, mdl, library):
        fileName = QFileDialog.getSaveFileName(iface.mainWindow(), u"Salvar como",u"Perfil do terreno" + u".png", "Scalable Vector Graphics (*.svg)")
        if fileName:
            if isinstance(fileName,tuple):  #pyqt5 case
                fileName = fileName[0]
            if fileName[-4:].lower() != '.svg':
                fileName += '.svg'
                
            if library == "PyQtGraph":
                exporter = exporters.SVGExporter(wdg.plotWdg.getPlotItem().scene())
                exporter.export(fileName = fileName)
            
    def outPNG(self, iface, wdg, mdl, library):
        fileName = QFileDialog.getSaveFileName(iface.mainWindow(), u"Salvar como",u"Perfil do terreno" + u".png", "Portable Network Graphics (*.png)")[0]
        if fileName:
            if library == "PyQtGraph":
                exporter =  exporters.ImageExporter(wdg.plotWdg.getPlotItem())
                if fileName[-4:].lower() != '.png':
                    fileName += '.png'
                exporter.export(fileName)
               
    