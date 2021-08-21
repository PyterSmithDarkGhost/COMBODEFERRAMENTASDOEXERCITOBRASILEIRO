# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
import os
from math import *

class AzimuthTool(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.initVariables()
        self.initSignals()

    def initGui(self):
        iconPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'azimuth.png')
        self.enableAction = QAction( QIcon(iconPath), u"Ativar criação de ponto por azimute e distância", self.iface.mainWindow())
        self.enableAction.setCheckable(True)
        self.toolbar = self.iface.addToolBar(u'Criação de ponto por azimute e distância')
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
            while dist_check:
                inp_dist = QInputDialog.getText(qid, "Digite a distância", "Distância (unidades da camada): ", QLineEdit.Normal)[0]
                if not inp_dist:
                    return
                try:
                    dist = float(inp_dist.replace(",", "."))
                    dist_check = False
                except:
                    QMessageBox.critical(None , u"Erro", u"Entre um valor numérico para a distância.")
            while ang_check:
                inp_ang = QInputDialog.getText(qid, "Digite o azimute", "Azimute (GG.MM.SS,SSS, GG.MM.SS ou Decimal): ", QLineEdit.Normal)[0]
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
            return dist, ang

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
                d, ang = inputs
            pt_new = QgsPointXY(workgeom.x() + d * sin(radians(ang)), workgeom.y() + d * cos(radians(ang)))
            feat_new = QgsFeature()
            feat_new.setGeometry(QgsGeometry.fromPointXY(pt_new))
            worklayer.startEditing()
            worklayer.dataProvider().addFeatures([feat_new])
            worklayer.triggerRepaint()
            QMessageBox.information(None , u"Aviso", u"Ponto criado com\n\nAzimute: {} º\n\nDistância: {}".format(ang, d))
            return
        else:
            return
