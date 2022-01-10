# -*- coding: UTF-8 -*-
import os, processing
from qgis.PyQt import QtGui, uic, QtCore, QtWidgets
from qgis.core import QgsProject, QgsMapLayerProxyModel, QgsMessageLog, Qgis
from qgis.PyQt.QtWidgets import QMessageBox

GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'window.ui'))

class Interface(QtWidgets.QDockWidget, GUI):
    def __init__(self):
        super(Interface, self).__init__()
        self.setupUi(self)
        self.initSignals()
        self.layerCombo.setFilters(QgsMapLayerProxyModel.PointLayer)
    
    def initSignals(self):
        self.ativarButton.clicked.connect(self.doWork)      
        
    def doWork(self):
        if not self.layerCombo.currentLayer():
            QMessageBox.critical(self, u"Erro", u"Nenhuma camada de pontos selecionada. Selecione uma camada.")
            return

        kmeansLayer = processing.run("native:kmeansclustering", {'INPUT': self.layerCombo.currentLayer(),
        'CLUSTERS': self.knumberBox.value(),
        'FIELD_NAME': "CLUSTER_ID",
        'OUTPUT': 'memory:'})['OUTPUT']
        collectedLayer = processing.run("native:collect", {'INPUT': kmeansLayer,
        'FIELD': "CLUSTER_ID",
        'OUTPUT': 'memory:'})['OUTPUT']
        centroidsLayer = processing.run("native:centroids", {'INPUT': collectedLayer,
        'OUTPUT': 'memory:'})['OUTPUT']
        voronoiLayer = processing.run("qgis:voronoipolygons", {'INPUT': centroidsLayer,
        'BUFFER': 100,
        'OUTPUT': 'memory:'})['OUTPUT']

        voronoiLayer.setName('Zonas')
        centroidsLayer.setName('Pontos de encontro')
        QgsProject.instance().addMapLayer(voronoiLayer)
        QgsProject.instance().addMapLayer(centroidsLayer)

