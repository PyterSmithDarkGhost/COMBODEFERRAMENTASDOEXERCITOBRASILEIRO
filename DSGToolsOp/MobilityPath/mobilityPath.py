# -*- coding: UTF-8 -*-
import os, processing
from qgis.PyQt import QtGui, uic, QtCore, QtWidgets
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox, QDialog, QFileDialog, QTableWidgetItem
from qgis.core import QgsProject, QgsMapLayerProxyModel, QgsVectorLayer, QgsRasterLayer, QgsGeometry, QgsFeature, QgsField, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
from operator import itemgetter

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'window.ui'))

class MobilityPath(QDialog, FORM_CLASS):
    def __init__(self, iface):
        super(MobilityPath, self).__init__()
        self.iface = iface
        self.setupUi(self)
        self.populateLayers()
        QgsProject.instance().layersAdded.connect(self.populateLayers)
        QgsProject.instance().layersRemoved.connect(self.populateLayers)
        self.layerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.okButton.pressed.connect(self.resolveInputs)
        self.cancelButton.pressed.connect(self.cancel)
        self.tableWidget.cellChanged.connect(self.rowsCheck)
        self.saveToFileButton.pressed.connect(self.exportCsv)
        self.readFromFileButton.pressed.connect(self.readCsv)

    def cancel(self):
        self.close()

    def rowsCheck(self, currentRow, currentColumn):
        if self.tableWidget.rowCount() == (currentRow + 1):
            try:
                self.tableWidget.item(currentRow, 0).text() != ""
                col1 = True
            except AttributeError:
                col1 = False
            try:
                self.tableWidget.item(currentRow, 1).text() != ""
                col2 = True
            except AttributeError:
                col2 = False
            try:
                self.tableWidget.item(currentRow, 2).text() != ""
                col3 = True
            except AttributeError:
                col3 = False
            if col1 and col2 and col3:
                self.tableWidget.setRowCount(self.tableWidget.rowCount())
                self.tableWidget.insertRow(self.tableWidget.rowCount())
        return

    def resolveInputs(self):
        if not self.layerCombo.currentLayer():
            QMessageBox.critical(self, u"Erro", u"Nenhuma camada raster selecionada. Selecione uma camada.")
            return

        temp_layer = QgsVectorLayer("Point", "Dados de Classe", "memory")
        dtprovider = temp_layer.dataProvider()
        dtprovider.addAttributes([QgsField("Deslocamento", QVariant.String),
        QgsField("Minimo", QVariant.Double),
        QgsField("Maximo", QVariant.Double),
		QgsField("Valor", QVariant.Int)])
        temp_layer.updateFields()
        temp_list = []
        for i in range(self.tableWidget.rowCount()-1):
            if self.tableWidget.item(i, 0).text() == self.tableWidget.item(i, 1).text() ==  self.tableWidget.item(i, 2).text() == '':
                continue
            means = self.tableWidget.item(i, 0).text()
            min = self.conv_gms_dec(self.tableWidget.item(i, 1).text())
            max = self.conv_gms_dec(self.tableWidget.item(i, 2).text())
            if min == 'Fail' or max == 'Fail':
                return
            temp_list.append((means,min,max))

        feature_list = sorted(temp_list, key=itemgetter(2))
        j = 1
        for i in feature_list:
            temp_feature = QgsFeature()
            temp_feature.setAttributes([i[0], i[1], i[2], j])
            dtprovider.addFeatures([temp_feature])
            j += 1
        self.doWork(temp_layer)
        self.close()

    def conv_gms_dec(self, basecoord):
        try:
            if basecoord.rfind(".") == -1:
                basecoord += "."
            if basecoord.rfind("'") == -1 and len(basecoord[0:basecoord.rfind(".")]) < 4:
                conv_exp_str = float(basecoord)
            elif basecoord.rfind("'") == -1 and len(basecoord[0:basecoord.rfind(".")]) > 4 and (len(basecoord[0:basecoord.rfind(".")]) < 8 and basecoord.rfind("-") != -1):
                xdeg = float(basecoord[0:basecoord.rfind(".")-4])
                xmin = float(basecoord[basecoord.rfind(".")-4:basecoord.rfind(".")-2])
                xseg = float(basecoord[basecoord.rfind(".")-2:])
                conv_exp_str = float(str(copysign((abs(xdeg) + xmin/60 + xseg/3600),xdeg)))
            elif basecoord.rfind("'") != -1:
                xdeg = float(basecoord[0:basecoord.rfind("º")])
                xmin = float(basecoord[basecoord.rfind("º")+1:basecoord.rfind("'")])
                xseg = float(basecoord[basecoord.rfind("'")+1:basecoord.rfind("\"")])
                conv_exp_str = float(str(copysign((abs(xdeg) + xmin/60 + xseg/3600),xdeg)))
            return conv_exp_str
        except:
                QMessageBox.critical(self, u"Erro", u"Colunas 'Declividade Mínima' e 'Declividade Máxima' devem conter valor em um dos formatos especificados")
                return 'Fail'

    def exportCsv(self):
        fileDlg = QFileDialog()
        filePath = fileDlg.getSaveFileName(None, u"Selecionar arquivo de saída", "", u"Arquivo CSV (*.csv)")[0]
        
        if filePath != "" and filePath[-4:].lower() != ".csv":
            filePath += ".csv"
        if filePath != "":
            csvFile = open(filePath, 'w')
        if filePath == "":
            return

        csvFile.write(u'Deslocamento;Min;Max\n')
        itemCount = self.tableWidget.rowCount() - 1
        for i in range(itemCount):
            csvFile.write(u'{};{};{}\n'.format(self.tableWidget.item(i, 0).text(), self.tableWidget.item(i, 1).text(), self.tableWidget.item(i, 2).text()))    
        csvFile.close()   

    def readCsv(self):
        fileDlg = QFileDialog()
        filePath = fileDlg.getOpenFileName(None, u"Selecionar arquivo CSV", "", u"Arquivo CSV (*.csv)")[0]
        lineIdx = self.tableWidget.rowCount() - 1
        if filePath:
            csvFile = open(filePath, "r")
            for l in csvFile:
                line = l.rstrip().replace('\n','').split(";")
                if line[0] == 'Deslocamento':
                    continue
                self.tableWidget.setItem(lineIdx, 0, QTableWidgetItem(line[0]))
                self.tableWidget.setItem(lineIdx, 1, QTableWidgetItem(line[1]))
                self.tableWidget.setItem(lineIdx, 2, QTableWidgetItem(line[2]))
                lineIdx += 1
            csvFile.close()

    def doWork(self, tableLayer):
        workLayer = self.layerCombo.currentLayer()
        cutGeom = QgsGeometry().fromRect(workLayer.extent())
        cutLayer = QgsVectorLayer("Polygon?crs={}".format(workLayer.crs().authid()), "temp_cut", "memory")
        cut_feature = QgsFeature()
        cut_feature.setGeometry(cutGeom)
        cutLayer.dataProvider().addFeatures([cut_feature])
        restLayers = self.getLayers()

        if restLayers:
            for layer in restLayers:
                cutLayer = processing.run("native:difference", {'INPUT': cutLayer,
                'OVERLAY': layer,
                'OUTPUT': 'memory:'})['OUTPUT']	
				
            cutted_raster_path = processing.run("gdal:cliprasterbymasklayer", {'INPUT': workLayer,
            'MASK' : cutLayer,
            'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
			
            cutted_raster = QgsRasterLayer(cutted_raster_path)
        else:
            cutted_raster = workLayer

        slopeLayer_path = processing.run("gdal:slope", {'INPUT': cutted_raster,
        'BAND': 1,
        'SCALE': 1,
        'AS_PERCENT': False,
        'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        slopeLayer = QgsRasterLayer(slopeLayer_path)

        classLayer_path = processing.run("native:reclassifybylayer", {'INPUT_RASTER': slopeLayer,
        'RASTER_BAND': 1,
        'INPUT_TABLE': tableLayer,
        'MIN_FIELD': 'Minimo',
        'MAX_FIELD': 'Maximo',
        'VALUE_FIELD': 'Valor',
        'RANGE_BOUNDARIES': 1,
        'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']

        classLayer = QgsRasterLayer(classLayer_path)
        classLayer.setName('Mapa de trafegabilidade')
        QgsProject.instance().addMapLayer(classLayer)
        self.setRasterStyle(classLayer, tableLayer)

        return

    def setRasterStyle(self, raster_layer, layer_values):
        shaderType = QgsColorRampShader()
        shaderType.setColorRampType(QgsColorRampShader.Discrete)
        item_list = []
        j = 1
        for i in list(layer_values.getFeatures()):
            color_temp = QColor(0, 0, 0)
            color_temp.setHsvF(j/layer_values.featureCount(), 1, 1)
            item_list.append(QgsColorRampShader.ColorRampItem(i[3], color_temp, lbl = str(i[0])))
            j += 1
        shaderType.setColorRampItemList(item_list)
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(shaderType)
        renderer = QgsSingleBandPseudoColorRenderer(raster_layer.dataProvider(), 1, shader)
        raster_layer.setRenderer(renderer)

    def populateLayers(self):
        self.restLayerComboBox.clear()
        layers = self.iface.mapCanvas().layers()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) and layer.featureCount() > 0 and layer.geometryType() == 2:
                self.restLayerComboBox.addItem(layer.name())

    def getLayers(self):
        workLayers = []
        checkedLayers = self.restLayerComboBox.checkedItems()
        layers = self.iface.mapCanvas().layers()
        for candLayers in checkedLayers:
            for layer in layers:
                if layer.name() == candLayers:
                    workLayers.append(layer)
        return workLayers
