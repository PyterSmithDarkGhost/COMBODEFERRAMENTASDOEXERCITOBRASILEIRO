# -*- coding: utf-8 -*-

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import QgsMapLayer, QgsMapLayerProxyModel
import platform
import os
#from layerselector import Ui_LayerSelector

GUI, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layerselector.ui'))

class LayerSelection(QtWidgets.QDialog, GUI):

	selected = pyqtSignal(QgsMapLayer)
	
	def __init__(self):
		super(LayerSelection, self).__init__()
		self.setupUi(self)
		self.buttonBox.clicked.connect(self.getSelectedLayer)
		self.layerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
		
	def getSelectedLayer(self, b):
		if b == QDialogButtonBox.Ok:
			return self.layerCombo.currentLayer()
		else:
			return None
		
		self.close()