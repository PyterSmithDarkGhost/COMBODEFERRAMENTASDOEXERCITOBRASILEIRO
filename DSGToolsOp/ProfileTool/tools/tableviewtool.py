# -*- coding: utf-8 -*-
#Qt import
from qgis.PyQt import uic, QtCore, QtGui
try:
    from qgis.PyQt.QtGui import QInputDialog, QMessageBox
except:
    from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
#qgis import
from qgis.core import *
from qgis.gui import *
#plugin import
from .plottingtool import *
from .utils import isProfilable


class TableViewTool(QtCore.QObject):
    
    layerAddedOrRemoved = QtCore.pyqtSignal()

    def addLayer(self , iface, mdl, layer1 = None):
        if layer1 == None:
            templist=[]
            j=0
            # Ask the layer by a input dialog 
            for i in range(0, iface.mapCanvas().layerCount()):
                donothing = False
                layer = iface.mapCanvas().layer(i)
                if isProfilable(layer):
                    for j in range(0, mdl.rowCount()):
                        if str(mdl.item(j,2).data(QtCore.Qt.EditRole)) == str(layer.name()):
                            donothing = True
                else:
                    donothing = True
                    
                if donothing == False:
                    templist +=  [[layer, layer.name()]]
                        
            if len(templist) == 0:
                QMessageBox.warning(iface.mainWindow(), u"Perfil do terreno", u"Não há camadas raster para adicionar.")
                return
            else:    
                testqt, ok = QInputDialog.getItem(iface.mainWindow(), u"Seletor de camadas", u"Selecione uma camada", [templist[k][1] for k in range( len(templist) )], False)
                if ok:
                    for i in range (0,len(templist)):
                        if templist[i][1] == testqt:
                            layer2 = templist[i][0]
                else:
                    return
        else : 
            if isProfilable(layer1):
                layer2 = layer1
            else:
                QMessageBox.warning(iface.mainWindow(), u"Perfil do terreno", u"Camada ativa não pode ser usada para gerar perfis.")
                return

        # Ask the Band by a input dialog
        #First, if isProfilable, considerate the real band number (instead of band + 1 for raster)
        if layer2.type() == layer2.PluginLayer and  isProfilable(layer2):
            self.bandoffset = 0
            typename = u'parâmetro'
        elif layer2.type() == layer2.RasterLayer:
            self.bandoffset = 1
            typename = u'banda'
        elif layer2.type() == layer2.VectorLayer:
            self.bandoffset = 0
            typename = u'campo'

        if layer2.type() == layer2.RasterLayer and layer2.bandCount() != 1:
            listband = []
            for i in range(0,layer2.bandCount()):
                listband.append(str(i+self.bandoffset))
            testqt, ok = QInputDialog.getItem(iface.mainWindow(), u"Seletor de " + typename , u"Selecione " + typename, listband, False)
            if ok :
                choosenBand = int(testqt) - self.bandoffset
            else:
                return 2
        elif layer2.type() == layer2.VectorLayer :
            fieldstemp = [field.name() for field in layer2.fields() ]
            if int(QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                fields = [field.name() for field in layer2.fields() if field.type() in [2,3,4,5,6]]
            
            elif int(QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                fields = [field.name() for field in layer2.fields() if field.isNumeric()]
            if len(fields)==0:
                QMessageBox.warning(iface.mainWindow(), u"Perfil do terreno", u"Camada ativa não pode ser usada para gerar perfis.")
                return
            elif len(fields) == 1 :
                choosenBand = fieldstemp.index(fields[0])
                
            else:
                testqt, ok = QInputDialog.getItem(iface.mainWindow(), u"Seletor de " + typename , u"Selecione " + typename, fields, False)
                if ok :
                    choosenBand = fieldstemp.index(testqt)
                else:
                    return 2
            
        else:
            choosenBand = 0

        #Complete the tableview
        row = mdl.rowCount()
        mdl.insertRow(row)
        mdl.setData( mdl.index(row, 0, QModelIndex()) ,QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        mdl.item(row,0).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
        lineColour = QtCore.Qt.red
        if layer2.type() == layer2.PluginLayer and layer2.LAYER_TYPE == 'crayfish_viewer':
            lineColour = QtCore.Qt.blue
        mdl.setData( mdl.index(row, 1, QModelIndex())  ,QColor(lineColour) , QtCore.Qt.BackgroundRole)
        mdl.item(row,1).setFlags(QtCore.Qt.ItemIsEnabled) 
        mdl.setData( mdl.index(row, 2, QModelIndex())  ,layer2.name())
        mdl.item(row,2).setFlags(QtCore.Qt.ItemIsEnabled) 
        mdl.setData( mdl.index(row, 3, QModelIndex())  ,choosenBand + self.bandoffset)
        mdl.item(row,3).setFlags(QtCore.Qt.ItemIsEnabled) 

        if layer2.type() == layer2.VectorLayer :
            mdl.setData( mdl.index(row, 4, QModelIndex())  ,100.0)
        else:
            mdl.setData( mdl.index(row, 4, QModelIndex())  ,'')
            mdl.item(row,4).setFlags(QtCore.Qt.NoItemFlags) 
            
        mdl.setData( mdl.index(row, 5, QModelIndex())  ,layer2)
        mdl.item(row,5).setFlags(QtCore.Qt.NoItemFlags)
        self.layerAddedOrRemoved.emit()
        
    def removeLayer(self, mdl, index):
        try:
            mdl.removeRow(index)
            self.layerAddedOrRemoved.emit()
        except:
            return

    def chooseLayerForRemoval(self, iface, mdl):
        
        if mdl.rowCount() < 2:
            if mdl.rowCount() == 1:
                return 0
            return None

        list1 = []
        for i in range(0,mdl.rowCount()):
            list1.append(str(i +1) + " : " + mdl.item(i,2).data(QtCore.Qt.EditRole))
        testqt, ok = QInputDialog.getItem(iface.mainWindow(), u"Seletor de camadas", u"Selecione uma camada", list1, False)
        if ok:
            for i in range(0,mdl.rowCount()):
                if testqt == (str(i+1) + " : " + mdl.item(i,2).data(QtCore.Qt.EditRole)):
                    return i
        return None
        
    def onClick(self, iface, wdg, mdl, plotlibrary, index1):
        temp = mdl.itemFromIndex(index1)
        if index1.column() == 1:                #modifying color
            name = ("%s#%d") % (mdl.item(index1.row(),2).data(QtCore.Qt.EditRole), mdl.item(index1.row(),3).data(QtCore.Qt.EditRole))
            color = QColorDialog().getColor(temp.data(QtCore.Qt.BackgroundRole))
            mdl.setData( mdl.index(temp.row(), 1, QModelIndex())  ,color , QtCore.Qt.BackgroundRole)
            PlottingTool().changeColor(wdg, plotlibrary, color, name)
        elif index1.column() == 0:                #modifying checkbox
            name = ("%s#%d") % (mdl.item(index1.row(),2).data(QtCore.Qt.EditRole), mdl.item(index1.row(),3).data(QtCore.Qt.EditRole))
            booltemp = temp.data(QtCore.Qt.CheckStateRole)
            mdl.setData( mdl.index(temp.row(), 0, QModelIndex())  ,booltemp, QtCore.Qt.CheckStateRole)
            PlottingTool().changeAttachCurve(wdg, plotlibrary, booltemp, name)
        elif False and index1.column() == 4:               
            name = mdl.item(index1.row(),4).data(QtCore.Qt.EditRole)
            print(name)
        else:
            return

        
