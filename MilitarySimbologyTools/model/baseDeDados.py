#! -*- coding: UTF-8 -*-
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtSql import QSqlDatabase
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsProject, QgsProjectBadLayerHandler
from qgis.utils import iface
import os, re
from osgeo import ogr, gdal

class BaseDeDados(QObject):
    def __init__(self):
        super(BaseDeDados, self).__init__()
        self.initVariables()

    def initVariables(self):
        self.listName = {
                    'tropa_a': u'Tropa aliada',
                    'tropa_i': u'Tropa inimiga', 
                    'limite_entre_fracoes_esquerdo': u'Limite entre frações - texto esquerdo',
                    'limite_entre_fracoes_direito': u'Limite entre frações - texto direito',
                    'linha_de_controle': u'Linha de controle',
                    'eixo_de_direcao': u'Eixo de direcao',
                    'armamento_a': u'Armamento aliado',
                    'armamento_i': u'Armamento inimigo',
                    'instalacao_orgao_a': u'Instalação ou órgão aliado', 
                    'instalacao_orgao_i': u'Instalação ou órgão inimigo', 
                    'nucleo_defesa': u'Núcleo de defesa',
                    'objetivo': u'Objetivo',
                    'ponto_coordenacao': u'Ponto de coordenação',
                    'posto_observacao_a': u'Posto de observação aliado',  
                    'posto_observacao_i': u'Posto de observação inimigo',
                    'seta_situacao': u'Seta de situação',
                    'area_coordenacao': u'Área de coordenação',
                    'fortificacoes': u'Fortificações', 
                    #'fortificacoes_ot': u'Fortificações - Trabahos de OT',
                    'fortificacoes_pf': u'Fortificações - Pontos Fortes',
                    #'obstaculos': u'Obstáculos',
                    #'redes': u'Redes',
                    #'fumaca': u'Fumaça',
                    #'minas': u'Minas',
                    #'campos_minados': u'Campos Minados',
                    #'barreiras': u'Barreiras',
                    'localizacao_comando_a': u'Localização de comando aliada',
                    'localizacao_comando_i': u'Localização de comando inimiga',
                    #'comunicacoes' : u'Comunicações',
                    'concentracao_explosao' : u'Alvos',
                    'ativ_isoladas': u'Atividades Isoladas',
                    'coord_ap_fogo': u'Coordenação de Apoio de Fogo',
                    'veiculos': u'Veículos'
                   }
        self.grupos = {
           '1_calco_operacoes': {
               'nome': u'CALCO DE OPERAÇÕES',
               'classes': ['tropa_a', 'posto_observacao_a','armamento_a','limite_entre_fracoes_esquerdo','limite_entre_fracoes_direito', 'linha_de_controle', 'eixo_de_direcao', 'nucleo_defesa',
                            'objetivo', 'ponto_coordenacao', 'medida_restritiva', 'area_coordenacao','seta_situacao','ativ_isoladas','veiculos']
           },
           '3_calco_logistica': {
               'nome': u'CALCO DE APOIO LOGÍSTICO',
               'classes': [ 'instalacao_orgao_a', 'localizacao_comando_a']
           },
           '2_calco_fogos': {
               'nome': u'CALCO DE ALVOS DO PAF',
               'classes': ['coord_ap_fogo', 'concentracao_explosao']
           }, 
           '4_plano_barreiras': {
               'nome': u'PLANO DE BARREIRAS',
               'classes': ['fortificacoes','fortificacoes_ot','fortificacoes_pf','obstaculos','redes','fumaca','minas','campos_minados','barreiras']
           },		   
           '5_calco_comu': {
               'nome': u'CALCO DE COMUNICAÇÕES - DIAGRAMA DO SISTEMA MULTICANAL',
               'classes': ['comunicacoes']
           }
        }
        self.Database = None

    def checkTableFromDatabase(self, tablename):
        allTables = [l.GetName() for l in ogr.Open(self.Database)]
        if tablename in allTables:
            layer = QgsVectorLayer(self.Database + "|layername=" + tablename, '', 'ogr')
            attrList = []
            for i in layer.getFeatures():
                attrList.append(i[0])
        else:
            attrList = ['table not available']
        return attrList

    def setCurrentDatabase(self, pathDatabase):
        pathDatabase.replace('\\','/')
        self.Database =  pathDatabase

    def getDataBaseLayerName(self):
        listOfNames = [l.GetName() for l in ogr.Open(self.Database)]
        return listOfNames

    def getTemplateDatabase(self):
        path  = os.path.join(os.path.dirname(__file__), 'templates', 'dataBase.gpkg')
        return path

    def createDataBase(self, path):
        f = open(self.getTemplateDatabase(),'rb')
        g = open(path,'wb')
        x = f.readline()
        while x:
            g.write(x)
            x = f.readline()
        g.close()

    def loadDatabase(self):
        projects = self.checkTableFromDatabase('qgis_projects')
        if projects[0] == 'table not available':
            return self.loadSymbLayers()
        else:
            return self.loadProject()

    def loadSymbLayers(self):
        fileNameFull = self.Database
        fileName = fileNameFull.split('/')[-1].split('.')[0]
        root = QgsProject.instance().layerTreeRoot()
        self.groupMain = root.insertGroup(0, fileName)
        symbolGroupA = self.groupMain.insertGroup(0, 'CALCO DE SITUACÃO DAS TROPAS ALIADAS')
        symbolGroupE = self.groupMain.insertGroup(1, 'CALCO DE SITUACÃO DO INIMIGO')
        symbolGroupO = self.groupMain.insertGroup(2, 'OUTRAS CAMADAS')
        subSimbol = {}
        for key, value in self.grupos.items() :
            subSimbol[key] = symbolGroupA.insertGroup(0, value['nome'])
        for name in self.getDataBaseLayerName():
            if name == 'limite_entre_fracoes':
                workname = ['limite_entre_fracoes_esquerdo','limite_entre_fracoes_direito']
            else:
                workname = [name]
            for i in workname:
                if i in self.listName:
                    layer = QgsVectorLayer(self.Database + "|layername=" + name, self.listName[i], 'ogr')
                    QgsProject.instance().addMapLayer(layer, False)
                    if i == 'limite_entre_fracoes_esquerdo':
                        for labels in layer.labeling().rootRule().children():
                            if 'direita' in labels.description():
                                labels.setActive(False)
                    elif i == 'limite_entre_fracoes_direito':
                        for labels in layer.labeling().rootRule().children():
                            if 'esquerda' in labels.description():
                                labels.setActive(False)
                    if i[-2:] == '_i':
                        symbolGroupE.addLayer(layer)
                    else:
                        for key, value in self.grupos.items() :
                            if i in value['classes']:
                                subSimbol[key].addLayer(layer)
                elif i not in ['metadata', 'layer_styles']:
                    layer = QgsVectorLayer(self.Database + "|layername=" + i, i, 'ogr')
                    QgsProject.instance().addMapLayer(layer, False)
                    symbolGroupO.addLayer(layer)
        self.loadRasterLayers()
        self.groupMain.removeChildrenGroupWithoutLayers()
        iface.mapCanvas().refresh()
        return 1

    def loadRasterLayers(self):
        symbolGroupR = self.groupMain.insertGroup(3, 'CAMADAS RASTER')
        raster_info=gdal.Info(self.Database)
        if not not raster_info:
            raster_layers = re.findall("GPKG:.*", raster_info)
            if not raster_layers:
                raster_layers = re.findall("IDENTIFIER=.*", raster_info)
                raster_layer = raster_layers[0].replace('IDENTIFIER=','')
                layer = QgsRasterLayer("GPKG:" + self.Database + ":" + raster_layer, raster_layer, 'gdal')
                QgsProject.instance().addMapLayer(layer, False)
                symbolGroupR.addLayer(layer)
            else:
                for raster in raster_layers:
                    layer = QgsRasterLayer(raster, raster[raster.rfind(':')+1:], 'gdal')
                    QgsProject.instance().addMapLayer(layer, False)
                    symbolGroupR.addLayer(layer)

    def loadProject(self):
        file_path = self.Database.replace('\\','/')
        gpkgname=file_path.split('/')[-1]

        projectList = self.checkTableFromDatabase('qgis_projects')
        projectName = projectList[0]

        tempProject=QgsProject.instance()
        tempProject.setBadLayerHandler(QgsProjectBadLayerHandler())
        tempProject.read('geopackage:' + file_path + '?projectName=' + projectName)

        layersList=QgsProject.instance().mapLayers()
        for i in layersList:
            layer = QgsProject.instance().mapLayer(i)
            layerPath = layer.dataProvider().dataSourceUri()
            if gpkgname in layerPath:
                if layer.providerType() == 'gdal':
                    if layerPath.endswith('.gpkg'):
                        newPath = file_path
                    else:
                        newPath = layerPath.replace(layerPath[:layerPath.rfind(':')], 'GPKG:' + file_path)
                else:
                    newPath = layerPath.replace(layerPath[:layerPath.find('|')],file_path)
                layer.dataProvider().setDataSourceUri(newPath)
                layer.setDataSource(newPath, layer.name(), layer.providerType(), layer.dataProvider().ProviderOptions())

        QgsProject.instance().write('geopackage:' + file_path + '?projectName=' + projectName)
        return 2
