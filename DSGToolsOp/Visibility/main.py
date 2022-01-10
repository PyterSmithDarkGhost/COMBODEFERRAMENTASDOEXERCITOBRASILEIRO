# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import *
from qgis.gui import *
from .UI.interface_window import Interface

import math

class Main:
    def __init__(self, iface):
        '''Construtor'''
        self.iface = iface
        self.isOpen = False

    def initGui(self):
        #CRIAR ACTIONS
        
        #INICIAR VARIÁEIS E SINAIS
        self.initVariables()
        self.initSignals()
        self.openWindow()
        self.isOpen = False
        
    def unload(self):
        pass
       
    def initVariables(self):
        self.msgBox = QMessageBox()
        self.canvas = self.iface.mapCanvas()
        self.dockWindow = Interface(self.iface)

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
    