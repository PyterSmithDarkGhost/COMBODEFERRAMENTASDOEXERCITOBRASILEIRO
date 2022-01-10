# -*- coding: utf-8 -*-
from qgis.PyQt import uic, QtWidgets
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'about.ui'))

class About(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self):
        """Constructor."""
        super(About, self).__init__()
        self.setupUi(self)
