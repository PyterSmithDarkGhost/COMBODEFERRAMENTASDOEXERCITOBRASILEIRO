# -*- coding: utf-8 -*-
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import pyqtSlot
from qgis.core import QgsField, QgsMapLayerProxyModel, QgsVectorLayer, QgsGeometry, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject, QgsRectangle, QgsPointXY, QgsWkbTypes
from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtWidgets import QMessageBox
import os


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'window.ui'))


class VirtualFieldGenerator(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, iface):
        super(VirtualFieldGenerator, self).__init__()
        '''Constructor'''
        self.setupUi(self)
        self.iface = iface
        self.checkBoxSelected.hide()
        self.populateLayers()
        QgsProject.instance().layersAdded.connect(self.populateLayers)
        QgsProject.instance().layersRemoved.connect(self.populateLayers)
        self.okButton.pressed.connect(self.doWork)
        self.cancelButton.pressed.connect(self.cancel)
        self.checkBoxCoord.stateChanged.connect(self.setCoordEdit)
        self.checkBoxSelected.stateChanged.connect(self.setDialog)

    def cancel(self):
        self.close()

    def populateLayers(self):
        self.mapLayerSelection.clear()
        self.mapLayerSelection.addItem('Selecione uma camada')
        layers = self.iface.mapCanvas().layers()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) and layer.featureCount() > 0:
                myfilepath= layer.dataProvider().dataSourceUri()
                (Directory, nameFile) = os.path.split(myfilepath)
                self.mapLayerSelection.addItem(nameFile + '\\' + layer.name())

    def getLayer(self):
        currentLayerName = self.mapLayerSelection.currentText()
        layers = self.iface.mapCanvas().layers()
        for layer in layers:
            myfilepath= layer.dataProvider().dataSourceUri()
            (Directory, nameFile) = os.path.split(myfilepath)
            if (nameFile + '\\' + layer.name()) == currentLayerName:
                return layer
        return None

    @pyqtSlot(int)
    def on_mapLayerSelection_currentIndexChanged(self):
        if self.mapLayerSelection.currentIndex() == 0:
            return
        currentLayer = self.getLayer()
        if not currentLayer:
            return
        self.setDialog()

    def setDialog(self):
        self.workLayer = self.getLayer()
        workCrs = self.workLayer.crs()

        #Unchecking boxes
        self.checkList1 = []
        self.checkList2 = []
        self.checkList3 = []

        for c in self.zoneFrame1.children():
            self.checkList1.append(c) if type(c) == QtWidgets.QCheckBox else ''
        for c in self.zoneFrame2.children():
            self.checkList2.append(c) if type(c) == QtWidgets.QCheckBox else ''
        for c in self.zoneFrame3.children():
            self.checkList3.append(c) if type(c) == QtWidgets.QCheckBox else ''

        for c in self.checkList1:
            c.setChecked(False)
        for c in self.checkList2:
            c.setChecked(False)
        for c in self.checkList3:
            c.setChecked(False)
        self.checkBoxArea.setChecked(False)
        self.checkBoxPer.setChecked(False)
        self.checkBoxLeng.setChecked(False)

        if self.checkBoxSelected.isChecked():
            workFeatures = self.workLayer.selectedFeatures()
            if not workFeatures:
                QMessageBox.critical(self, u"Erro", u"Nenhuma feição selecionada. Selecione ao menos uma feição.")
                return
        else:
            itrFeature = self.workLayer.getFeatures()
            workFeatures = list(itrFeature)

        #Defining layer type
        if self.workLayer.geometryType() == 0:
            self.fieldsFrame.hide()
        elif self.workLayer.geometryType() == 1:
            self.fieldsFrame.show()
            self.checkBoxPer.hide()
            self.checkBoxArea.hide()
            self.checkBoxLeng.show()
            self.checkBoxLeng.setChecked(True)
        elif self.workLayer.geometryType() == 2:
            self.fieldsFrame.show()
            self.checkBoxPer.show()
            self.checkBoxPer.setChecked(True)
            self.checkBoxArea.show()
            self.checkBoxArea.setChecked(True)
            self.checkBoxLeng.hide()

        utm = self.UTMcheck(workFeatures, workCrs)
        zones = utm[0]
        #Displaying found zones and checking according boxes
        self.zoneLabel.setText(utm[1])

        for c in self.checkList1:
            c.setChecked(True) if c.text() in zones else ''
        for c in self.checkList2:
            c.setChecked(True) if c.text() in zones else ''
        for c in self.checkList3:
            c.setChecked(True) if c.text() in zones else ''

    def UTMcheck(self, workFeatures, workCrs):
        #Opening UTM Zones layer and finding intersections
        filePathZones = self.pathGpkg()
        zonesLayer = filePathZones + "|layername=Brasil_Fusos"
        zonesMap = QgsVectorLayer(zonesLayer, "zones", "ogr")

        zonesList = zonesMap.getFeatures()
        zones = []
        found = 'Seus dados estão nos seguintes fusos: '

        geoFeatures = []
        transformer = QgsCoordinateTransform(workCrs, QgsCoordinateReferenceSystem(4674, QgsCoordinateReferenceSystem.EpsgCrsId), QgsProject.instance())

        for i in range(len(workFeatures)):
            geoFeatures.append(workFeatures[i].geometry())
            geoFeatures[i].transform(transformer)

        featuresBbox=QgsGeometry().collectGeometry(geoFeatures).boundingBox()
        bboxStr = str(featuresBbox).replace(',','').replace('>','').replace('((','').replace('))','').split()
        if bboxStr[3]==bboxStr[1] and bboxStr[4]==bboxStr[2]:
            roundedBbox = QgsGeometry.fromPointXY(QgsPointXY(round(float(bboxStr[3]),5), round(float(bboxStr[4]),5)))
        else:
            extentMax = QgsPointXY(round(float(bboxStr[3]),5), round(float(bboxStr[4]),5))
            extentMin = QgsPointXY(round(float(bboxStr[1]),5), round(float(bboxStr[2]),5))
            roundedBbox = QgsGeometry.fromRect(QgsRectangle(extentMin, extentMax))
        
        lineLen = len(found)
        lineLen0 = len(found)
        for i in zonesList:
            if roundedBbox.intersects(i.geometry()) and not roundedBbox.touches(i.geometry()):
                found = found + str(i[3]) + ', '
                lineLen = lineLen + 5
                zones.append(i[3])
            if lineLen > 70:
                found += '\n'
                lineLen = 0

        if len(found) == lineLen0:
            found = 'Seus dados não estão projetados.'
        else:
            found = found[:-2]
            found = found + '.'
        return zones, found

    def setCoordEdit(self):
        if self.checkBoxCoord.isChecked():
            self.zoneFrame1.setEnabled(True)
            self.zoneFrame2.setEnabled(True)
            self.zoneFrame3.setEnabled(True)
            self.checkBoxSelected.show()
        else:
            self.zoneFrame1.setEnabled(False)
            self.zoneFrame2.setEnabled(False)
            self.zoneFrame3.setEnabled(False)
            self.checkBoxSelected.hide()

    def doWork(self):
        self.count = 0

        if not self.mapLayerSelection or self.mapLayerSelection.currentText() == 'Selecione uma camada':
            QMessageBox.critical(self, u"Erro", u"Sem camada vetorial definida. Selecione uma camada.")
            return

        self.zonesChecked = []
        for c in self.checkList1:
            self.zonesChecked.append(c.text()) if c.isChecked() else ''
        for c in self.checkList2:
            self.zonesChecked.append(c.text()) if c.isChecked() else ''
        for c in self.checkList3:
            self.zonesChecked.append(c.text()) if c.isChecked() else ''

        if self.checkBoxPer.isChecked():
            self.createPerimeter(self.workLayer)
        if self.checkBoxLeng.isChecked():
            self.createLength(self.workLayer)
        if self.checkBoxArea.isChecked():
            self.createArea(self.workLayer)
        if self.checkBoxCentlayerCrs.isChecked():
            if self.workLayer.geometryType() == 0:
                self.createXY(self.workLayer)
            else:
                self.createCentroidXY(self.workLayer)
        if self.checkBoxCentlatLong.isChecked():
            if self.workLayer.geometryType() == 0:
                self.createLatLong(self.workLayer)
            else:
                self.createCentroidLatLong(self.workLayer)
        if self.zonesChecked:
            self.createUTM(self.workLayer)

        if self.count > 0:
            QMessageBox.information(self, u"Informação", u"<p><p align='center'>{} atributos gerados com sucesso!<br><br>Os atributos gerados sao temporários.<br><br>Para gravar os dados gerados, salve a camada em um novo arquivo.</p>".format(self.count))
        else:
            QMessageBox.warning(self, u"Aviso", u"Nenhum atributo selecionado/gerado.")

        self.close()

    def createArea(self, layer):
        layer.addExpressionField('format_number($area,6)', QgsField(u'Área', QtCore.QVariant.Double))
        self.count += 1

    def createPerimeter(self, layer):
        layer.addExpressionField('format_number($perimeter,3)', QgsField(u'Perímetro', QtCore.QVariant.Double))
        self.count += 1

    def createCentroidXY(self, layer):
        layer.addExpressionField('format_number(x(centroid( $geometry)),10)', QgsField(u'Centroide_X_CAMADA', QtCore.QVariant.String))
        layer.addExpressionField('format_number(y(centroid( $geometry)),10)', QgsField(u'Centroide_Y_CAMADA', QtCore.QVariant.String))
        self.count += 2

    def createCentroidLatLong(self, layer):
        geomX = u"to_real(replace(format_number(x(transform(centroid($geometry), layer_property('{}','crs'), 'EPSG:4674')),5),',','.'))".format(layer.name())
        geomY = u"to_real(replace(format_number(y(transform(centroid($geometry), layer_property('{}','crs'), 'EPSG:4674')),5),',','.'))".format(layer.name())
        expressionX_neg = u"concat(ceil({0}),'º ', floor((abs({0})-floor(abs({0})))*60),''' ',".format(geomX)
        expressionX_neg += u"format_number((((abs({0})-floor(abs({0})))*60)-floor((abs({0})-floor(abs({0})))*60))*60,2),'\"')".format(geomX)
        expressionY_neg = u"concat(ceil({0}),'º ', floor((abs({0})-floor(abs({0})))*60),''' ',".format(geomY)
        expressionY_neg += u"format_number((((abs({0})-floor(abs({0})))*60)-floor((abs({0})-floor(abs({0})))*60))*60,2),'\"')".format(geomY)
        
        expressionX_pos = expressionX_neg.replace('concat(ceil', 'concat(floor')
        expressionY_pos = expressionY_neg.replace('concat(ceil', 'concat(floor')

        exprX_ok = 'case when {} < 0 then {} else {} end'.format(geomX, expressionX_neg, expressionX_pos)
        exprY_ok = 'case when {} < 0 then {} else {} end'.format(geomY, expressionY_neg, expressionY_pos)

        layer.addExpressionField(exprY_ok, QgsField(u'Centroide_Lat', QtCore.QVariant.String))
        layer.addExpressionField(exprX_ok, QgsField(u'Centroide_Long', QtCore.QVariant.String))
        self.count += 2
    
    def createXY(self, layer):
        layer.addExpressionField('format_number($x,3)', QgsField(u'X_CAMADA', QtCore.QVariant.String))
        layer.addExpressionField('format_number($y,3)', QgsField(u'Y_CAMADA', QtCore.QVariant.String))
        self.count += 1

    def createLatLong(self, layer):
        geomX = u"to_real(replace(format_number(x(transform($geometry, layer_property('{}','crs'), 'EPSG:4674')),5),',','.'))".format(layer.name())
        geomY = u"to_real(replace(format_number(y(transform($geometry, layer_property('{}','crs'), 'EPSG:4674')),5),',','.'))".format(layer.name())
        expressionX_neg = u"concat(ceil({0}),'º ', floor((abs({0})-floor(abs({0})))*60),''' ',".format(geomX)
        expressionX_neg += u"format_number((((abs({0})-floor(abs({0})))*60)-floor((abs({0})-floor(abs({0})))*60))*60,2),'\"')".format(geomX)
        expressionY_neg = u"concat(ceil({0}),'º ', floor((abs({0})-floor(abs({0})))*60),''' ',".format(geomY)
        expressionY_neg += u"format_number((((abs({0})-floor(abs({0})))*60)-floor((abs({0})-floor(abs({0})))*60))*60,2),'\"')".format(geomY)
        
        expressionX_pos = expressionX_neg.replace('concat(ceil', 'concat(floor')
        expressionY_pos = expressionY_neg.replace('concat(ceil', 'concat(floor')

        exprX_ok = 'case when {} < 0 then {} else {} end'.format(geomX, expressionX_neg, expressionX_pos)
        exprY_ok = 'case when {} < 0 then {} else {} end'.format(geomY, expressionY_neg, expressionY_pos)

        layer.addExpressionField(exprY_ok, QgsField(u'Lat', QtCore.QVariant.String))
        layer.addExpressionField(exprX_ok, QgsField(u'Long', QtCore.QVariant.String))
        self.count += 2
        
    def createLength(self, layer):
        layer.addExpressionField('format_number($length, 3)', QgsField(u'Comprimento', QtCore.QVariant.Double))
        self.count += 1

    def createUTM(self, layer):
        zoneDict = { \
            '18 S':31978,\
            '19 S':31979,\
            '20 S':31980,\
            '21 S':31981,\
            '22 S':31982,\
            '23 S':31983,\
            '24 S':31984,\
            '25 S':31985,\
            '26 S':5396,\
            '19 N':31973,\
            '20 N':31974,\
            '21 N':31975,\
            '22 N':31976,\
            '23 N':6210 \
        }
        
        for zone in self.zonesChecked:
            xFieldName = u"X_{}".format(zone)
            yFieldName = u"Y_{}".format(zone)
            if self.workLayer.geometryType() == 0:
                layer.addExpressionField(u"format_number(x(transform($geometry, layer_property('{}', 'crs'), 'EPSG:{}')), 3)".format(layer.name(), zoneDict[zone]), QgsField(xFieldName, QtCore.QVariant.String))
                layer.addExpressionField(u"format_number(y(transform($geometry, layer_property('{}', 'crs'), 'EPSG:{}')), 3)".format(layer.name(), zoneDict[zone]), QgsField(yFieldName, QtCore.QVariant.String))
            else:
                layer.addExpressionField(u"format_number(x(transform(centroid($geometry), layer_property('{}', 'crs'), 'EPSG:{}')), 3)".format(layer.name(), zoneDict[zone]), QgsField(xFieldName, QtCore.QVariant.String))
                layer.addExpressionField(u"format_number(y(transform(centroid($geometry), layer_property('{}', 'crs'), 'EPSG:{}')), 3)".format(layer.name(), zoneDict[zone]), QgsField(yFieldName, QtCore.QVariant.String))
            self.count += 2

    def pathGpkg(self):
        filePath = os.path.dirname(os.path.dirname(__file__))
        filePathGpkg = os.path.join(filePath, "auxiliar", "shp", "Brasil_Fusos.gpkg")
        return filePathGpkg