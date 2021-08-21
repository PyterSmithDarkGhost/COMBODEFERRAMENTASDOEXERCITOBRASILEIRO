# -*- coding: utf-8 -*-
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsRectangle, QgsMapLayer, QgsWkbTypes, QgsPointXY
from qgis.gui import QgsMapToolEmitPoint, QgsMapToolIdentifyFeature, QgsMapToolIdentify, QgsRubberBand
from qgis.PyQt import uic, QtWidgets, QtCore
from qgis.PyQt.QtWidgets import QFileDialog, QTreeWidgetItem, QHeaderView, QMessageBox
from qgis.PyQt.QtCore import pyqtSignal, Qt
from .interface_dialog import InterfaceDialog
from .find_dialog import FindDialog
import processing, os, requests, tempfile, string, math, csv
from osgeo import gdal
from PIL import Image

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'detMIArea_dockwidget_base.ui'))


class Main(QtWidgets.QDockWidget, FORM_CLASS):

    closingDock = pyqtSignal()

    def __init__(self, iface):
        super(Main, self).__init__()
        '''Constructor'''
        self.setupUi(self)
        self.iface = iface
        self.dialog = InterfaceDialog()
        self.dialogFind = FindDialog()
        self.isOpen = False
        self.openFiles()

    def initGui(self):
        self.initVariables()
        self.initSignals()
        self.openWindow()
        self.isOpen = True

    def openWindow(self):
        self.iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)
        self.isOpen = True

    def closeDock(self, event):
        layers = self.iface.mapCanvas().layers()
        for l in layers:
            if l.type() == QgsMapLayer.VectorLayer:
                l.removeSelection()
        self.closingDock.emit()
        event.accept()
        self.isOpen = False
        self.boxButton.setChecked(False)
        self.geometryButton.setChecked(False)
        self.mapList.clear()

    def initVariables(self):
        self.canvas = self.iface.mapCanvas()
        self.myToolBox = RectangleMapTool(self.canvas)
        self.myToolGeom = GeometryMapTool(self.canvas, self.iface)
        self.currentTool = self.canvas.mapTool()
        self.scaleSelected = 0
        self.webParamDict = {1:[975,1090,6,6], 2:[1600,1600,4,4], 3:[1600,1600,4,4], 4:[1450,1200,5,4]} #[width,height,ncol,nrow]

    def initSignals(self):
        self.closeEvent = self.closeDock
        self.boxButton.clicked.connect(self.getFromBox)
        self.geometryButton.clicked.connect(self.getFromGeometry)
        self.myToolBox.boxCreated.connect(self.findDialog)
        self.myToolGeom.geometrySelected.connect(self.findDialog)
        self.dialogFind.finished.connect(self.doWorkBox)
        self.downloadButton.clicked.connect(self.selectScale)
        self.dialog.finished.connect(self.downloadMaps)
        self.txtButton.clicked.connect(self.exportTxt)
        self.csvButton.clicked.connect(self.exportCsv) 

    def getFromBox(self, state):
        if state:
            self.mapList.clear()
            self.geometryButton.setChecked(False)
            self.clearLayersSelections()
            self.canvas.setMapTool(self.myToolBox)
            self.canvas.scene().addItem(self.myToolBox.rubberBand)
        else:
            self.canvas.unsetMapTool(self.myToolBox)
            self.canvas.scene().removeItem(self.myToolBox.rubberBand)
            self.myToolBox.reset()

    def getFromGeometry(self, state):
        if state:
            self.mapList.clear()
            self.boxButton.setChecked(False)
            self.myToolBox.reset()
            self.canvas.setMapTool(self.myToolGeom)
        else:
            self.canvas.unsetMapTool(self.myToolGeom)
            self.clearLayersSelections()

    def clearLayersSelections(self):
        layers = self.iface.mapCanvas().layers()
        for l in layers:
            if l.type() == QgsMapLayer.VectorLayer:
                l.removeSelection()

    def findDialog(self, geom):
        self.workgeom = geom
        self.dialogFind.exec_()

    def doWorkBox(self, choice):
        self.choice = choice
        if self.choice == 'small':
            multi = 24
        else:
            multi = 1
        if self.workgeom is not None:
            sup_esq = QgsPointXY(self.workgeom.xMinimum(), self.workgeom.yMaximum())
            inf_dir = QgsPointXY(self.workgeom.xMaximum(), self.workgeom.yMinimum())
            if multi == 24:
                carta_SupEsq = self.findChart(sup_esq,25)
                carta_InfDir = self.findChart(inf_dir,25)
            else:
                carta_SupEsq = self.findChart(sup_esq,1)
                carta_InfDir = self.findChart(inf_dir,1)

            self.featuresByScale = {1:{}, 2:{}, 3:{}, 4:{}}
            featDict = {25:1, 50:2, 100:3, 250:4}
            self.chartsByScale = {0: {}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}, 7:{}}
            chartsDict = {1:0, 2:1, 5:2, 10:3, 25:4, 50:5, 100:6, 250:7}
            
            geom_SupEsq = carta_SupEsq[2].center()
            geom_InfDir = carta_InfDir[2].center()
            
            nStepXi = (geom_InfDir.x() - geom_SupEsq.x())/(multi * 0.3125/60)
            nStepYi = (geom_SupEsq.y() - geom_InfDir.y())/(multi * 0.3125/60)
            
            nStepX = int(nStepXi)
            nStepY = int(nStepYi)

            for j in range(nStepY+1):
                idxY = geom_SupEsq.y() - j*(multi * 0.3125/60)
                for i in range(nStepX+1):
                    idxX = geom_SupEsq.x() + i*(multi * 0.3125/60)
                    pt = QgsPointXY(idxX, idxY)
                    if multi == 24:
                        for scale in [25, 50, 100, 250]:
                            chart = self.findChart(pt, scale)
                            self.chartsByScale[chartsDict[scale]][chart[0]] = chart[1]
                            self.featuresByScale[featDict[scale]][chart[0]] = chart[2]
                    else:
                        for scale in [1, 2, 5, 10]:
                            chart = self.findChart(pt, scale)
                            self.chartsByScale[chartsDict[scale]][chart[0]] = chart[1]

            self.fillListBox()
    
    def fillListBox(self):
        self.mapList.clear()
        self.item = []

        self.item.append(QTreeWidgetItem(['1:1.000','']))
        self.item.append(QTreeWidgetItem(['1:2.000','']))
        self.item.append(QTreeWidgetItem(['1:5.000','']))
        self.item.append(QTreeWidgetItem(['1:10.000','']))
        self.item.append(QTreeWidgetItem(['1:25.000','']))
        self.item.append(QTreeWidgetItem(['1:50.000','']))
        self.item.append(QTreeWidgetItem(['1:100.000','']))
        self.item.append(QTreeWidgetItem(['1:250.000','']))

        self.mapList.addTopLevelItems([self.item[0], self.item[1], self.item[2], self.item[3], self.item[4], self.item[5], self.item[6], self.item[7]])  
        
        for listNum in range(8):
            for key in self.chartsByScale[listNum]:
                if self.chartsByScale[listNum][key]:
                    if self.chartsByScale[listNum][key][0] == '-':
                        item_temp = QTreeWidgetItem([key, ''])
                        self.item[listNum].addChild(item_temp)
                    else:
                        item_temp = QTreeWidgetItem([key, self.chartsByScale[listNum][key]])
                        self.item[listNum].addChild(item_temp)
            self.item[listNum].setExpanded(True)
            if self.item[listNum].childCount() == 0:
                self.mapList.invisibleRootItem().removeChild(self.item[listNum])
        
        self.mapList.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def selectScale(self):
        if self.choice == 'small':
            self.dialog.exec_()
        else:
            QMessageBox.warning(self, u"Aviso:", u"Opção apenas disponível para pequenas escalas (até 25.000)")

    def processImages(self, layerWMS, webScaleParamList, outputFolder):
        scaleFeaturesDict = self.featuresByScale[self.scaleSelected]
        width, height, ncol, nrow =  webScaleParamList
        
        for feat in scaleFeaturesDict.keys():
            bboxStr = scaleFeaturesDict[feat].asWktCoordinates().replace(',','').split(' ')
            bbox = []
            for i in bboxStr:
                bbox.append(float(i))
            temp_path = tempfile.TemporaryDirectory()
            complete_image = Image.new('RGB', (width * ncol, height * nrow))
            dx = (bbox[2] - bbox[0]) / ncol
            dy = (bbox[3] - bbox[1]) / nrow

            for column in range(ncol):
                xmin = bbox[0] + dx * column
                xmax = bbox[0] + dx * (column + 1)
                for line in range(nrow):
                    ymin = bbox[3] - dy * (line + 1)
                    ymax = bbox[3] - dy * line
                    imageURL = "https://bdgex.eb.mil.br/mapcache?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&BBOX={},{},{},{}&SRS=EPSG:4326&WIDTH={}&HEIGHT={}&LAYERS={}&STYLES=,,,&FORMAT=image/png&DPI=96&MAP_RESOLUTION=96&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE".format(xmin, ymin, xmax, ymax, width, height, layerWMS)
                    partialImage = requests.get(imageURL, allow_redirects=True)
                    temp_file = os.path.join(temp_path.name, 'temp_image.png')
                    open(temp_file, "wb").write(partialImage.content)
                    complete_image.paste(Image.open(temp_file), (width * column, height * line))
        
            complete_image.save(os.path.join(temp_path.name, 'complete_image.png'))
            outputFile = os.path.join(outputFolder, feat + ".tif")
            
            p1=gdal.GCP(bbox[0], bbox[1], 0, 0, height * nrow)
            p2=gdal.GCP(bbox[2], bbox[1], 0, width * ncol, height * nrow)
            p3=gdal.GCP(bbox[0], bbox[3], 0, 0, 0)
            p4=gdal.GCP(bbox[2], bbox[3], 0, width * ncol, 0)
            
            opt = gdal.TranslateOptions(format = 'GTiff', GCPs = [p1,p2,p3,p4])
            gdal.Translate(outputFile, os.path.join(temp_path.name, 'complete_image.png'), options = opt)
            temp_path.cleanup()
            processing.run("gdal:assignprojection", {'INPUT': outputFile, 'CRS' : "EPSG:4326"})
            
        return

    def downloadMaps(self, scaleSelected, outputFolder, multiScale):
        layersDictWeb = {1:"ctm25" , 2:"ctm50" , 3:"ctm100" , 4:"ctm250"}
        self.scaleSelected = scaleSelected
        if multiScale:
            layerWMS = "ctm250,ctm100,ctm50,ctm25"
        else:
            layerWMS = layersDictWeb[scaleSelected]
        webScaleParamList = self.webParamDict[scaleSelected]
        self.processImages(layerWMS, webScaleParamList, outputFolder)
        return

    def exportTxt(self):
        fileDlg = QFileDialog()
        filePath = fileDlg.getSaveFileName(None, u"Selecionar pasta de saída das imagens", "", u"Arquivo texto (*.txt)")[0]
        if filePath != "" and filePath[-4:].lower() != ".txt":
            filePath += ".txt"
        
        if filePath != "":
            csvFile = open(filePath, 'w')

        if filePath == "":
            return

        csvFile.write(u'*********************************************\n')
        head = u'* Lista de cartas topograficas de interesse *\n'
        csvFile.write(head)
        csvFile.write(u'*********************************************\n\n')
        
        itemCount = self.mapList.invisibleRootItem().childCount()
        scale_list = (u'1:1.000', u'1:2.000', u'1:5.000', u'1:10.000', u'1:25.000', u'1:50.000', u'1:100.000', u'1:250.000')
		
        for i in range(itemCount):
            currentItem = self.mapList.invisibleRootItem().child(i)

            for s in range(8):
                if currentItem.text(0) == scale_list[s]:
                    csvFile.write(scale_list[s]+':\n')
                    csvFile.write(u'---------\n\n')
                    csvFile.write(u'{0:20} | {1:10}\n'.format(u'Nomenclatura', u'MI/MIR'))
                    csvFile.write(u'------------           ------    \n\n')
                
                    if s in range(4):
                        for j in range(currentItem.childCount()):
                            csvFile.write(u'{0:30} | {1:20}\n'.format(currentItem.child(j).text(0), currentItem.child(j).text(1)))
                    else:
                        for j in range(currentItem.childCount()):
                            csvFile.write(u'{0:20} | {1:10}\n'.format(currentItem.child(j).text(0), currentItem.child(j).text(1)))
                    
                    csvFile.write(u'\n')
                    csvFile.write(u'---------------------------------\n\n\n')

        csvFile.close()
    
    def exportCsv(self):
        fileDlg = QFileDialog()
        filePath = fileDlg.getSaveFileName(None, u"Selecionar arquivo de saída", "", u"Arquivo CSV (*.csv)")[0]
        
        if filePath != "" and filePath[-4:].lower() != ".csv":
            filePath += ".csv"
        
        if filePath != "":
            csvFile = open(filePath, 'w')

        if filePath == "":
            return

        csvFile.write(u'Escala;Nomenclatura;MI\n')
        
        itemCount = self.mapList.invisibleRootItem().childCount()
        for i in range(itemCount):
            currentItem = self.mapList.invisibleRootItem().child(i)
            for j in range(currentItem.childCount()):
                csvFile.write(u'{};{};{}\n'.format(currentItem.text(0),currentItem.child(j).text(0), currentItem.child(j).text(1)))
            
        csvFile.close()    

    def openFiles(self):
        filePath = os.path.dirname(os.path.dirname(__file__))
        filePath250 = os.path.join(filePath, "auxiliar", "csv", "MIR250.csv")
        filePath100 = os.path.join(filePath, "auxiliar", "csv", "MI100.csv")
        pathCsvExceptions25k = os.path.join(filePath, "auxiliar", "csv", "exclusionList25k.csv")
        pathCsvExceptions50k = os.path.join(filePath, "auxiliar", "csv", "exclusionList50k.csv")
        with open(filePath250, 'r') as file:
            self.file250 = {x[0]: x[1] for x in csv.reader(file, delimiter=';')}
        with open(filePath100, 'r') as file:
            self.file100 = {x[0]: x[1] for x in csv.reader(file, delimiter=';')}
        with open(pathCsvExceptions25k, 'r') as file:
            self.exceptions25k = [x[0] for x in csv.reader(file)]
        with open(pathCsvExceptions50k, 'r') as file:
            self.exceptions50k = [x[0] for x in csv.reader(file)]
        
    def findChart(self, point, escala):
        alpha = string.ascii_uppercase
        alphabet = {i: alpha[i-1] for i in range(1,len(alpha)+1)}
        self.scaleIndex={
            500 : {
                0: "V",
                1: "X",
                2: "Y",
                3: "Z"
            },
            250 : {
                0: "A",
                1: "B",
                2: "C",
                3: "D"
            },
            100 : {
                0: "I",
                1: "II",
                2: "III",
                3: "IV",
                4: "V",
                5: "VI"
            },
            50 : {
                0: "1",
                1: "2",
                2: "3",
                3: "4"
            },
            25 : {
                0: "NO",
                1: "NE",
                2: "SO",
                3: "SE"
            },
            10 : {
                0: "F",
                1: "D",
                2: "B",
                3: "E",
                4: "C",
                5: "A"
            },
            5 : {
                0: "I",
                1: "II",
                2: "III",
                3: "IV"
            },
            2 : {
                0: "1",
                1: "2",
                2: "3",
                3: "4",
                4: "5",
                5: "6"
            },
            1 : {
                0: "A",
                1: "B",
                2: "C",
                3: "D"
            }
        }
        nomeFolha = ""
        miFolha = ""
        scaleX = 6.0
        scaleY = 4.0
        
        # 1:1.000.000
        hemisferio = 'S' if point.y() < 0 else 'N'
        nomeFolha += hemisferio
        linha = math.floor(abs(point.y()/4)) + 1
        linhaAlpha = alphabet[linha]
        nomeFolha += linhaAlpha
        nomeFolha += '-'
        fuso = 30 + int(point.x()/6)
        nomeFolha += str(fuso)
        
        # 1:500.000 init
        esqFuso = -180 + (fuso-1) * 6
        infFuso = linha * 4

        if hemisferio == 'S':
            infFuso *= -1
        else:
            infFuso -= 4        
        
        for scales in [500, 250, 100, 50, 25, 10, 5, 2, 1]:
            scaleX, scaleY, esqFuso, infFuso, nomeFolha, miFolha = self.scaleFinder(point, scaleX, scaleY, esqFuso, infFuso, scales, nomeFolha, miFolha)
            if escala == scales:
                rect = QgsRectangle(esqFuso, infFuso, esqFuso + scaleX, infFuso + scaleY)
                return (nomeFolha, miFolha, rect) 

    def findMI(self, nome, arq):
        try:
            mi = str(arq[nome])
            return mi
        except:
            return ""

    def miExclusion(self, mi, arq):
        return 

    def scaleFinder(self, point, scaleX, scaleY, esqFuso, infFuso, mapScale, nomeFolha, miFolha):
        if mapScale == 10:
            scaleX, scaleY, esqFuso, infFuso, pos = self.positionFinder23(point, scaleX, scaleY, esqFuso, infFuso)
        elif mapScale in [100, 2]:
            scaleX, scaleY, esqFuso, infFuso, pos = self.positionFinder32(point, scaleX, scaleY, esqFuso, infFuso)
        else:
            scaleX, scaleY, esqFuso, infFuso, pos = self.positionFinder22(point, scaleX, scaleY, esqFuso, infFuso)
        
        nome = self.scaleIndex[mapScale][pos]
        nomeFolha += '-' + nome

        if miFolha:
                miFolha += '-' + nome

        if mapScale == 250:
            miFolha = self.findMI(nomeFolha, self.file250)
        elif mapScale == 100:
            miFolha = self.findMI(nomeFolha, self.file100)    
        elif mapScale == 50:
            if nomeFolha in self.exceptions50k:
                miFolha = ""
        elif mapScale == 25:
            if nomeFolha in self.exceptions25k:
                miFolha = ""
        
        return scaleX, scaleY, esqFuso, infFuso, nomeFolha, miFolha

    def positionFinder22(self, point, scaleX, scaleY, esqFuso, infFuso):
        scaleX /= 2
        scaleY /= 2
        
        if point.x() < esqFuso + scaleX:
            if point.y() > infFuso + scaleY:
                pos = 0
            else:
                pos = 2
        else:
            if point.y() > infFuso + scaleY:
                pos = 1
            else:
                pos = 3

        esqFuso = esqFuso + int(pos%2)*scaleX
        inf = 0 if pos > 1 else 1
        infFuso = infFuso + inf*scaleY

        return scaleX, scaleY, esqFuso, infFuso, pos

    def positionFinder23(self, point, scaleX, scaleY, esqFuso, infFuso):
        scaleX /= 2
        scaleY /= 3
        
        if point.y() < infFuso + scaleY:
            if point.x() > esqFuso + scaleX:
                pos = 0
            else:
                pos = 3
        elif point.y() < infFuso + 2*scaleY:
            if point.x() > esqFuso + scaleX:
                pos = 1
            else:
                pos = 4
        else:
            if point.x() > esqFuso + scaleX:
                pos = 2
            else:
                pos = 5

        esq = 0 if pos > 2 else 1
        esqFuso = esqFuso + esq*scaleX
        infFuso = infFuso + int(pos%3)*scaleY

        return scaleX, scaleY, esqFuso, infFuso, pos

    def positionFinder32(self, point, scaleX, scaleY, esqFuso, infFuso):
        scaleX /= 3
        scaleY /= 2
        
        if point.x() < esqFuso + scaleX:
            if point.y() > infFuso + scaleY:
                pos = 0
            else:
                pos = 3
        elif point.x() < esqFuso + scaleX*2:
            if point.y() > infFuso + scaleY:
                pos = 1
            else:
                pos = 4
        else:
            if point.y() > infFuso + scaleY:
                pos = 2
            else:
                pos = 5

        esqFuso = esqFuso + int(pos%3)*scaleX
        inf = 0 if pos > 2 else 1
        infFuso = infFuso + inf*scaleY

        return scaleX, scaleY, esqFuso, infFuso, pos




class GeometryMapTool(QgsMapToolIdentifyFeature):
    
    geometrySelected = pyqtSignal(QgsRectangle)
    
    def __init__(self, canvas, iface):
        self.canvas = canvas
        self.iface = iface
        QgsMapToolIdentifyFeature.__init__(self,self.canvas)
      
    def canvasReleaseEvent(self, event):
        event.snapPoint()
        found_features = self.identify(event.x(), event.y(), QgsMapToolIdentify.TopDownStopAtFirst, self.VectorLayer)
    
        layers = self.iface.mapCanvas().layers()
        for l in layers:
            if l.type() == QgsMapLayer.VectorLayer:
                l.selectByIds([])

        if len(found_features) > 0:
            feature = found_features[0].mFeature
            layer = found_features[0].mLayer
            layer.selectByIds([feature.id()])
            geometry = feature.geometry()
            transformer = QgsCoordinateTransform(layer.crs(), QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId), QgsProject.instance())
            geometry.transform(transformer)
        else:
            return
        self.geometrySelected.emit(geometry.boundingBox())




class RectangleMapTool(QgsMapToolEmitPoint):
    
    boxCreated = pyqtSignal(QgsRectangle)
    
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes().GeometryType(2))
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setBrushStyle(Qt.Dense6Pattern)
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes().GeometryType(2))

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.boxCreated.emit(r)

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return

        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes().GeometryType(2))
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return

        point1 = QgsPointXY(startPoint.x(), startPoint.y())
        point2 = QgsPointXY(startPoint.x(), endPoint.y())
        point3 = QgsPointXY(endPoint.x(), endPoint.y())
        point4 = QgsPointXY(endPoint.x(), startPoint.y())

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)    # true to update canvas
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None
        self.rubberBand.hide()
		
        srsCrs = self.canvas.mapSettings().destinationCrs()
        dstCrs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        coordinateTransformer = QgsCoordinateTransform(srsCrs, dstCrs, QgsProject.instance())
        rect = coordinateTransformer.transform(QgsRectangle(self.startPoint, self.endPoint))

        return rect
