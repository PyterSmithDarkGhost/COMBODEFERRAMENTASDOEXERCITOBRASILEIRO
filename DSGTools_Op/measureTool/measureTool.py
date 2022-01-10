# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *

from . import resources_rc

from .EventFilter import EventFilter
from .PointList import PointList


class MeasureTool(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface

    def initGui(self):
        # Criar ação de ativação
        self.enableAction = QAction( QIcon(":/plugins/DsgTools/DsgToolsOp/MilitaryTools/measureTool/icon.png"), u"Ativar medição da aquisição", self.iface.mainWindow())
        self.enableAction.setCheckable(True)
        
        # pointList: isso armazena todos os pontos
        self.pointList = PointList()

        # EventFilter: este widget filtrará os mouseEvents e os restringirá, se necessário
        self.eventFilter = EventFilter(self.iface, self.pointList, self.enableAction)

        # Precisamos da janela de visualização da tela para rastrear o mouse para que mouseMoveEvents aconteça
        self.iface.mapCanvas().viewport().setMouseTracking(True)

        # Nós instalamos o eventFilter na viewport da tela para obter os eventos do mouse
        self.iface.mapCanvas().viewport().installEventFilter( self.eventFilter )

        # Nós instalamos o eventFilter na própria tela para obter os principais eventos
        self.iface.mapCanvas().installEventFilter( self.eventFilter )

        # Adicionar itens de menu e barras de ferramentas
        self.toolbar = self.iface.addToolBar(u'Medição na aquisição')
        self.toolbar.addAction(self.enableAction)

        # SINAIS
        # Nós conectamos o sinal mapToolSet para que possamos ativar / desativar a widget
        self.iface.mapCanvas().mapToolSet.connect(self.maptoolChanged)

        # E nós o executamos para definir o estado correto após o carregamento
        self.maptoolChanged()
        self.iface.mapCanvas().currentLayerChanged.connect(self.maptoolChanged)

    def unload(self):
        # remove o event filter
        self.eventFilter.close()
        self.iface.mapCanvas().viewport().removeEventFilter( self.eventFilter )
        self.iface.mapCanvas().removeEventFilter( self.eventFilter )

        # e remova o menu de itens
        self.toolbar.removeAction(self.enableAction)
        del self.toolbar

        # e remova o sinal maptoolchanded isEditTool
        self.iface.mapCanvas().mapToolSet.disconnect( self.maptoolChanged )

    def maptoolChanged(self):
        self.eventFilter.active = (self.iface.mapCanvas().mapTool() is not None and self.iface.mapCanvas().mapTool().flags() == QgsMapTool.EditTool)
