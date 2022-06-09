# -*- coding: utf-8 -*-

# Importar as bibliotecas necessárias:
import os
from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsVectorFileWriter,QgsProcessingAlgorithm,
                       QgsProcessingParameterMultipleLayers, QgsCoordinateTransformContext,
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingParameterFolderDestination
                       )

class InsertMASACODE(QgsProcessingAlgorithm):
    INPUT_LINES = 'INPUT_LINES'
    INPUT_AREAS = 'INPUT_AREAS'
    INPUT_POINTS = 'INPUT_POINTS'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def initAlgorithm(self, config = None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_POINTS,
                self.tr('Selecione as camadas vetoriais do tipo ponto para inserir o MASACODE:'),
                layerType=QgsProcessing.TypeVectorPoint,
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_LINES,
                self.tr('Selecione as camadas vetoriais do tipo linha para inserir o MASACODE:'),
                layerType=QgsProcessing.TypeVectorLine,
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_AREAS,
                self.tr('Selecione as camadas vetoriais do tipo área para inserir o MASACODE:'),
                layerType=QgsProcessing.TypeVectorPolygon,
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Pasta para salvar os arquivos exportados:')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        converter = {'VEG_Floresta_A' : 10000, 'VEG_Veg_Cultivada_A' : 10001, 
                    'VEG_Brejo_Pantano_A' : 10002, 'LOC_Area_Edificada_A' : 10003, 
                    'LOC_Aglomerado_Rural_De_Extensao_Urbana_P' : 10003, 'LOC_Aglomerado_Rural_Isolado_P' : 10003, 
                    'LOC_Cidade_P' : 10003, 'LOC_Vila_P' : 10003, 'HID_Massa_Dagua_A' : 10004, 
                    'HID_Trecho_Massa_Dagua_A' : 10004, 'TRA_Trecho_Rodoviario_L' : 20003, 'TRA_Arruamento_L' : 20004, 
                    'TRA_Ponte_L' : 20005, 'TRA_Trecho_Ferroviario_L' : 20006, 'HID_Trecho_Drenagem_L' : 21002}
        converter_nome = {'VEG_Floresta_A' : 'Forest', 'VEG_Veg_Cultivada_A' : 'Plantation', 
                        'VEG_Brejo_Pantano_A' : 'Swamp',
                        'LOC_Area_Edificada_A' : 'Urban_Area', 'LOC_Aglomerado_Rural_De_Extensao_Urbana_P' : 'Urban_Point', 
                        'LOC_Aglomerado_Rural_Isolado_P' : 'Urban_Point', 'LOC_Cidade_P' : 'Urban_Point', 
                        'LOC_Vila_P' : 'Urban_Point', 'HID_Massa_Dagua_A' : 'Water', 'HID_Trecho_Massa_Dagua_A' : 'Water', 
                        'TRA_Trecho_Rodoviario_L' : 'Road', 'TRA_Arruamento_L' : 'Road', 'TRA_Ponte_L' : 'Bridge', 
                        'TRA_Trecho_Ferroviario_L' : 'Railroad', 'HID_Trecho_Drenagem_L' : 'River'}            
        outputFolderPath = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        linesInput = self.parameterAsLayerList(parameters, self.INPUT_LINES, context)
        areasInput = self.parameterAsLayerList(parameters, self.INPUT_AREAS, context)
        pointsInput = self.parameterAsLayerList(parameters, self.INPUT_POINTS, context)
        lines = []
        areas = []
        points = []
        merge_road = []
        merge_loc = []
        merge_water = []
        numPoint = 0
        numLine = 0
        numPoly = 0
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        for j in range(len(linesInput)):
            auxLineLayer = self.runAddCount(linesInput[j], feedback = feedback)
            self.runCreateSpatialIndex(auxLineLayer, feedback = feedback)
            auxLineLayer.setName(linesInput[j].name())
            lines.append(auxLineLayer)
        for j in range(len(areasInput)):
            auxAreaLayer = self.runAddCount(areasInput[j], feedback = feedback)
            self.runCreateSpatialIndex(auxAreaLayer, feedback = feedback)
            auxAreaLayer.setName(areasInput[j].name())
            areas.append(auxAreaLayer)
        for j in range(len(pointsInput)):
            auxPointLayer = self.runAddCount(pointsInput[j], feedback = feedback)
            self.runCreateSpatialIndex(auxPointLayer, feedback = feedback)
            auxPointLayer.setName(pointsInput[j].name())
            points.append(auxPointLayer)

        for j in range(len(lines)):
            name = str(lines[j].name())
            if name in converter_nome:
                if name == 'TRA_Trecho_Rodoviario_L':
                    features = lines[j].getFeatures()
                    lines[j].startEditing()
                    layer_provider = lines[j].dataProvider()
                    for f in features:
                        id = f.id()
                        if f[2] == 'Rodovia' and f[3] == 'Desconhecida':
                            attrs = {(len(lines[j].fields().names())-1) : 20002}
                            layer_provider.changeAttributeValues({id : attrs})
                        elif f[2] == 'Rodovia' and (f[3] == 'Federal' or f[3] == 'Estadual'):
                            attrs = {(len(lines[j].fields().names())-1) : 20001}
                            layer_provider.changeAttributeValues({id : attrs})
                        elif f[2] == 'Caminho carroçável':
                            attrs = {(len(lines[j].fields().names())-1) : 20003}
                            layer_provider.changeAttributeValues({id : attrs})
                        else:
                            attrs = {(len(lines[j].fields().names())-1) : converter[name]}
                            layer_provider.changeAttributeValues({id : attrs})
                    attrsdelete = []
                    for k in range((len(lines[j].fields().names())-1)):
                        attrsdelete.append(k)
                    layer_provider.deleteAttributes(list(attrsdelete))
                    lines[j].commitChanges()
                elif name == 'HID_Trecho_Drenagem_L':
                    features = lines[j].getFeatures()
                    lines[j].startEditing()
                    layer_provider = lines[j].dataProvider()
                    for f in features:
                        id = f.id()
                        if f[8] == 'Permanente':
                            attrs = {(len(lines[j].fields().names())-1) : 21002}
                            layer_provider.changeAttributeValues({id : attrs})
                        elif f[8] == 'Temporário':
                            attrs = {(len(lines[j].fields().names())-1) : 21003}
                            layer_provider.changeAttributeValues({id : attrs})
                        else: 
                            attrs = {(len(lines[j].fields().names())-1) : 21001}
                            layer_provider.changeAttributeValues({id : attrs})
                    attrsdelete = []
                    for k in range((len(lines[j].fields().names())-1)):
                        attrsdelete.append(k)
                    layer_provider.deleteAttributes(list(attrsdelete))
                    lines[j].commitChanges()
                else:
                    features = lines[j].getFeatures()
                    lines[j].startEditing()
                    layer_provider = lines[j].dataProvider()
                    for f in features:
                        id = f.id()
                        attrs = {(len(lines[j].fields().names())-1) : converter[name]}
                        layer_provider.changeAttributeValues({id : attrs})
                    attrsdelete = []    
                    for k in range((len(lines[j].fields().names())-1)):
                        attrsdelete.append(k)
                    layer_provider.deleteAttributes(list(attrsdelete))
                    lines[j].commitChanges()

                if name == 'TRA_Trecho_Rodoviario_L' or name == 'TRA_Arruamento_L':
                    merge_road.append(lines[j])

                outputFilePath = os.path.join(outputFolderPath, converter_nome[name])
                QgsVectorFileWriter.writeAsVectorFormatV2(lines[j], outputFilePath, QgsCoordinateTransformContext(), options)
                numLine += 1
            else:
                continue    
        if len(merge_road) != 0:
            mergeado_road = self.mergeVector(list(merge_road), feedback)
            mergeado_road.startEditing()
            mergeado_road.dataProvider().deleteAttributes([1, 2])
            mergeado_road.updateFields()
            mergeado_road.commitChanges()
            outputFilePath = os.path.join(outputFolderPath, 'Road')
            QgsVectorFileWriter.writeAsVectorFormatV2(mergeado_road, outputFilePath, QgsCoordinateTransformContext(), options)
            numLine += 1
        
        for j in range(len(areas)):
            name = str(areas[j].name())
            if name in converter_nome:
                features = areas[j].getFeatures()
                areas[j].startEditing()
                layer_provider = areas[j].dataProvider()
                for f in features:
                    id = f.id()
                    attrs = {(len(areas[j].fields().names())-1) : converter[name]}
                    layer_provider.changeAttributeValues({id : attrs})
                attrsdelete = []
                for k in range((len(areas[j].fields().names())-1)):
                    attrsdelete.append(k)
                layer_provider.deleteAttributes(list(attrsdelete))
                areas[j].commitChanges()

                if name == 'HID_Massa_Dagua_A' or name == 'HID_Trecho_Massa_Dagua_A':
                    merge_water.append(areas[j])

                outputFilePath = os.path.join(outputFolderPath, converter_nome[name])
                QgsVectorFileWriter.writeAsVectorFormatV2(areas[j], outputFilePath, QgsCoordinateTransformContext(), options)
                numPoly += 1
            else:
                continue

        if len(merge_water) != 0:
            mergeado_water = self.mergeVector(list(merge_water), feedback)
            mergeado_water.startEditing()
            mergeado_water.dataProvider().deleteAttributes([1, 2])
            mergeado_water.updateFields()
            mergeado_water.commitChanges()
            outputFilePath = os.path.join(outputFolderPath, 'Water')
            QgsVectorFileWriter.writeAsVectorFormatV2(mergeado_water, outputFilePath, QgsCoordinateTransformContext(), options)
            numPoly += 1
        
        for j in range(len(points)):
            name = str(points[j].name())
            if name in converter_nome:
                features = points[j].getFeatures()
                points[j].startEditing()
                layer_provider = points[j].dataProvider()
                for f in features:
                    id = f.id()
                    attrs = {(len(points[j].fields().names())-1) : converter[name]}
                    layer_provider.changeAttributeValues({id : attrs})
                attrsdelete = []
                for k in range((len(points[j].fields().names())-1)):
                    attrsdelete.append(k)
                attrsdelete.pop(0)
                layer_provider.deleteAttributes(list(attrsdelete))
                points[j].commitChanges()

                if name == 'LOC_Aglomerado_Rural_De_Extensao_Urbana_P' or name == 'LOC_Aglomerado_Rural_Isolado_P' or name == 'LOC_Cidade_P' or name == 'LOC_Vila_P':
                    merge_loc.append(points[j])

                outputFilePath = os.path.join(outputFolderPath, converter_nome[name])
                QgsVectorFileWriter.writeAsVectorFormatV2(points[j], outputFilePath, QgsCoordinateTransformContext(), options)
                numPoint += 1
            else:
                continue

        if len(merge_loc) != 0:
            mergeado_loc = self.mergeVector(list(merge_loc), feedback)
            mergeado_loc.startEditing()
            mergeado_loc.dataProvider().deleteAttributes([2, 3])
            mergeado_loc.updateFields()
            mergeado_loc.commitChanges()
            outputFilePath = os.path.join(outputFolderPath, 'Urban_Point')
            QgsVectorFileWriter.writeAsVectorFormatV2(mergeado_loc, outputFilePath, QgsCoordinateTransformContext(), options)   
            numPoint += 1

        returnMessage = f'{numPoint} camadas pontos, {numLine} camadas linhas, {numPoly} camadas polígonos, total = {numPoint+numLine+numPoly} camadas geradas em {outputFolderPath}'
        return {self.OUTPUT_FOLDER: returnMessage} 

    def runAddCount(self, inputLyr, feedback):
        output = processing.run(
            "native:addautoincrementalfield",
            {
                'INPUT': inputLyr,
                'FIELD_NAME':'MASACODE',
                'START': 0,
                'GROUP_FIELDS': [],
                'SORT_EXPRESSION': '',
                'SORT_ASCENDING': False,
                'SORT_NULLS_FIRST': False,
                'OUTPUT': 'memory:'
            },
            feedback = feedback
        )
        return output['OUTPUT']

    def runCreateSpatialIndex(self, inputLyr, feedback):
        processing.run(
            "native:createspatialindex",
            {'INPUT': inputLyr},
            feedback = feedback
        )

    def mergeVector(self, inputLyr, feedback):
        output = processing.run(
            "native:mergevectorlayers", 
            {
                'LAYERS': inputLyr, 
                'CRS': QgsProcessingFeatureSourceDefinition(),
                'OUTPUT': 'memory:'
            },
            feedback = feedback
        )
        return output['OUTPUT']

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return InsertMASACODE()

    def name(self):
        return 'insertMASACODE'

    def displayName(self):
        return self.tr('Inserir MASACODE')

    def group(self):
        return self.tr('Missoes')

    def groupId(self):
        return 'missoes'

    def shortHelpString(self):
        return self.tr("InsertMASACODE")