# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from qgis import processing


class Mosaic(QtWidgets.QWidget):

    def __init__(self, iface):
        super(Mosaic, self).__init__()
        '''Constructor'''
        processing.execAlgorithmDialog('DSGToolsOpProvider:mosaic')

    def cancel(self):
        self.close()
