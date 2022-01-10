# -*- coding: utf-8 -*-
from qgis.PyQt import QtCore
from qgis.core import QgsField, QgsExpression, QgsMapLayerProxyModel, QgsVectorLayer, QgsMapLayer
from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtWidgets import QMessageBox
import os


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'convAng_dialog_base.ui'))


class Main(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface):
        super(Main, self).__init__()
        '''Construtor'''
        self.setupUi(self)
        self.mapLayerSelection.layerChanged.connect(self.attributeSelection.setLayer)
        self.mapLayerSelection.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.okButton.pressed.connect(self.doWork)
        self.cancelButton.pressed.connect(self.cancel)
        self.iface = iface

    def cancel(self):
        self.close()

    def doWork(self):
        if not self.mapLayerSelection:
            QMessageBox.critical(self, u"Erro", u"Sem camada definida. Selecione uma camada.")
            return
        elif not self.attributeSelection:
            QMessageBox.critical(self, u"Erro", u"Sem atributo definido. Selecione um atributo.")
            return
        newFieldName = self.newAttribute.toPlainText()
        
        if(newFieldName == ''):
            QMessageBox.critical(self, u"Erro", u"O nome do novo atributo não pode estar em branco.")
            return
        
        workingLayer = self.mapLayerSelection.currentLayer()
        fields = workingLayer.fields()
        workingField = self.attributeSelection.currentField()
        
        if(not (fields.field(workingField).typeName() in ('Real', 'integer', 'Integer64'))):
            QMessageBox.critical(self, u"Erro", u"O atributo selecionado não é numérico. Selecione um atributo numérico para a conversão.")
            return
        
        for f in fields:
            if newFieldName == f.name():
                QMessageBox.critical(self, u"Erro", u"Já existe atributo com o nome escolhido. Defina outro nome.")
                return
        
        workingLayer.startEditing()
        newField = QgsField(newFieldName, QtCore.QVariant.Double)
        workingLayer.dataProvider().addAttributes([newField])
        workingLayer.updateFields()
		
        for feat in workingLayer.getFeatures():
            feat.setAttribute(newFieldName, (6400/360) * float(feat[workingField]))
            workingLayer.updateFeature(feat)

        workingLayer.commitChanges()

        QMessageBox.information(self, u"Informação", u"Atributo convertido com sucesso!")
        self.close()
