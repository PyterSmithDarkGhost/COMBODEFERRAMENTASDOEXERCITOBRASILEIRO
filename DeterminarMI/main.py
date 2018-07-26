# -*- coding: utf-8 -*-
from PyQt4.QtGui import QAction, QIcon, QToolButton, QMenu
from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import QMessageBox
from icons import resources_rc
from UI.interface import Interface
from auxiliar.auxiliar import Auxiliar
import math

class Main:
    def __init__(self, iface):
        '''Construtor'''
        self.iface = iface
        self.isOpen = False

    def initGui(self):
        #CRIAR ACTIONS
        
        #INICIAR VARIÁVEIS E SINAIS
        self.initVariables()
        self.initSignals()
        self.openWindow()
        self.isOpen = True
        
    def unload(self):
#        del self.toolbar
        pass
       
    def initVariables(self):
        self.msgBox = QMessageBox()
        self.canvas = self.iface.mapCanvas()
        self.auxiliar = Auxiliar(self.iface)
        self.dockWindow = Interface(self.canvas, self.auxiliar)

    def initSignals(self):
        self.dockWindow.closeEvent = self.closeDock
    
    def initPlugin(self):
        pass
    
    def openWindow(self):
        self.iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockWindow)
        self.isOpen = True
            
    def closeDock(self, e):
        del self.dockWindow
        self.isOpen = False

        vertex_items = [ i for i in self.iface.mapCanvas().scene().items() if issubclass(type(i), QgsVertexMarker)]
        for ver in vertex_items:
            if ver in self.iface.mapCanvas().scene().items():
                self.iface.mapCanvas().scene().removeItem(ver)

    def closeWindow(self, e):
        pass

    def showMessage(self, text):
        self.msgBox.setIcon(QMessageBox.Critical)
        self.msgBox.setWindowTitle("Erro")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.setText(text)
        self.msgBox.exec_()
            
    def closeMsgBox(self, b):
        self.msgBox.close()
        
    