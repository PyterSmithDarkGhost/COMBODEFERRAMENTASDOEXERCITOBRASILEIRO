# -*- coding: utf-8 -*-
'''
/***************************************************************************
 DSGTools Op
                                 A QGIS plugin
 Ferramentas para planejamento militar do Exército Brasileiro
                             -------------------
        begin                : 2017-01-01
        copyright            : (C) 2017 by Diego Benincasa
        email                : benincasa.diego@eb.mil.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''

from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtGui, QtCore, uic
import os, sys, webbrowser
from qgis.utils import iface
from qgis.core import QgsMapLayer, QgsProject
from qgis.PyQt.QtWidgets import QToolBar, QAction, QMessageBox, QMenu
from qgis.PyQt.QtGui import QIcon
from .BDGEx.bdgexGuiManager import BDGExGuiManager

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'auxiliar'))

class DSGToolsOp:
	def __init__(self, iface):
		self.iface = iface
		self.actions = []
    	
	def initGui(self):
		self.initVariables()
		self.loadTools()

	def initPlugin(self):
		pass

	def initVariables(self):
		self.menuBar = self.iface.mainWindow().menuBar()
		self.dsgToolsOp = QMenu(self.iface.mainWindow())
		self.dsgToolsOp.setObjectName(u'DSGToolsOp')
		self.dsgToolsOp.setTitle('Ferramentas Militares')
		self.fieldToolbox = None
		self.menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.dsgToolsOp)

	def unload(self):
		for action in self.actions:
			self.iface.removePluginMenu(u'DSGTools Op',	action)
		if self.dsgToolsOp is not None:
			self.menuBar.removeAction(self.dsgToolsOp.menuAction())
		del self.dsgToolsOp

	def addMenu(self, name, title, icon_file, parentMenu = None):
		self.menuList = []
		child = QMenu(self.dsgToolsOp)
		child.setObjectName(name)
		child.setTitle(title)
		child.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', icon_file)))
		if parentMenu:
			parentMenu.addMenu(child)
		else:
			self.dsgToolsOp.addMenu(child)
		self.menuList.append(child)
		return child

	def add_action(self,
				icon_path,
				text,
				callback,
				enabled_flag=True,
				add_to_menu=True,
				add_to_toolbar=True,
				status_tip=None,
				whats_this=None,
				parent=None):
        
		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def loadTools(self):
		pass

		self.bdgexGuiManager = BDGExGuiManager(self, self.iface, self.dsgToolsOp, toolbar = None)
		self.bdgexGuiManager.initGui()

		self.ms_action = self.add_action(
		 	os.path.join(os.path.dirname(__file__), 'icons', 'militarySimbology.png'),
		 	text=u'Simbologia Militar',
		 	callback=self.loadMilitarySimbology,
		 	parent=self.dsgToolsOp,
		 	add_to_menu=False,
		 	add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.ms_action)

		self.pt_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'profileIcon.png'),
			text=u'Traçar perfil do terreno',
			callback=self.loadProfileTool,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.pt_action)
		from .ProfileTool.profileplugin import ProfilePlugin as Main_ProfileTool
		self.mainProfileTool = Main_ProfileTool(iface)

		self.vis_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'visib.png'),
			text=u'Mapa de visibilidade',
			callback=self.loadVisibility,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.vis_action)
		from .Visibility.main import Main as Main_Visib
		self.mainVisib = Main_Visib(iface)

		self.ar_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'arearange.png'),
			text=u'Geração de área de alcance de armamento',
			callback=self.loadAreaRange,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.ar_action.setCheckable(True)
		self.dsgToolsOp.addAction(self.ar_action)
		from .AreaRange.areaRange import AreaRange as Main_AreaRange
		self.mainAreaRange = Main_AreaRange(iface)

		self.miA_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'findmiarea.png'),
			text=u'Localizar carta topográfca (MI) por região',
			callback=self.loadDeterminarMIArea,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.miA_action)
		from .DeterminarMIArea.main import Main as Main_MIArea
		self.mainMIArea = Main_MIArea(iface)
        
		self.dec_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'declconv.png'),
			text=u'Declinação magnética e convergência meridiana',
			callback=self.loadDeclinacaoConvergencia,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.dec_action)
		from .DeclinacaoConvergencia.main import Main as Main_DecConv
		self.mainDecConv = Main_DecConv(iface)

		self.sd_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'shaderIcon.png'),
			text=u'Sombrear terreno',
			callback=self.loadShaderTool,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.sd_action)
		from .Shader.main import Main as Main_Shader
		self.mainShaderTool = Main_Shader(iface)

		self.nd_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'numericaldigitize.png'),
			text=u'Criação de pontos por coordenadas',
			callback=self.loadNumericalDigitize,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.nd_action)

		self.mv_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'numericalvertexedit.png'),
			text=u'Mover pontos por coordenadas',
			callback=self.loadMoveVertex,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.mv_action)

		self.az_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'azimuth.png'),
			text=u'Criação de pontos por azimute e distância',
			callback=self.loadAzimuthTool,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.az_action.setCheckable(True)
		self.dsgToolsOp.addAction(self.az_action)
		from .AzimuthDistance.azimuthTool import AzimuthTool as Main_AzimuthTool
		self.mainAzimuthTool = Main_AzimuthTool(iface)
		
		self.geo_action = self.add_action(
		 	os.path.join(os.path.dirname(__file__), 'icons', 'geocoder.png'),
		 	text=u'Geocodificação',
		 	callback=self.loadGeocoding,
		 	parent=self.dsgToolsOp,
		 	add_to_menu=False,
		 	add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.geo_action)
		from .QuickGeocoder.geocoder import QuickGeocoder as Main_Geocoding
		self.mainGeocoding = Main_Geocoding(iface)

		self.azgen_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'azimuthgen.png'),
			text=u'Gerador de azimute e distância',
			callback=self.loadAzimuthGenerator,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.azgen_action)
		from .AzimuthGenerator.main import Main as Main_AzimuthGen
		self.mainAzimuthGen = Main_AzimuthGen(iface)

		self.rd_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'rendezvous.png'),
			text=u'Plano de chamada',
			callback=self.loadRendezvous,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.rd_action)
		from .Rendezvous.main import Main as Main_Rendezvous
		self.mainRendezvous = Main_Rendezvous(iface)

		self.vfaction = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'dimensionsvf.png'),
			text=u'Calculadora de Coordenadas e Dimensões',
			callback=self.loadVirtualFieldGenerator,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.vfaction)
		
		self.auc_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'convang.png'),
			text=u'Conversor de unidades angulares',
			callback=self.loadAngleUnitConverter,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.auc_action)

		self.mt_action = self.add_action(
			os.path.join(os.path.dirname(__file__), 'icons', 'measuretool.png'),
			text=u'Medição durante aquisição vetorial',
			callback=self.loadMeasureTool,
			parent=self.dsgToolsOp,
			add_to_menu=False,
			add_to_toolbar=False)
		self.mt_action.setCheckable(True)
		self.dsgToolsOp.addAction(self.mt_action)
		from .measureTool.measureTool import MeasureTool as Main_MeasureTool
		self.mainMeasureTool = Main_MeasureTool(iface)

		self.ms_action = self.add_action(
		 	os.path.join(os.path.dirname(__file__), 'icons', 'help.png'),
		 	text=u'Ajuda',
		 	callback=self.loadHelp,
		 	parent=self.dsgToolsOp,
		 	add_to_menu=False,
		 	add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.ms_action)

		self.ms_action = self.add_action(
		 	os.path.join(os.path.dirname(__file__), 'icons', 'dsg.png'),
		 	text=u'Sobre',
		 	callback=self.loadAbout,
		 	parent=self.dsgToolsOp,
		 	add_to_menu=False,
		 	add_to_toolbar=False)
		self.dsgToolsOp.addAction(self.ms_action)

	def loadDeterminarMIArea(self):
		"""
        Finds topographic chart within a user-defined box
        """
		if self.mainMIArea.isOpen == False:
			self.mainMIArea.initGui()
    
	def loadMoveVertex(self):
		"""
        Moves points to a new user-input location
        """
		from .numericalVertexEdit.numericalvertexedit import NumericalVertexEdit as Main_MoveVertex
		self.mainMoveVertex = Main_MoveVertex(iface)
		self.mainMoveVertex.initGui()
		self.mainMoveVertex.run()
        
	def loadNumericalDigitize(self):
		"""
        Creates points by user input of coordinates
        """
		from .numericalDigitize.numericalDigitize import NumericalDigitize as Main_NumericalDigitize
		self.mainNumericalDigitize = Main_NumericalDigitize(iface)
		self.mainNumericalDigitize.initGui()
		self.mainNumericalDigitize.run()
    
	def loadDeclinacaoConvergencia(self):
		"""
        Computes magnetic heading and meridian convergence
        """
		if self.mainDecConv.isOpen == False:
			self.mainDecConv.initGui()
    
	def loadAngleUnitConverter(self):
		"""
        Convert units from degrees to milliradian
        """
		from .AngleUnitConverter.main import Main
		dialogBoxAng = Main(iface)
		dialogBoxAng.exec_()

	def loadGeocoding(self):
		"""
        Geocode and reverse geocode dock
        """
		if self.mainGeocoding.pluginIsActive == False:
			self.mainGeocoding.run()

	def loadMilitarySimbology(self):
		"""
        Shows the Military Simbology Dock
        """
		from .MilitarySimbologyTools.main import Main
		main = Main()
		dlg = main.getFrame()
		dlg.setGeometry(700, 500, 100, 50)
		if dlg:
			dlg.show()

	def loadMeasureTool(self):
		"""
        Add icons to toolbar for measuring features during their acquisition
        """
		if self.mt_action.isChecked():
			self.mainMeasureTool.initGui()
		else:
			self.mainMeasureTool.unload()
        
	def loadProfileTool(self):
		"""
        Generates terrain profile
        """
		hasRaster = False
		for l in QgsProject.instance().mapLayers().values():
			if l.type() == QgsMapLayer.RasterLayer:
				hasRaster = True
				break
		if hasRaster == False:
			msgBox = QMessageBox(QMessageBox.Information, u"Informação", u"Não há camadas raster para traçar o perfil.", QMessageBox.Ok)
			msgBox.exec_()
			return
		if self.mainProfileTool.dockOpened == False:
			self.mainProfileTool.run()
        
	def loadVirtualFieldGenerator(self):
		"""
        Computes geometries dimensions and centroids
        """
		from .VirtualFieldGenerator.virtualFieldGenerator import VirtualFieldGenerator
		dialogVFG = VirtualFieldGenerator(iface)
		dialogVFG.exec_()

	def loadShaderTool(self):
		"""
		Terrain shading based on sun positon on given time and given observer position
		"""
		if self.mainShaderTool.isOpen == False:
			self.mainShaderTool.initGui()

	def loadAzimuthTool(self):
		"""
        Adds icons to toolbar for creating points from given point, distance and azymuth
        """
		if self.az_action.isChecked():
			self.mainAzimuthTool.initGui()
		else:
			self.mainAzimuthTool.unload()
			
	def loadAreaRange(self):
		"""
        Adds icons to toolbar for generating gun range area
        """
		if self.ar_action.isChecked():
			self.mainAreaRange.initGui()
		else:
			self.mainAreaRange.unload()

	def loadAzimuthGenerator(self):
		"""
        Create azimuth and distance list for given geometries or set of points
        """
		if self.mainAzimuthGen.isOpen == False:
			self.mainAzimuthGen.initGui()

	def loadRendezvous(self):
		"""
		From given set os points create Voronoi diagrams and its centroids
		"""
		if self.mainRendezvous.isOpen == False:
			self.mainRendezvous.initGui()

	def loadMobPath(self):
		"""
		Creates raster with paths available from restriction vector layers and slope ranges
		"""
		from .MobilityPath.mobilityPath import MobilityPath
		dialogMobPath = MobilityPath(iface)
		dialogMobPath.exec_()
		
	def loadVisibility(self):
		"""
        Creates visibility from given point and observer height 
        """
		if self.mainVisib.isOpen == False:
			self.mainVisib.initGui()
			
	def loadHelp(self):
		"""
        Open github wiki page
        """
		webbrowser.open('https://github.com/dsgoficial/DSGToolsOp/wiki')

	def loadAbout(self):
		"""
        Open "about" window
        """
		from .About.about import About
		dialogAbout = About()
		dialogAbout.exec_()
