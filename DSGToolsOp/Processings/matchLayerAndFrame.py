# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterMultipleLayers,
                       QgsFeatureSink,
                       QgsProcessingParameterVectorLayer,
                       QgsFeature,
                       QgsGeometry,
                       QgsFields,
                       QgsField,
                       QgsProcessingParameterFeatureSink
                       )

class MatchLayerAndFrame(QgsProcessingAlgorithm): 

    INPUT_LAYERS = 'INPUT_LAYERS'
    INPUT_FRAME = 'INPUT_FRAME'
    INPUT_SCALE = 'INPUT_SCALE'
    INPUT_SRC = 'INPUT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                'INPUT_LAYERS',
                self.tr('Selecionar camadas'),
                QgsProcessing.TypeRaster,
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'INPUT_FRAME',
                self.tr('Moldura'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Associado')
            )
        ) 
        
    def processAlgorithm(self, parameters, context, feedback):      
        feedback.setProgressText('Associando...')
        layers = self.parameterAsLayerList(parameters,'INPUT_LAYERS', context)
        input_frame = self.parameterAsVectorLayer(parameters,'INPUT_FRAME', context)
        input_frame_features = self.createFeaturesArray(input_frame)
        
        listSize = len(input_frame_features)
        progressStep = 100/listSize if listSize else 0
        step = 0
        
        setCRS = input_frame.crs()
        frame_layer_pairs = []
        for step,feat in enumerate(input_frame_features):
            inter_over_poly_list = []
            inter_over_image_list =[]
            for j,pct_layer in enumerate(layers):
                if feedback.isCanceled():
                        return {self.OUTPUT: 'cancelado'}
                rect = QgsGeometry().fromRect(pct_layer.extent())
                intersec = feat.geometry().intersection(rect)
                inter_area = intersec.area()
                feat_area = feat.geometry().area()
                image_area = rect.area()
                inter_over_poly = inter_area/feat_area
                inter_over_poly_list.append(inter_over_poly)
                inter_over_image = inter_area/image_area
                inter_over_image_list.append(inter_over_image)
            image_index = self.selectImageIndex(inter_over_poly_list, inter_over_image_list)
            frame_layer_pairs.append([feat.geometry(), layers[image_index].name()])
            feedback.setProgress( step * progressStep )
        newLayer = self.outLayer(parameters, context, frame_layer_pairs, setCRS)
        return{self.OUTPUT: newLayer}
    def selectImageIndex(self, inter_over_poly_list, inter_over_image_list):
        max_iop_value = max(inter_over_poly_list)
        iop_indices = [index for index, value in enumerate(inter_over_poly_list) if value == max_iop_value]
        selected = iop_indices[0]
        if len(iop_indices)>1:
            for index in iop_indices:
                if inter_over_image_list[index]>inter_over_image_list[selected]:
                    selected=index
        return selected
            
        
    def createFeaturesArray(self, original_layer):
        array_features = []
        features = original_layer.getFeatures()
        for feature in features:
            array_features.append(feature)
        return array_features
    
    def outLayer(self, parameters, context, frame_layer_pairs, setCRS):
        newField = QgsFields()
        newField.append(QgsField('id', QVariant.Int))
        newField.append(QgsField('nome', QVariant.String))
        

        (sink, newLayer) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            newField,
            3, #polygon in QgsWkbTypes
            setCRS
        )

        idcounter = 1
        for pair in frame_layer_pairs:
            frame = pair[0]
            layer = pair[1]
            newFeat = QgsFeature()
            newFeat.setGeometry(frame)
            newFeat.setFields(newField)
            newFeat['id'] = idcounter
            newFeat['nome'] = layer
            sink.addFeature(newFeat, QgsFeatureSink.FastInsert)
            idcounter +=1
        return newLayer
        
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return MatchLayerAndFrame()

    def name(self):
        return 'matchlayerandframe'

    def displayName(self):
        return self.tr('Associar Frame a Imagem')

    def group(self):
        return self.tr('Vetor e Raster')

    def groupId(self):
        return 'vetoreraster'

    def shortHelpString(self):
        return self.tr("O algoritmo atribui um SRC definido pelo usuario a camadas cujo SRC nao estava definido")
    
