# -*- coding: utf-8 -*-

# Importar as bibliotecas necessárias:
from abc import ABC, abstractmethod
from typing import List
from dataclasses import MISSING, dataclass
import os
from qgis import processing
from qgis.PyQt.Qt import QVariant
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsVectorFileWriter,QgsProcessingAlgorithm,
                       QgsProcessingParameterMultipleLayers, QgsCoordinateTransformContext,
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterBoolean, QgsFields, QgsField,
                       QgsVectorLayer, QgsFeature, QgsWkbTypes
                       )

class InsertMASACODE(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    KEEP_ATTRIBUTES = 'KEEP_ATTRIBUTES'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def initAlgorithm(self, config = None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT,
                self.tr('Input Layers'),
                QgsProcessing.TypeVectorAnyGeometry
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.KEEP_ATTRIBUTES,
                self.tr('Manter atributos da modelagem original'),
                defaultValue=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Pasta para salvar os arquivos exportados')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):         
        outputFolderPath = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        keepAttributes = self.parameterAsBool(parameters, self.KEEP_ATTRIBUTES, context)
        inputLayers = self.parameterAsLayerList(
            parameters, self.INPUT, context)
        nInputs = len(inputLayers)
        if nInputs == 0:
            return {self.OUTPUT_FOLDER: 'Camadas vazias. Não foi possível converter os dados.'}
        conversion_factory = {
            'VEG_Floresta_A': EDGVClass(
                masacode=10000,
                output_file_name='Forest',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'VEG_Veg_Cultivada_A': EDGVClass(
                masacode=10001,
                output_file_name='Plantation',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'VEG_Brejo_Pantano_A': EDGVClass(
                masacode=10002,
                output_file_name='Swamp',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'LOC_Area_Edificada_A': EDGVClass(
                masacode=10003,
                output_file_name='Urban_Area',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'LOC_Aglomerado_Rural_De_Extensao_Urbana_P': EDGVClass(
                masacode=10003,
                output_file_name='Urban_Point',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Point,
            ),
            'LOC_Aglomerado_Rural_Isolado_P': EDGVClass(
                masacode=10003,
                output_file_name='Urban_Point',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Point,
            ),
            'LOC_Cidade_P': EDGVClass(
                masacode=10003,
                output_file_name='Urban_Point',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Point,
            ),
            'LOC_Vila_P': EDGVClass(
                masacode=10003,
                output_file_name='Urban_Point',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Point,
            ),
            'HID_Massa_Dagua_A': EDGVClass(
                masacode=10004,
                output_file_name='Water',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'HID_Trecho_Massa_Dagua_A': EDGVClass(
                masacode=10004,
                output_file_name='Water',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'HID_Trecho_Drenagem_L': TrechoDrenagem(
                output_file_name='River',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.LineString,
            ),
            'REL_Terreno_Exposto_A': TerrenoExposto(
                output_file_name='Sand',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'REL_Elemento_Fisiografico_Natural_A': ElementoFisiograficoNatural(
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.Polygon,
            ),
            'TRA_Trecho_Rodoviario_L': TrechoRodoviario(
                output_file_name='Road',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.LineString,
            ),
            'TRA_Arruamento_L': EDGVClass(
                masacode=20004,
                output_file_name='Road',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.LineString,
            ),
            'TRA_Ponte_L': EDGVClass(
                masacode=20005,
                output_file_name='Bridge',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.LineString,
            ),
            'TRA_TUNEL_L': EDGVClass(
                masacode=20007,
                output_file_name='Tunnel',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.LineString,
            ),
            'TRA_Trecho_Ferroviario_L': EDGVClass(
                masacode=20006,
                output_file_name='Railroad',
                output_file_path=outputFolderPath,
                keep_input_attributes=keepAttributes,
                output_geom_type=QgsWkbTypes.LineString,
            ),
        }
        stepSize = 100/nInputs
        for current, layer in enumerate(inputLayers):
            if feedback.isCanceled():
                break
            if layer.name() not in conversion_factory:
                continue
            if layer.featureCount() == 0:
                continue
            fixedLyr = processing.run(
                "native:dropmzvalues",
                {
                    'INPUT':layer,
                    'DROP_M_VALUES':True,
                    'DROP_Z_VALUES':True,
                    'OUTPUT':'TEMPORARY_OUTPUT'
                }
            )['OUTPUT']
            fixedLyr = processing.run(
                "native:multiparttosingleparts",
                {
                    'INPUT': fixedLyr,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
            )['OUTPUT']
            conversion_factory[layer.name()].convertFeatures(
                fixedLyr, fixedLyr.getFeatures()
            )
            
            feedback.setProgress(current * stepSize)
        
        return {self.OUTPUT_FOLDER: 'Conversão concluída'}

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

@dataclass
class AbstractEDGVClass(ABC):
    output_file_path: str
    keep_input_attributes: bool
    output_geom_type: int
    output_file_name: str = MISSING
    masacode: int = MISSING

    
    @abstractmethod
    def get_masacode(self, feature):
        pass
    
    def __post_init__(self):
        self.output_file = self.get_output_file()
    
    def get_output_file(self):
        return os.path.join(self.output_file_path, self.output_file_name+'.shp')

    def get_output_fields(self, input_layer):
        fields = QgsFields()
        fields.append(QgsField('MASACODE', QVariant.Int))
        if not self.keep_input_attributes:
            return fields
        for field in input_layer.fields():
            fields.append(field)
        return fields

    def create_output_file_writer(self, output_fields, output_file, srs):
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.actionOnExistingFile = QgsVectorFileWriter.AppendToLayerAddFields if os.path.exists(
            output_file) else QgsVectorFileWriter.CreateOrOverwriteFile
        vectorFileWriter = QgsVectorFileWriter.create(
            output_file,
            output_fields,
            self.output_geom_type,
            srs,
            QgsCoordinateTransformContext(),
            options
        )
        return vectorFileWriter
    
    def convertFeature(self, feature: QgsFeature, output_fields) -> QgsFeature:
        masacode = self.get_masacode(feature)
        if masacode is None:
            return None
        newFeat = QgsFeature(output_fields)
        newFeat.setGeometry(feature.geometry())
        newFeat['MASACODE'] = masacode
        if not self.keep_input_attributes:
            return newFeat
        for field in feature.fields():
            field_name = field.name()
            if field_name not in self.output_field_names:
                continue
            newFeat[field_name] = feature[field_name]
        return newFeat
    
    def convertFeatures(self, input_layer, featureList: List[QgsFeature]) -> bool:
        output_fields = self.get_output_fields(input_layer)
        self.output_field_names = [field.name()
                                   for field in output_fields]
        output_file_writer = self.create_output_file_writer(
            output_fields=output_fields,
            output_file=self.output_file,
            srs=input_layer.crs(),
        )
        convertLambda = lambda x: self.convertFeature(x, output_fields)
        out = output_file_writer.addFeatures(
            list(filter(lambda x: x is not None, map(convertLambda, featureList)))
        )
        del output_file_writer

@dataclass
class EDGVClass(AbstractEDGVClass):
    def get_masacode(self, feature):
        return self.masacode

@dataclass
class TrechoDrenagem(AbstractEDGVClass):
    masacode: int = 0
    def __post_init__(self):
        super().__post_init__()
        self.conversion_map = {
            'Permanente': 21002,
            'Temporário': 21003,
        }
        self.default_value = 21002
    def get_masacode(self, feature):
        if 'regime' not in feature:
            return None
        return self.conversion_map.get(feature['regime'], self.default_value)

@dataclass
class TrechoRodoviario(AbstractEDGVClass):
    masacode: int = 0

    def get_masacode(self, feature):
        tipoTrechoRodField = [
            field.name() for field in feature.fields() \
                if field.name().lower() == 'tipotrechorod'
        ]
        if len(tipoTrechoRodField) == 0:
            return None
        tipoTrechoRodField = tipoTrechoRodField[0]
        jurisdicaoField = [
            field.name() for field in feature.fields()
            if field.name().lower() == 'jurisdicao'
        ]
        if len(jurisdicaoField) == 0:
            return None
        jurisdicaoField = jurisdicaoField[0]
        if feature[tipoTrechoRodField] == 'Rodovia' and feature[jurisdicaoField] == 'Desconhecida':
            return 20002
        elif feature[tipoTrechoRodField] == 'Rodovia' and feature[jurisdicaoField] in ('Federal', 'Estadual'):
            return 20003
        else:
            return 20001


@dataclass
class TerrenoExposto(AbstractEDGVClass):
    masacode: int = 0

    def get_masacode(self, feature):
        tipoTerrExpField = [
            field.name() for field in feature.fields()
            if field.name().lower() == 'tipoterrex'
        ]
        if len(tipoTerrExpField) == 0:
            return None
        tipoTerrExpField = tipoTerrExpField[0]
        if feature[tipoTerrExpField] == 'Areia':
            return 10005
        return None


@dataclass
class ElementoFisiograficoNatural(AbstractEDGVClass):
    masacode: int = 0
    output_file_name: str = ''

    def get_masacode(self, feature):
        tipoElemNatField = [
            field.name() for field in feature.fields()
            if field.name().lower() == 'tipoelemnat'
        ]
        if len(tipoElemNatField) == 0:
            return None
        tipoElemNatField = tipoElemNatField[0]
        if feature[tipoElemNatField] == 'Montanha':
            return 10007
        elif feature[tipoElemNatField] == 'Escarpa':
            return 21000
        return None


    def convertFeatures(self, input_layer, featureList: List[QgsFeature]) -> bool:
        output_fields = self.get_output_fields(input_layer)
        self.output_field_names = [field.name()
                                for field in output_fields]
        outputFileWriterDict = {
            10007: self.create_output_file_writer(
                input_layer,
                output_fields,
                output_file=os.path.join(self.output_file_path, 'Mountain.shp'),
                srs=input_layer.crs(),
            ),
            21000: self.create_output_file_writer(
                input_layer,
                output_fields,
                output_file=os.path.join(self.output_file_path, 'Cliff.shp'),
                srs=input_layer.crs(),
            ),

        }
        def convertLambda(x): return self.convertFeature(x, output_fields)
        for feat in map(convertLambda, featureList):
            if feat is None:
                continue
            outputFileWriterDict[feat['MASACODE']].addFeature(feat)
        for code, writer in outputFileWriterDict.items():
            del writer
        return True
