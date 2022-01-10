# -*- coding: utf-8 -*-

#Qt import
from qgis.PyQt import uic, QtCore, QtGui
try:
    from qgis.PyQt.QtGui import QDockWidget
except:
    from qgis.PyQt.QtWidgets import QDockWidget
    
#qgis import
from qgis.core import *
from qgis.gui import *
#other
import platform
import os
#plugin import
from ..tools.plottingtool import *
from ..tools.tableviewtool import TableViewTool
#from .profiletool import Ui_ProfileTool

uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'profiletool.ui'))
FormClass = uic.loadUiType(uiFilePath)[0]

class PTDockWidget(QDockWidget, FormClass):

    TITLE = "ProfileTool"
    TYPE = None
    
    closed = QtCore.pyqtSignal()
    

    def __init__(self, iface1, profiletoolcore, parent=None):
        QDockWidget.__init__(self, parent)
        self.setupUi(self)
        self.profiletoolcore = profiletoolcore
        self.iface = iface1
        self.layerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        
        #Apperance
        self.location = QtCore.Qt.BottomDockWidgetArea
        minsize = self.minimumSize()
        maxsize = self.maximumSize()
        self.setMinimumSize(minsize)
        self.setMaximumSize(maxsize)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        #init scale widgets
        self.sbMaxVal.setValue(0)
        self.sbMinVal.setValue(0)
        self.sbMaxVal.setEnabled(False)
        self.sbMinVal.setEnabled(False)
        self.connectYSpinbox()
        
        #model
        self.mdl = QStandardItemModel(0, 6)
        self.tableView.setModel(self.mdl)
        self.tableView.setColumnWidth(0, 20)
        self.tableView.setColumnWidth(1, 20)
        
        hh = self.tableView.horizontalHeader()
        hh.setStretchLastSection(True)
        self.tableView.setColumnHidden(5 , True)
        self.mdl.setHorizontalHeaderLabels(["","","Camada","Banda/Campo","Buffer de busca"])
        self.tableViewTool = TableViewTool()
        
        #other
        self.selectionmethod = 0
        self.plotlibrary = None
        self.showcursor = True
        
        #Signals
        self.butSaveAs.clicked.connect(self.saveAs)
        self.tableView.clicked.connect(self._onClick)
        self.mdl.itemChanged.connect(self._onChange)
        #self.pushButton_2.clicked.connect(self.addLayer)
        #self.pushButton.clicked.connect(self.removeLayer)
        self.layerCombo.layerChanged.connect(self.addLayerCombo)
        self.addLayerCombo(self.layerCombo.currentLayer())
        self.comboBox.currentIndexChanged.connect(self.selectionMethod)
        self.tableViewTool.layerAddedOrRemoved.connect(self.refreshPlot)
        self.pushButton_reinitview.clicked.connect(self.reScalePlot)
        
    def selectionMethod(self,item):
    
        self.profiletoolcore.rubberband.reset(self.profiletoolcore.polygon)
        self.profiletoolcore.rubberbandpoint.hide()
    
        if item == 0:
            self.selectionmethod = 0
            self.profiletoolcore.toolrenderer.tool.setCursor(QtCore.Qt.CrossCursor)
        elif item == 1:
            self.selectionmethod = 1
            self.profiletoolcore.toolrenderer.tool.setCursor(QtCore.Qt.PointingHandCursor)
            self.pointstoDraw = []
            self.pointstoCal = []
            
        if self.iface.mapCanvas().mapTool() == self.profiletoolcore.toolrenderer.tool:
            self.iface.mapCanvas().setMapTool(self.profiletoolcore.toolrenderer.tool)
            self.profiletoolcore.toolrenderer.connectTool()
            if self.selectionmethod == 0:
                self.iface.mainWindow().statusBar().showMessage(self.profiletoolcore.toolrenderer.textquit0)
            elif self.selectionmethod == 1:
                self.iface.mainWindow().statusBar().showMessage(self.profiletoolcore.toolrenderer.textquit1)
            
    def changePlotLibrary(self, name):
        self.plotlibrary = name
        self.addPlotWidget(self.plotlibrary)
        
        if self.plotlibrary == 'PyQtGraph':
            self.checkBox_mpl_tracking.setEnabled(True)
            #self.checkBox_showcursor.setEnabled(True)
            self.checkBox_mpl_tracking.setCheckState(2)
            self.profiletoolcore.activateMouseTracking(2)
            self.checkBox_mpl_tracking.stateChanged.connect(self.profiletoolcore.activateMouseTracking) 
    
        else:
            self.checkBox_mpl_tracking.setCheckState(0)
            self.checkBox_mpl_tracking.setEnabled(False)
            
    def addPlotWidget(self, library):
        layout = self.frame_for_plot.layout()
        
        while layout.count():
                        child = layout.takeAt(0)
                        child.widget().deleteLater()
                        
                        
        if library == "PyQtGraph":
            self.stackedWidget.setCurrentIndex(0)
            self.plotWdg = PlottingTool().changePlotWidget("PyQtGraph", self.frame_for_plot)
            layout.addWidget(self.plotWdg)
            self.TYPE = "PyQtGraph"
            self.cbxSaveAs.clear()
            self.cbxSaveAs.addItems(['PNG','SVG'])
             
    def connectYSpinbox(self):
        self.sbMinVal.valueChanged.connect(self.reScalePlot)
        self.sbMaxVal.valueChanged.connect(self.reScalePlot)
        
    def disconnectYSpinbox(self):
        try:
            self.sbMinVal.valueChanged.disconnect(self.reScalePlot)
            self.sbMaxVal.valueChanged.disconnect(self.reScalePlot)
        except:
            pass
            
    def connectPlotRangechanged(self):
        self.plotWdg.getViewBox().sigRangeChanged.connect(self.plotRangechanged)
        
    def disconnectPlotRangechanged(self):
        try:
            self.plotWdg.getViewBox().sigRangeChanged.disconnect(self.plotRangechanged)
        except:
            pass
    
    def plotRangechanged(self, param = None):
        PlottingTool().plotRangechanged(self,  'PyQtGraph' )
            
    def reScalePlot(self, param):
            
        if type(param) == bool:
            PlottingTool().reScalePlot(self, self.profiletoolcore.profiles, 'PyQtGraph' , True)
        
        else:
            
            if self.sbMinVal.value() == self.sbMaxVal.value() == 0:
                pass
            else:
                PlottingTool().reScalePlot(self, self.profiletoolcore.profiles, 'PyQtGraph' )
    
    def showCursor(self,int1):
        #For pyqtgraph mode
        if self.plotlibrary == 'PyQtGraph':
            if int1 == 2 :
                self.showcursor = True
                self.profiletoolcore.doTracking = bool(self.checkBox_mpl_tracking.checkState() )
                self.checkBox_mpl_tracking.setEnabled(True)
                for item in self.plotWdg.allChildItems():
                    if str(type(item)) == "<class 'profiletool.pyqtgraph.graphicsItems.InfiniteLine.InfiniteLine'>":
                        if item.name() == 'cross_vertical':
                            item.show()
                        elif item.name() == 'cross_horizontal':
                            item.show()
                    elif str(type(item)) == "<class 'profiletool.pyqtgraph.graphicsItems.TextItem.TextItem'>":
                        if item.textItem.toPlainText()[0] == 'X':
                            item.show()
                        elif item.textItem.toPlainText()[0] == 'Y':
                            item.show()
            elif int1 == 0 :
                self.showcursor = False
                self.profiletoolcore.doTracking = False
                self.checkBox_mpl_tracking.setEnabled(False)
                self.profiletoolcore.rubberbandpoint.hide()
                
                for item in self.plotWdg.allChildItems():
                    if str(type(item)) == "<class 'profiletool.pyqtgraph.graphicsItems.InfiniteLine.InfiniteLine'>":
                        if item.name() == 'cross_vertical':
                            item.hide()
                        elif item.name() == 'cross_horizontal':
                            item.hide()
                    elif str(type(item)) == "<class 'profiletool.pyqtgraph.graphicsItems.TextItem.TextItem'>":
                        if item.textItem.toPlainText()[0] == 'X':
                            item.hide()
                        elif item.textItem.toPlainText()[0] == 'Y':
                            item.hide()
            
         
    def addLayer(self, layer1 = None):
        
        if isinstance(layer1,bool):
            layer1 = self.iface.activeLayer()
        self.tableViewTool.addLayer(self.iface, self.mdl, layer1)
        layer1.dataChanged.connect(self.refreshPlot)
        
    def addLayerCombo(self, l):
        self.tableViewTool.removeLayer(self.mdl, 0)
        if l is not None:
            self.tableViewTool.addLayer(self.iface, self.mdl, l)
            l.dataChanged.connect(self.refreshPlot)
        
    def removeLayer(self, index=None):
        if isinstance(index,bool):
            index = self.tableViewTool.chooseLayerForRemoval(self.iface, self.mdl)

        if index is not None:
            layer = self.mdl.index(index, 4).data()
            try:
                layer.dataChanged.disconnect(self.refreshPlot)
            except:
                pass
            self.tableViewTool.removeLayer(self.mdl, index)
        
    def refreshPlot(self):
                
        if len(self.profiletoolcore.toolrenderer.lastFreeHandPoints) > 1:
            self.profiletoolcore.calculateProfil(self.profiletoolcore.toolrenderer.lastFreeHandPoints)
        
    def _onClick(self,index1):
        self.tableViewTool.onClick(self.iface, self, self.mdl, self.plotlibrary, index1)
        
    def _onChange(self,item):
        if (not self.mdl.item(item.row(),5) is None 
                and item.column() == 4 
                and self.mdl.item(item.row(),5).data(QtCore.Qt.EditRole).type() == qgis.core.QgsMapLayer.VectorLayer
                and len(self.profiletoolcore.toolrenderer.lastFreeHandPoints) > 1):
            
            self.profiletoolcore.calculateProfil(self.profiletoolcore.toolrenderer.lastFreeHandPoints)
        
    def updateCoordinateTab(self):
        try:
            self.VLayout = self.scrollAreaWidgetContents.layout()
            while 1:
                child = self.VLayout.takeAt(0)
                if not child:
                    break
                child.widget().deleteLater()
        except:
            self.VLayout = QVBoxLayout(self.scrollAreaWidgetContents)
            self.VLayout.setContentsMargins(9, -1, -1, -1)
        self.groupBox = []
        self.profilePushButton = []
        self.coordsPushButton = []
        self.tolayerPushButton = []
        self.tableView = []
        self.verticalLayout = []
        for i in range(0 , self.mdl.rowCount()):
            self.groupBox.append( QGroupBox(self.scrollAreaWidgetContents) )
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.groupBox[i].sizePolicy().hasHeightForWidth())
            self.groupBox[i].setSizePolicy(sizePolicy)
            self.groupBox[i].setMinimumSize(QSize(0, 150))
            self.groupBox[i].setMaximumSize(QSize(16777215, 150))
            try:    #qgis2
                self.groupBox[i].setTitle(QApplication.translate("GroupBox" + str(i), self.profiletoolcore.profiles[i]["layer"].name(), None, QApplication.UnicodeUTF8))
            except: #qgis3
                self.groupBox[i].setTitle(QApplication.translate("GroupBox" + str(i), self.profiletoolcore.profiles[i]["layer"].name(), None))
            self.groupBox[i].setObjectName("groupBox" + str(i))

            self.verticalLayout.append( QVBoxLayout(self.groupBox[i]) )
            self.verticalLayout[i].setObjectName("verticalLayout")
            #The table
            self.tableView.append( QTableView(self.groupBox[i]) )
            self.tableView[i].setObjectName("tableView" + str(i))
            font = QFont("Arial", 8)
            column = len(self.profiletoolcore.profiles[i]["l"])
            self.mdl2 = QStandardItemModel(2, column)
            for j in range(len(self.profiletoolcore.profiles[i]["l"])):
                self.mdl2.setData(self.mdl2.index(0, j, QModelIndex())  ,self.profiletoolcore.profiles[i]["l"][j])
                self.mdl2.setData(self.mdl2.index(0, j, QModelIndex())  ,font ,QtCore.Qt.FontRole)
                self.mdl2.setData(self.mdl2.index(1, j, QModelIndex())  ,self.profiletoolcore.profiles[i]["z"][j])
                self.mdl2.setData(self.mdl2.index(1, j, QModelIndex())  ,font ,QtCore.Qt.FontRole)
            self.tableView[i].verticalHeader().setDefaultSectionSize(18)
            self.tableView[i].horizontalHeader().setDefaultSectionSize(60)
            self.tableView[i].setModel(self.mdl2)
            self.verticalLayout[i].addWidget(self.tableView[i])

            self.horizontalLayout = QHBoxLayout()

            self.profilePushButton.append( QPushButton(self.groupBox[i]) )
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.profilePushButton[i].sizePolicy().hasHeightForWidth())
            self.profilePushButton[i].setSizePolicy(sizePolicy)
            try:    #qgis2
                self.profilePushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard", None, QApplication.UnicodeUTF8))
            except: #qgis3
                self.profilePushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard", None))
            self.profilePushButton[i].setObjectName(str(i))
            self.horizontalLayout.addWidget(self.profilePushButton[i])

            self.coordsPushButton.append(QPushButton(self.groupBox[i]))
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.coordsPushButton[i].sizePolicy().hasHeightForWidth())
            self.coordsPushButton[i].setSizePolicy(sizePolicy)
            try:    #qgis2
                self.coordsPushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard (with coordinates)", None, QApplication.UnicodeUTF8))
            except: #qgis3
                self.coordsPushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard (with coordinates)", None))
                
            self.tolayerPushButton.append(QPushButton(self.groupBox[i]))
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.tolayerPushButton[i].sizePolicy().hasHeightForWidth())
            self.tolayerPushButton[i].setSizePolicy(sizePolicy)
            try:    #qgis2
                self.tolayerPushButton[i].setText(QApplication.translate("GroupBox", "Create Temporary layer", None, QApplication.UnicodeUTF8))
            except: #qgis3
                self.tolayerPushButton[i].setText(QApplication.translate("GroupBox", "Create Temporary layer", None))
                
            self.coordsPushButton[i].setObjectName(str(i))
            self.horizontalLayout.addWidget(self.coordsPushButton[i])
            
            self.tolayerPushButton[i].setObjectName(str(i))
            self.horizontalLayout.addWidget(self.tolayerPushButton[i])

            self.horizontalLayout.addStretch(0)
            self.verticalLayout[i].addLayout(self.horizontalLayout)

            self.VLayout.addWidget(self.groupBox[i])
            
            self.profilePushButton[i].clicked.connect(self.copyTable)
            self.coordsPushButton[i].clicked.connect(self.copyTableAndCoords)
            self.tolayerPushButton[i].clicked.connect(self.createTemporaryLayer)
            
    def copyTable(self):
        nr = int( self.sender().objectName() )
        self.clipboard = QApplication.clipboard()
        text = ""
        for i in range( len(self.profiletoolcore.profiles[nr]["l"]) ):
            text += str(self.profiletoolcore.profiles[nr]["l"][i]) + "\t" + str(self.profiletoolcore.profiles[nr]["z"][i]) + "\n"
        self.clipboard.setText(text)

    def copyTableAndCoords(self):
        nr = int( self.sender().objectName() )
        self.clipboard = QApplication.clipboard()
        text = ""
        for i in range( len(self.profiletoolcore.profiles[nr]["l"]) ):
            text += str(self.profiletoolcore.profiles[nr]["l"][i]) + "\t" + str(self.profiletoolcore.profiles[nr]["x"][i]) + "\t"\
                 + str(self.profiletoolcore.profiles[nr]["y"][i]) + "\t" + str(self.profiletoolcore.profiles[nr]["z"][i]) + "\n"
        self.clipboard.setText(text)
        
    def createTemporaryLayer(self):
        nr = int( self.sender().objectName() )
        type = "Point?crs="+str(self.profiletoolcore.profiles[nr]["layer"].crs().authid()) 
        name = 'ProfileTool_'+str(self.profiletoolcore.profiles[nr]['layer'].name())
        vl = QgsVectorLayer(type, name, "memory")
        pr = vl.dataProvider()
        vl.startEditing()
        # add fields
        pr.addAttributes([QgsField("Value", QVariant.Double) ])
        vl.updateFields()
        #Add features to layer
        for i in range( len(self.profiletoolcore.profiles[nr]["l"]) ):
        
            fet = QgsFeature(vl.fields())
            #set geometry
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(self.profiletoolcore.profiles[nr]['x'][i],self.profiletoolcore.profiles[nr]['y'][i])))
            #set attributes
            fet.setAttributes( [self.profiletoolcore.profiles[nr]["z"][i]] )
            pr.addFeatures([fet])
        vl.commitChanges()
        #labeling/enabled
        if False:
            labelsettings = vl.labeling().settings()
            labelsettings.enabled = True
        
        try:    #qgis2
            qgis.core.QgsMapLayerRegistry.instance().addMapLayer(vl)
        except:     #qgis3
            qgis.core.QgsProject().instance().addMapLayer(vl)
        
    def closeEvent(self, event):
        self.closed.emit()

    def saveAs(self):
        idx = self.cbxSaveAs.currentText()
        if idx == 'PDF':
                self.outPDF()
        elif idx == 'PNG':
                self.outPNG()
        elif idx == 'SVG':
                self.outSVG()
        else:
            print('plottingtool: invalid index '+str(idx))

    def outPDF(self):
        PlottingTool().outPDF(self.iface, self, self.mdl, 'PyQtGraph')

    def outSVG(self):
        PlottingTool().outSVG(self.iface, self, self.mdl, 'PyQtGraph')

    def outPNG(self):
        PlottingTool().outPNG(self.iface, self, self.mdl, 'PyQtGraph')
        
    
