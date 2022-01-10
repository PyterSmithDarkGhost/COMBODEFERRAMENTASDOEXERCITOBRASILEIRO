#Sun position obtained using sunposition.py by Samuel Bear Powell
#https://github.com/s-bear/sun-position

# -*- coding: utf-8 -*-
from qgis.core import *
from qgis.gui import *
from .interface import Interface

class Main:
    def __init__(self, iface):
        '''Construtor'''
        self.iface = iface
        self.isOpen = False

    def initGui(self):
        self.initVariables()
        self.initSignals()
        self.openWindow()
        self.isOpen = False
        
    def unload(self):
        pass
       
    def initVariables(self):
        self.dockWindow = Interface()

    def initSignals(self):
        self.dockWindow.closeEvent = self.closeDock
    
    def initPlugin(self):
        pass
    
    def openWindow(self):
        if self.isOpen == False:
            self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockWindow)
            self.isOpen = True
            
    def closeDock(self, e):
        self.dockWindow.ativarButton.setChecked(False)
        del self.dockWindow
        self.isOpen = False

    def closeWindow(self, e):
        pass

