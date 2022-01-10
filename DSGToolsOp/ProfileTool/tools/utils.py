# -*- coding: utf-8 -*-

import qgis
from qgis.PyQt import QtCore

def isProfilable(layer):
    if int(QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
        if int(qgis.utils.QGis.QGIS_VERSION.split('.')[0]) == 2 and int(qgis.utils.QGis.QGIS_VERSION.split('.')[1]) < 18 :
            return    (layer.type() == layer.RasterLayer) or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'crayfish_viewer') or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'selafin_viewer') 
        elif int(qgis.utils.QGis.QGIS_VERSION.split('.')[0]) == 2 and int(qgis.utils.QGis.QGIS_VERSION.split('.')[1]) >= 18 :
            return    (layer.type() == layer.RasterLayer) or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'crayfish_viewer') or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'selafin_viewer') or \
                    (layer.type() == layer.VectorLayer and layer.geometryType() == qgis.core.QGis.Point)
    elif int(QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
        return    (layer.type() == layer.RasterLayer) or \
                (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'crayfish_viewer') or \
                (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'selafin_viewer') or \
                (layer.type() == layer.VectorLayer and layer.geometryType() ==  qgis.core.QgsWkbTypes.PointGeometry   )

