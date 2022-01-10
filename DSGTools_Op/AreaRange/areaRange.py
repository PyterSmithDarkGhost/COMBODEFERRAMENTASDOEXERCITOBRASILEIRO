# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from math import *
import os
import processing

class AreaRange(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.initVariables()
        self.initSignals()

    def initGui(self):
        iconPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'arearange.png')
        self.enableAction = QAction( QIcon(iconPath), u"Ativar geração de área de alcance de armamento", self.iface.mainWindow())
        self.enableAction.setCheckable(True)
        self.toolbar = self.iface.addToolBar(u'Geração de área de alcance de armamento')
        self.toolbar.addAction(self.enableAction)
        self.enableAction.changed.connect(self.maptoolChanged)

    def unload(self):
        self.toolbar.removeAction(self.enableAction)
        del self.toolbar

    def maptoolChanged(self):
        if self.enableAction.isChecked():
            self.canvas.setMapTool(self.myTool)
        else:
            self.canvas.unsetMapTool(self.myTool)

    def initVariables(self):
        self.myTool = QgsMapToolEmitPoint(self.canvas)
        self.currentTool = self.canvas.mapTool()
        self.clickedPoint = ''

    def initSignals(self):
        self.myTool.canvasClicked.connect(self.doWork)

    def getInput(self):
            qid = QInputDialog()
            dist_check = True
            ang_check = True
            ang_op_check = True
            while dist_check:
                inp_dist = QInputDialog.getText(qid, "Digite o alcance", "Alcance (em unidades do mapa): ", QLineEdit.Normal)[0]
                if not inp_dist:
                    return
                try:
                    dist = float(inp_dist.replace(",", "."))
                    dist_check = False
                except:
                    QMessageBox.critical(None , u"Erro", u"Entre um valor numérico para a distância.")
            while ang_check:
                inp_ang = QInputDialog.getText(qid, "Digite o azimute de disparo", "Azimute (GG.MM.SS,SSS, GG.MM.SS ou Decimal): ", QLineEdit.Normal)[0]
                if not inp_ang:
                    return
                if len(inp_ang.split(".")) == 3:
                    try:
                        ang = float(inp_ang.split(".")[0]) + float(inp_ang.split(".")[1])/60 + float(inp_ang.split(".")[2].replace(",", "."))/3600
                        ang_check = False
                    except:
                        QMessageBox.critical(None , u"Erro", u"Entre um formato válido para o azimute.")
                else:
                    try:
                        ang = float(inp_ang.replace(",", "."))
                        ang_check = False
                    except:
                        QMessageBox.critical(None , u"Erro", u"Entre um formato válido para o azimute.")
            while ang_op_check:
                inp_op_ang = QInputDialog.getText(qid, "Digite o ângulo de abertura", "Ângulo de abertura (GG.MM.SS,SSS, GG.MM.SS ou Decimal): ", QLineEdit.Normal)[0]
                if not inp_op_ang:
                    return
                if len(inp_op_ang.split(".")) == 3:
                    try:
                        ang_op = float(inp_op_ang.split(".")[0]) + float(inp_op_ang.split(".")[1])/60 + float(inp_op_ang.split(".")[2].replace(",", "."))/3600
                        ang_op_check = False
                    except:
                        QMessageBox.critical(None , u"Erro", u"Entre um formato válido para o ângulo de abertura.")
                else:
                    try:
                        ang_op = float(inp_op_ang.replace(",", "."))
                        ang_op_check = False
                    except:
                        QMessageBox.critical(None , u"Erro", u"Entre um formato válido para o ângulo de abertura.")
            return dist, ang, ang_op

    def getLayerFeature(self, point):
        if self.canvas.mapSettings().destinationCrs().isGeographic():
            d = 2 * pow(10,-8) * self.canvas.scale()
        else:
            d = 0.002 * self.canvas.scale()
        bufferRect = QgsRectangle(point.x() - d, point.y() - d, point.x() + d, point.y() + d)
        layerlist = self.iface.mapCanvas().layers()
        for layer in layerlist:
            if layer.geometryType() == 0:
                for feature in layer.getFeatures():
                    transf = QgsCoordinateTransform(layer.crs(), self.canvas.mapSettings().destinationCrs(), QgsProject.instance())
                    if feature.geometry().isMultipart():
                        workgeom = feature.geometry().coerceToType(1)[0].asPoint()
                    else:
                        workgeom = feature.geometry().asPoint()
                    geom = QgsPoint(workgeom)
                    geom.transform(transf)
                    geom = QgsGeometry.fromPointXY(QgsPointXY(geom))
                    if geom.intersects(bufferRect):
                        return layer, workgeom
            else:
                continue

    def generateArea(self, point, dist, azimuth, op_angle):
        edge_pt_1 = QgsPointXY(point.x() + dist * (1 / cos(radians(op_angle / 2))) * sin(radians(azimuth + op_angle / 2)), point.y() + dist * (1 / cos(radians(op_angle / 2))) * cos(radians(azimuth + op_angle / 2)))
        edge_pt_2 = QgsPointXY(point.x() + dist * (1 / cos(radians(op_angle / 2))) * sin(radians(azimuth - op_angle / 2)), point.y() + dist * (1 / cos(radians(op_angle / 2))) * cos(radians(azimuth - op_angle / 2)))
        cut_polygon = QgsGeometry.fromWkt( 'Polygon(({} {}, {} {}, {} {}, {} {}))'.format(point.x(), point.y(), edge_pt_1.x(), edge_pt_1.y(),edge_pt_2.x(), edge_pt_2.y(), point.x(), point.y()))
        point = QgsGeometry.fromPointXY(point)
        buffered = point.buffer(dist, 20)
        range_area = buffered.intersection(cut_polygon)
        return range_area

    def doWork(self, point, button):
        if button == QtCore.Qt.LeftButton:
            layerFeat = self.getLayerFeature(point)
            if not layerFeat:
                return
            else:
                worklayer, workgeom = layerFeat
            inputs = self.getInput()
            if not inputs:
                return
            else:
                d, ang, op = inputs
            area_geom = self.generateArea(workgeom, d, ang, op)

            output_layer = QgsVectorLayer("Polygon?crs={}".format(worklayer.crs().authid()), "Alcance do armamento", "memory")
            dtprovider = output_layer.dataProvider()
            QgsProject.instance().addMapLayer(output_layer)
            dtprovider.addAttributes([QgsField("Alcance", QVariant.Double),
            QgsField("Azimute", QVariant.Double),
            QgsField("Abertura", QVariant.Double)])
            output_layer.updateFields()

            output_feature = QgsFeature()
            output_feature.setGeometry(area_geom)
            output_feature.setAttributes([d, ang, op])

            dtprovider.addFeatures([output_feature])
            output_layer.updateExtents()
            QMessageBox.information(None , u"Aviso", u"Ponto criado com\n\nAzimute: {} º\n\nDistância: {}\n\nAbertura: {} º".format(ang, d, op))
            return
        else:
            return
