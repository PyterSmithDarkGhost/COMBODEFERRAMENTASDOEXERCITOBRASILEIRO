# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QMessageBox
import qgis


try:
    from qgis.PyQt.QtWidgets import *
except:
    pass


from . import resources
from .tools.profiletool_core import ProfileToolCore
from .ui.layerselection import LayerSelection

class ProfilePlugin:

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.profiletool = None
        self.dockOpened = False
        self.canvas.mapToolSet.connect(self.mapToolChanged)
        self.layerselection = LayerSelection()
        self.layerselection.selected.connect(self.run)

    def initGui(self):
        pass

    def unload(self):
        try:
            self.profiletool.dockwidget.close()
            self.dockOpened = False
        except:
            pass
            
        try:
            self.canvas.mapToolSet.disconnect(self.mapToolChanged)
        except:
            pass
    
    def pre_run(self):
        self.layerselection.show()
    
    def run(self, l = '0'):
        if not self.dockOpened:
            if l == None:
                return
            self.profiletool = ProfileToolCore(self.iface,self)
            self.profiletool.dockwidget.activateButton.clicked.connect(self.enableTool)
            self.profiletool.dockwidget.creditsButton.clicked.connect(self.about)
            self.iface.addDockWidget(self.profiletool.dockwidget.location, self.profiletool.dockwidget)
            self.profiletool.dockwidget.closed.connect(self.cleaning)
            self.dockOpened = True
            self.profiletool.activateProfileMapTool()
        else:
            self.profiletool.activateProfileMapTool()
        
    def enableTool(self):
        self.run()
		
    def about(self):
        QMessageBox.information(self.profiletool.dockwidget, u"Sobre","Profile Tool Plugin\n\nThe Profile Plugin plots terrain profiles along interactive pointed or selected polylines.\n\nData could come from raster layer or point vector layer with elevation field.\nGraph could be exported to SVG or PNG format. The polyline used  can be exported to 3D polyline in dxf format.\n\nPlease send your reflections, opinions, suggestions and wishes (especially related to this plugin;) on https://github.com/etiennesky/profiletool/issues\n\nProfile Tool Plugin - License GNU GPL 2\nWritten in 2008 by Borys Jurgiel\nWritten in 2012 by Borys Jurgiel, Patrice Verchere\n\nREQUIREMENTS:\n- Qwt5 (python-qwt5-qt4) and/or python-matplotlib\n- QT ver 4.1 for saving to PDF and 4.3 for saving to SVG\n");
        
    def cleaning(self):  
        self.dockOpened = False
        self.profiletool.rubberband.reset(self.profiletool.polygon)
        self.profiletool.rubberbandbuf.reset()
        self.profiletool.rubberbandpoint.hide()
        self.canvas.unsetMapTool(self.profiletool.toolrenderer.tool)
        self.canvas.setMapTool(self.profiletool.saveTool)

        self.iface.mainWindow().statusBar().showMessage( "" )
        
    def mapToolChanged(self,newtool,oldtool = None):
        pass
            