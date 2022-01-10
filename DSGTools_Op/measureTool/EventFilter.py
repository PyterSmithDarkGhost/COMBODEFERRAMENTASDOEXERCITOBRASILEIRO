# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
import math


class EventFilter(QObject):
   
    def __init__(self, iface, pointList, enableAction):
        QObject.__init__(self)
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        self.pointList = pointList
        self.enableAction = enableAction
        # Tratamento para o plugin funcionar somente com a active layer
        self.active = False

    def close(self):
        pass

    
    ###################
    ##### EVENTOS #####
    ###################

    def eventFilter(self, obj, event):
        # Nós só executamos isso se o evento for espontâneo, significa que foi gerado pelo sistema operacional.
        # Desta forma, o evento que criamos abaixo não será processado (o que seria um loop inifinito)
        if not event.spontaneous():
            return QObject.eventFilter(self, obj, event)
            
        # MOVEU MOUSE OU CLICK ESQUERDO
        if ( (  (event.type() == QEvent.MouseMove and event.button() != Qt.MidButton) or
                (event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton) or
                (event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton) )
                and self.active == True ):
            curPoint = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates( event.pos() )
            self.updateMeasure(curPoint)
            
            self.pointList.updateCurrentPoint(curPoint)

            # Modo de entrada do mouse
            modifiedEvent = QMouseEvent( event.type(), self.toPixels(curPoint), event.button(), event.buttons(), event.modifiers() )
            QCoreApplication.sendEvent(obj,modifiedEvent)
                
           
        # No modo de entrada (B), registramos os últimos pontos para seguir o cálculo relativo em caso de mousePress
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.pointList.newPoint()   
            # Ao retornar True, informamos ao eventSystem que o evento não deve ser enviado mais (desde que um novo evento tenha sido enviado por meio de QCoreApplication)
            return True

        elif event.type() == QEvent.KeyPress:
            # remove último ponto
            if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
                self.pointList.removeLastPoint()
                return False
            # Se inputWidget interceptou o evento, isso será True (evento não propagado ainda)
            return event.isAccepted()

        # CLIQUE DIREITO
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.RightButton:
            # cancelar a digitalização ao clicar com o botão direito
            self.pointList.empty()
            QCoreApplication.sendEvent(obj,event)
            return True

        # DE OUTRA FORMA
        else:
            return QObject.eventFilter(self, obj, event)


    ###############################
    ##### ATUALIZANDO MEDIDAS #####
    ###############################

    def updateMeasure(self, point): 
        previousPoint = self.pointList.previousPoint()
        dist, distAcum = None, None
        area = None
    
        #################
        if self.iface.mapCanvas().currentLayer().geometryType() == QgsWkbTypes.LineGeometry:
            # Restrição de distância
            if len(self.pointList)>1:
                dist = math.sqrt(point.sqrDist(previousPoint))
    
            line = QgsGeometry.fromPolylineXY(self.pointList)
            distAcum = line.length()
            
            if dist != None and self.enableAction.isChecked():
                                
                    # Configura a cor referente a distância Parcial
                    color = 'darkred'
                    color2 = 'yellow'
                    txt = "<p style='background-color:{color};color:{color2}'><b>Parcial: {distance} m</b><br/>".format(color=color, color2=color2, distance="%.3f" % dist)    
                    txt += "<b>Total: {distance} m</b></p>".format(distance="%.3f" % distAcum)
                    # Configura a apresentação tooltip no mouse                 
                    QToolTip.showText(self.mapCanvas.mapToGlobal(self.mapCanvas.mouseLastXY()), txt, self.mapCanvas)
            else:
                QToolTip.hideText()
                
        
        elif self.iface.mapCanvas().currentLayer().geometryType() == QgsWkbTypes.PolygonGeometry:
            # Restrição de distância
            tempPointList = []
            
            if len(self.pointList)>2:
                tempPointList = self.pointList[:]
                tempPointList.append(self.pointList[0])
                polygon = QgsGeometry.fromPolygonXY([tempPointList])
                area = polygon.area()

            if area != None and self.enableAction.isChecked():
                                
                    # Configura a cor referente a distância Parcial
                    color = 'darkred'
                    color2 = 'yellow'
                    txt = "<p style='background-color:{color};color:{color2}'><b>Área: {area}</b></p>".format(color=color, color2=color2, area="%.3f" % area)    
                    # Configura a apresentação tooltip no mouse
                    QToolTip.showText(self.mapCanvas.mapToGlobal(self.mapCanvas.mouseLastXY()), txt, self.mapCanvas)
            else:
                QToolTip.hideText()

        
    #######################################
    ##### TRANSFORMAÇÃO DE COORDENADAS ####
    #######################################

    def toPixels(self, qgspoint):
        """
        Dado um ponto nas coordenadas do projeto, retorna um ponto nas coordenadas de tela (pixel)
        """
        try:
            p = self.iface.mapCanvas().getCoordinateTransform().transform( qgspoint )
            return QPoint( int(p.x()), int(p.y()) )
        except ValueError:
            # isso acontece às vezes no carregamento, parece que o mapCanvas não está pronto e retorna um ponto na NaN
            return QPoint()


