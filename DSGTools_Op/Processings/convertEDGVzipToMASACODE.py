# -*- coding: utf-8 -*-

# Importar as bibliotecas necessárias:
import glob
import os
import shutil
import zipfile

from qgis import processing
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingUtils)
from qgis.PyQt.QtCore import QCoreApplication


class ConvertBDGExZIPtoMASACODE(QgsProcessingAlgorithm):
    INPUT_FOLDER = 'INPUT_FOLDER'
    KEEP_ATTRIBUTES = 'KEEP_ATTRIBUTES'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def initAlgorithm(self, config = None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_FOLDER,
                self.tr('Pasta com os arquivos no formato zip'),
                behavior=QgsProcessingParameterFile.Folder,
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
        self.outputFolderPath = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        keepAttributes = self.parameterAsBool(parameters, self.KEEP_ATTRIBUTES, context)
        inputFolder = self.parameterAsFile(
            parameters, self.INPUT_FOLDER, context)
        inputFiles = [i for i in glob.glob(f'{inputFolder}/*.zip')]
        nInputs = len(inputFiles)
        if nInputs == 0:
            return {self.OUTPUT_FOLDER: 'Não foi possível localizar os arquivos no formato zip na pasta informada'}
        multiStepFeedback = QgsProcessingMultiStepFeedback(nInputs, feedback)
        for current, file in enumerate(inputFiles):
            if feedback.isCanceled():
                break
            multiStepFeedback.setCurrentStep(current)
            self.tempFolder = QgsProcessingUtils.tempFolder()
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(self.tempFolder)
            zip_ref.close()
            fileList = [i for i in glob.glob(f'{self.tempFolder}/**/*.shp')]
            processing.run(
                "DSGToolsOpProvider:convertedgvtomasacode",
                {
                    "INPUT": fileList,
                    "KEEP_ATTRIBUTES": keepAttributes,
                    "OUTPUT_FOLDER": self.outputFolderPath,
                },
                context=context,
                feedback=multiStepFeedback
            )
        
        return {self.OUTPUT_FOLDER: 'Conversão concluída'}
    
    def postProcessAlgorithm(self, context, feedback):
        if not os.path.exists(self.tempFolder):
            return
        shutil.rmtree(self.tempFolder)

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConvertBDGExZIPtoMASACODE()

    def name(self):
        return 'convertbdgexziptomasacode'

    def displayName(self):
        return self.tr("Converte os zips baixados do BDGEx para o formato MASACODE")

    def group(self):
        return self.tr('Missoes')

    def groupId(self):
        return 'missoes'

    def shortHelpString(self):
        return self.tr('Converte em lote os zips contendo shapefiles no formato EDGV para o formato MASACODE')
