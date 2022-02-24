# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterVectorLayer,
                       QgsFeatureRequest,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField
                       )
from qgis import processing

class MakeMosaic(QgsProcessingAlgorithm): 

    INPUT_LAYERS = 'INPUT_LAYERS'
    INPUT_FRAME = 'INPUT_FRAME'
    INPUT_SCALE = 'INPUT_SCALE'
    INPUT_NAME_FIELD = 'INPUT_NAME_FIELD'
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
            QgsProcessingParameterBoolean(
                'CHECKBOX_MATCH_LAYERS',
                self.tr('Associar imagem e polígonos automaticamente'),
                defaultValue = True
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                'INPUT_NAME_FIELD',
                self.tr('Selecione o campo que informa o nome da camada correspondente ao poligono.'), 
                type=QgsProcessingParameterField.String, 
                parentLayerParameterName='INPUT_FRAME', 
                allowMultiple=False, 
                optional = True,
                defaultValue='nome')
            )
        
        
        
        self.addParameter(
            QgsProcessingParameterBoolean(
                'CHECKBOX_PCT',
                self.tr('Corrigir paleta, se necessário'),
                defaultValue = True
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Mosaico')
            )
        ) 
        
    def processAlgorithm(self, parameters, context, feedback):      
        feedback.setProgressText('Construindo mosaico...')
        layers = self.parameterAsLayerList(parameters,'INPUT_LAYERS', context)
        inputFrame = self.parameterAsVectorLayer(parameters,'INPUT_FRAME', context)
        nameField = self.parameterAsFields (parameters,'INPUT_NAME_FIELD', context)[0]
        fixPct = self.parameterAsBool(parameters,'CHECKBOX_PCT', context)
        matchLayers = self.parameterAsBool(parameters,'CHECKBOX_MATCH_LAYERS', context)
        frameGrid = inputFrame
        if matchLayers:
            frameLayer = self.matchLayerAndFrame(inputFrame, layers)
            nameField = 'nome'
            frameGrid = frameLayer
        countGrid = frameGrid.featureCount()
        
        listLayerSize = len(layers)
        listSize = listLayerSize*countGrid+1
        progressStep = 100/listSize if listSize else 0
        
        mergeLayers = []
        i=1
        for feat in frameGrid.getFeatures():
            frameGrid.removeSelection()
            for step,pctLayer in enumerate(layers):
                if feedback.isCanceled():
                        return {self.OUTPUT: 'cancelado'}
                rect = pctLayer.extent()
                if (feat[nameField] == pctLayer.name()):
                    frameGrid.select(feat.id())
                    frameSelected = frameGrid.materialize(QgsFeatureRequest().setFilterFids(frameGrid.selectedFeatureIds()))
                    if pctLayer.bandCount()==1 and fixPct:
                        rgbLayer = self.pctToRgb(context, feedback, pctLayer)
                    else:
                        if fixPct and not pctLayer.bandCount()==1:
                            feedback.setProgressText('Corrigir paleta está marcada, mas a imagem ' + pctLayer.name() + ' não tem apenas 1 banda, será considerada como RGB')
                        rgbLayer = pctLayer
                    clippedLayer = self.clipLayer(context, feedback, rgbLayer, frameSelected)
                    mergeLayers.append(clippedLayer)
                    frameGrid.removeSelection()
                feedback.setProgress( ((i-1)*listLayerSize+step+1)  * progressStep )
            i+=1
        merged = self.mergeAll(parameters, context, feedback, mergeLayers)
        return{self.OUTPUT: merged}
    
    def matchLayerAndFrame(self, inputFrame, layers):
        frameLayer = processing.run('DSGToolsOpProvider:matchlayerandframe',
                {
                    'INPUT_LAYERS': layers,
                    'INPUT_FRAME': inputFrame,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                })['OUTPUT']
        return frameLayer
        
    def createFrames(self, context, feedback, inputFrame, inputScale):
        frameGrid = processing.run('dsgtools:createframeswithconstraintalgorithm', 
                {
                    'INPUT': inputFrame,
                    'STOP_SCALE': inputScale,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                },
                context=context,
                feedback=feedback)['OUTPUT']
        return frameGrid
    def pctToRgb(self, context, feedback, inputlayer):
        rgbLayer =processing.run('gdal:pcttorgb', 
                {
                    'INPUT': inputlayer,
                    'BAND': 1,
                    'RGBA': False,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                },
                context=context,
                feedback=feedback)['OUTPUT']
        return rgbLayer
    def clipLayer(self, context, feedback, inputlayer, inputGrid):
        
        clippedLayer = processing.run('gdal:cliprasterbymasklayer', 
                {
                    'INPUT': inputlayer,
                    'ALPHA_BAND': False,
                    'CROP_TO_CUTLINE': True,
                    'DATA_TYPE': 0,
                    'EXTRA': '',
                    'KEEP_RESOLUTION': True,
                    'MASK': inputGrid,
                    'MULTITHREADING': False,
                    'NODATA': None,
                    'OPTIONS': '',
                    'SET_RESOLUTION' : False, 
                    'SOURCE_CRS' : None, 
                    'TARGET_CRS' : None, 
                    'X_RESOLUTION' : None, 
                    'Y_RESOLUTION' : None,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                },
                context=context,
                feedback=feedback)['OUTPUT']
        return clippedLayer
    def mergeAll(self, parameters, context, feedback, mergeLayers):
        rgbLayer =processing.run('gdal:merge', 
                {
                    'INPUT': mergeLayers,
                    'DATA_TYPE': 5,
                    'EXTRA': '',
                    'NODATA_INPUT' : None, 
                    'NODATA_OUTPUT' : None, 
                    'OPTIONS' : '', 
                    'PCT' : False, 
                    'SEPARATE' : False ,
                    'OUTPUT': parameters['OUTPUT']
                },
                context=context,
                feedback=feedback)['OUTPUT']
        return rgbLayer
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return MakeMosaic()

    def name(self):
        return 'mosaic'

    def displayName(self):
        return self.tr('Mosaicar')

    def group(self):
        return self.tr('Vetor e Raster')

    def groupId(self):
        return 'vetoreraster'

    def shortHelpString(self):
        return self.tr("O algoritmo mosaica as camadas selcionadas baseada na moldura, que é responsável por limitar, usando polígonos, a área a ser mosaicada de cada imagem. Pode-se associar a imagem aos polígonos informando o campo da moldura que contém o nome da imagem correspondente ao polígono ou automaticamente, nesse caso será usado o campo 'nome' na moldura, portanto, é necessário que este campo já esteja preenchido com o nome da imagem correspondente. No caso de imagens com paleta pode-se corrigir automaticamente. Atenção: não corrigr paleta automaticamente quando selecionar outras camadas de apenas uma banda sem ser paleta, como imagens de MDS")
    
