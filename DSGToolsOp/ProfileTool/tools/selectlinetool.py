# -*- coding: utf-8 -*-
import qgis
from qgis.core import *
from qgis.gui import *

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

class SelectLineTool:
    
    def getPointTableFromSelectedLine(self, iface, tool, newPoints, layerindex, previousLayer, pointstoDraw ):
        pointstoDraw = []
        layer = iface.activeLayer()
        if layer == None or layer.type() != QgsMapLayer.VectorLayer:
            QMessageBox.warning( iface.mainWindow(), u"Buscador de Geometria Mais Próxima", u"Nenhuma camada vetorial selecionada." )
            return [pointstoDraw, layerindex, previousLayer]
        if not layer.isSpatial():
            QMessageBox.warning( iface.mainWindow(), u"Buscador de Geometria Mais Próxima", u"A camada selecionada não possui geometrias válidas." )
            return [pointstoDraw, layerindex, previousLayer]
        # get the point coordinates in the layer's CRS
        point = tool.toLayerCoordinates(layer, QgsPointXY(newPoints[0][0],newPoints[0][1]))

        
        if layerindex == None or layer != previousLayer:
            # there's no previously created index or it's not the same layer,
            # then create the index
            layerindex = QgsSpatialIndex()
            f = QgsFeature()
            iter = layer.getFeatures()
            while iter.nextFeature(f):
                layerindex.insertFeature(f)
            # get the feature which has the closest bounding box using the spatial index
        nearest = layerindex.nearestNeighbor( point, 1 )
        featureId = nearest[0] if len(nearest) > 0 else None
        closestFeature = QgsFeature()
        
        f = QgsFeature()
        if featureId == None or layer.getFeatures(QgsFeatureRequest(featureId)).nextFeature(f) == False:
            closestFeature = None
            return [pointstoDraw, None, None]
        
        if layer.geometryType() != qgis.core.QgsWkbTypes.LineGeometry  and closestFeature != None:
            QMessageBox.warning( iface.mainWindow(), u"Buscador de Geometria Mais Próxima", u"Nenhuma camada vetorial linha selecionada." )
            return [pointstoDraw, None, None]

        booltemp = False
        if layer.geometryType() != qgis.core.QgsWkbTypes.PointGeometry :
            booltemp = True
        
        if booltemp and closestFeature != None:
            # find the furthest bounding box borders
            f = QgsFeature()
            closestFeature = layer.getFeatures(QgsFeatureRequest(featureId)).nextFeature(f)
            rect = f.geometry().boundingBox()
            
            dist_pX_rXmax = abs( point.x() - rect.xMaximum() )
            dist_pX_rXmin = abs( point.x() - rect.xMinimum() )
            if dist_pX_rXmax > dist_pX_rXmin:
                width = dist_pX_rXmax
            else:
                width = dist_pX_rXmin

            dist_pY_rYmax = abs( point.y() - rect.yMaximum() )
            dist_pY_rYmin = abs( point.y() - rect.yMinimum() )
            if dist_pY_rYmax > dist_pY_rYmin:
                height = dist_pY_rYmax
            else:
                height = dist_pY_rYmin

            # create the search rectangle
            rect = QgsRectangle()
            rect.setXMinimum( point.x() - width )
            rect.setXMaximum( point.x() + width )
            rect.setYMinimum( point.y() - height )
            rect.setYMaximum( point.y() + height )
            
            # retrieve all geometries into the search rectangle
            
            iter2 = layer.getFeatures(QgsFeatureRequest(rect))
            # find the nearest feature
            minDist = -1
            featureId = None
            point = QgsGeometry.fromPointXY(point)
            f = QgsFeature() 
            while iter2.nextFeature(f):
                geom = f.geometry()
                distance = geom.distance(point)
                if minDist < 0 or distance < minDist:
                    minDist = distance
                    featureId = f.id()
            # get the closest feature
            try:
                closestFeature = layer.getFeatures(QgsFeatureRequest(featureId)).next()
                if featureId == None or layer.getFeatures(QgsFeatureRequest(featureId)).next(f) == False:
                    closestFeature = None
            except:
                f = QgsFeature()
                closestFeature = layer.getFeatures(QgsFeatureRequest(featureId)).nextFeature(f)
                closestFeature = f
                if featureId == None or layer.getFeatures(QgsFeatureRequest(featureId)).nextFeature(f) == False:
                    closestFeature = None
                    
        previousLayer = layer
        iface.mainWindow().statusBar().showMessage("selectline")
        layer.removeSelection()
        
        #closest
        layer.select( closestFeature.id() )
        transf = QgsCoordinateTransform(layer.crs(), iface.mapCanvas().mapSettings().destinationCrs(), QgsProject.instance())
        for point in closestFeature.geometry().vertices():
            point.transform(transf)
            pointstoDraw += [[point.x(),point.y()]]
        return [pointstoDraw, layerindex, previousLayer]
