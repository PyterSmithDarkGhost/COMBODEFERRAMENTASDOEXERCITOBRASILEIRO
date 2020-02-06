# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgTools
                                 A QGIS plugin
 Brazilian Army Cartographic Production Tools
                              -------------------
        begin                : 2018-10-22
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Philipe Borba - Cartographic Engineer @ Brazilian Army
        email                : borba.philipe@eb.mil.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import

from builtins import range
from itertools import tee
from collections import defaultdict

from qgis.analysis import QgsGeometrySnapper, QgsInternalGeometrySnapper
from qgis.core import (Qgis, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsExpression, QgsFeature,
                       QgsFeatureRequest, QgsField, QgsGeometry, QgsMessageLog,
                       QgsProcessingMultiStepFeedback, QgsProject,
                       QgsSpatialIndex, QgsVectorDataProvider, QgsVectorLayer,
                       QgsWkbTypes, edit)
from qgis.PyQt.Qt import QObject, QVariant

from .featureHandler import FeatureHandler
from .geometryHandler import GeometryHandler
from .layerHandler import LayerHandler


class SpatialRelationsHandler(QObject):
    def __init__(self, iface = None, parent = None):
        super(SpatialRelationsHandler, self).__init__()
        self.parent = parent
        self.iface = iface
        if iface:
            self.canvas = iface.mapCanvas()
        self.layerHandler = LayerHandler(iface)
        self.featureHandler = FeatureHandler(iface)
        self.geometryHandler = GeometryHandler(iface)
    
    def relateDrainagesWithContours(self, drainageLyr, contourLyr, frameLinesLyr, heightFieldName, threshold, topologyRadius, feedback=None):
        """
        Checks the conformity between directed drainages and contours.
        Drainages must be propperly directed.
        :param drainageLyr: QgsVectorLayer (line) with drainage lines.
        This must have a primary key field;
        :param contourLyr: QgsVectorLayer (line) with contour lines.
        This must have a primary key field;
        :param frameLinesLyrLyr: QgsVectorLayer (line) with frame lines;
        :param heightFieldName: (str) name of the field that stores
        contour's height;
        :param threshold: (int) equidistance between contour lines;
        :param threshold: (float) topology radius;
        Process steps:
        1- Build spatial indexes;
        2- Compute intersections between drainages and contours;
        3- Relate intersections grouping by drainages: calculate the
        distance between the start point and each intersection, then
        order the points by distance. If the height of each point does
        not follow this order, flag the intersection.
        4- After relating everything,
        """
        maxSteps = 4
        multiStepFeedback = QgsProcessingMultiStepFeedback(maxSteps, feedback) if feedback is not None else None
        currentStep = 0
        if multiStepFeedback is not None:
            if multiStepFeedback.isCanceled():
                return []
            multiStepFeedback.setCurrentStep(currentStep)
            currentStep += 1
            multiStepFeedback.pushInfo(
                self.tr('Building contour structures...')
                )
        contourSpatialIdx, contourIdDict, contourNodeDict, heightsDict = self.buildSpatialIndexAndIdDictRelateNodesAndAttributeGroupDict(
            inputLyr=contourLyr,
            attributeName=heightFieldName,
            feedback=multiStepFeedback
        )
        if multiStepFeedback is not None:
            if multiStepFeedback.isCanceled():
                return []
            multiStepFeedback.setCurrentStep(currentStep)
            currentStep += 1
            multiStepFeedback.pushInfo(
                self.tr('Validating contour structures. Check 1/4...')
                )
        invalidDict = self.validateContourRelations(
            contourNodeDict,
            feedback=multiStepFeedback
            )
        if invalidDict:
            multiStepFeedback.setCurrentStep(maxSteps-1)
            return invalidDict

        if multiStepFeedback is not None:
            if multiStepFeedback.isCanceled():
                return []
            multiStepFeedback.setCurrentStep(currentStep)
            currentStep += 1
            multiStepFeedback.pushInfo(
                self.tr('Building drainage spatial index...')
                )
        drainageSpatialIdx, drainageIdDict, drainageNodeDict = self.buildSpatialIndexAndIdDictAndRelateNodes(
            inputLyr=drainageLyr,
            feedback=multiStepFeedback
        )
        if multiStepFeedback is not None:
            if multiStepFeedback.isCanceled():
                return []
            multiStepFeedback.setCurrentStep(currentStep)
            currentStep += 1
            multiStepFeedback.pushInfo(
                self.tr('Relating contours with drainages...')
                )
        intersectionDict = self.buildIntersectionDict(
            drainageLyr,
            drainageIdDict,
            drainageSpatialIdx,
            contourIdDict,
            contourIdDict
            )

    def buildSpatialIndexAndIdDictAndRelateNodes(self, inputLyr, feedback=None, featureRequest=None):
        """
        creates a spatial index for the input layer
        :param inputLyr: (QgsVectorLayer) input layer;
        :param feedback: (QgsProcessingFeedback) processing feedback;
        :param featureRequest: (QgsFeatureRequest) optional feature request;
        """
        spatialIdx = QgsSpatialIndex()
        idDict = {}
        nodeDict = {}
        featCount = inputLyr.featureCount()
        size = 100/featCount if featCount else 0
        iterator = inputLyr.getFeatures() if featureRequest is None else inputLyr.getFeatures(featureRequest)
        firstAndLastNode = lambda x:self.geometryHandler.getFirstAndLastNode(inputLyr, x)
        addFeatureAlias = lambda x : self.addFeatureToSpatialIndexAndNodeDict(
            current=x[0],
            feat=x[1],
            spatialIdx=spatialIdx,
            idDict=idDict,
            nodeDict=nodeDict,
            size=size,
            firstAndLastNode=firstAndLastNode,
            feedback=feedback
        )
        list(map(addFeatureAlias, enumerate(iterator)))
        return spatialIdx, idDict, nodeDict
    
    def addFeatureToSpatialIndexAndNodeDict(self, current, feat, spatialIdx, idDict, nodeDict, size, firstAndLastNode, feedback):
        """
        Adds feature to spatial index. Used along side with a python map operator
        to improve performance.
        :param current : (int) current index
        :param feat : (QgsFeature) feature to be added on spatial index and on idDict
        :param spatialIdx: (QgsSpatialIndex) spatial index
        :param idDict: (dict) dictionary with format {feat.id(): feat}
        :param size: (int) size to be used to update feedback
        :param firstAndLastNode: (dict) dictionary used to relate nodes of features
        :param feedback: (QgsProcessingFeedback) feedback to be used on processing
        """
        firstNode, lastNode = firstAndLastNode(feat)
        if firstNode not in nodeDict:
            nodeDict[firstNode] = []
        nodeDict[firstNode] += [firstNode]
        if lastNode not in nodeDict:
            nodeDict[lastNode] = []
        nodeDict[lastNode] += [lastNode]
        self.layerHandler.addFeatureToSpatialIndex(current, feat, spatialIdx, idDict, size, feedback)

    def buildSpatialIndexAndIdDictRelateNodesAndAttributeGroupDict(self, inputLyr, attributeName, feedback=None, featureRequest=None):
        """

        """
        spatialIdx = QgsSpatialIndex()
        idDict = {}
        nodeDict = {}
        attributeGroupDict = {}
        featCount = inputLyr.featureCount()
        size = 100/featCount if featCount else 0
        iterator = inputLyr.getFeatures() if featureRequest is None else inputLyr.getFeatures(featureRequest)
        firstAndLastNode = lambda x:self.geometryHandler.getFirstAndLastNode(inputLyr, x)
        addFeatureAlias = lambda x : self.addFeatureToSpatialIndexNodeDictAndAttributeGroupDict(
            current=x[0],
            feat=x[1],
            spatialIdx=spatialIdx,
            idDict=idDict,
            nodeDict=nodeDict,
            size=size,
            firstAndLastNode=firstAndLastNode,
            attributeGroupDict=attributeGroupDict,
            attributeName=attributeName,
            feedback=feedback
        )
        list(map(addFeatureAlias, enumerate(iterator)))
        return spatialIdx, idDict, nodeDict, attributeGroupDict
    
    def addFeatureToSpatialIndexNodeDictAndAttributeGroupDict(self, current, feat, spatialIdx, idDict, nodeDict, size, firstAndLastNode, attributeGroupDict, attributeName, feedback):
        """
        Adds feature to spatial index. Used along side with a python map operator
        to improve performance.
        :param current : (int) current index
        :param feat : (QgsFeature) feature to be added on spatial index and on idDict
        :param spatialIdx: (QgsSpatialIndex) spatial index
        :param idDict: (dict) dictionary with format {feat.id(): feat}
        :param size: (int) size to be used to update feedback
        :param firstAndLastNode: (dict) dictionary used to relate nodes of features
        :param feedback: (QgsProcessingFeedback) feedback to be used on processing
        """
        attrValue = feat[attributeName]
        if attrValue not in attributeGroupDict:
            attributeGroupDict[attrValue] = set()
        attributeGroupDict[attrValue].add(feat.geometry())
        self.addFeatureToSpatialIndexAndNodeDict(current, feat, spatialIdx, idDict, nodeDict, size, firstAndLastNode, feedback)
    
    def validateContourRelations(self, contourNodeDict, frameLinesDict, frameLinesSpatialIdx, heightFieldName, feedback=None):
        """
        param: contourNodeDict: (dict) dictionary with contour nodes
        Invalid contours:
        - Contours that relates to more than 2 other contours;
        - Contours that do not relate to any other contour and does not touch frame lines;
        """
        invalidDict = dict()
        contourId = lambda x : x.id()
        contoursNumber = len(contourNodeDict)
        step = 100/contoursNumber if contoursNumber else 0
        for current, (node, contourList) in enumerate(contourNodeDict.items()):
            if feedback is not None and feedback.isCanceled():
                break
            if len(contourList) == 1:
                if self.isDangle(node, frameLinesDict, frameLinesSpatialIdx):
                    invalidDict[node] = self.tr(
                        'Contour lines id=({ids}) touch each other and have different height values!'
                        ).format(ids=', '.join(map(contourId, contourList)))
            if len(contourList) == 2 and contourList[0][heightFieldName] != contourList[1][heightFieldName]:
                invalidDict[node] = self.tr(
                    'Contour lines id=({ids}) touch each other and have different height values!'
                    ).format(ids=', '.join(map(contourId, contourList)))
            if len(contourList) > 2:
                invalidDict[node] = self.tr(
                    'Contour lines id=({ids}) touch each other. Contour lines must touch itself or only one other.'
                    ).format(ids=', '.join(map(contourId, contourList)))
            if feedback is not None:
                feedback.setProgress(step * current)
        return invalidDict
    
    def isDangle(self, point, featureDict, spatialIdx, searchRadius=10**-15):
        """
        :param point: (QgsPointXY) node tested as dangle;
        :param featureDict: (dict) dict {featid:feat};
        :param spatialIdx: (QgsSpatialIndex) spatial index
        of features from featureDict;
        :param searchRadius: (float) search radius.
        """
        qgisPoint = QgsGeometry.fromPointXY(point)
        buffer = qgisPoint.buffer(searchRadius, -1)
        bufferBB = buffer.boundingBox()
        for featid in spatialIdx.intersects(bufferBB):
            if buffer.intersects(featureDict[featid].geometry()) and \
                qgisPoint.distance(featureDict[featid].geometry()) < 10**-9:
                return True
        return False

    def buildIntersectionDict(self, drainageLyr, drainageIdDict, drainageSpatialIdx, contourIdDict, contourSpatialIdx, feedback=None):
        intersectionDict = dict()
        flagDict = dict()
        firstNode = lambda x:self.geometryHandler.getFirstNode(drainageLyr, x)
        lastNode = lambda x:self.geometryHandler.getLastNode(drainageLyr, x)
        addItemsToIntersectionDict = lambda x:self.addItemsToIntersectionDict(
            dictItem=x,
            contourSpatialIdx=contourSpatialIdx,
            contourIdDict=contourIdDict,
            intersectionDict=intersectionDict,
            firstNode=firstNode,
            lastNode=lastNode,
            flagDict=flagDict
        )
        # map for, this means: for item in drainageIdDict.items() ...
        list(map(addItemsToIntersectionDict, drainageIdDict.items()))
        return intersectionDict
    
    def addItemsToIntersectionDict(self, dictItem, contourSpatialIdx, contourIdDict, intersectionDict, firstNode, lastNode, flagDict):
        gid, feat = dictItem
        featBB = feat.geometry().boundingBox()
        featid = feat.id()
        featGeom = feat.geometry()
        intersectionDict[featid] = {
            'start_point':firstNode(featGeom), 
            'end_point':lastNode(featGeom),
            'intersection_list':[]
            }
        for candidateId in contourSpatialIdx.intersects(featBB):
            candidate = contourIdDict[candidateId]
            candidateGeom = candidate.geometry()
            if candidateGeom.intersects(featGeom): #add intersection
                intersectionGeom = candidateGeom.intersection(featGeom)
                intersectionList += [intersectionGeom.asPoint()] if not intersectionGeom.asMultiPoint() else intersectionGeom.asMultiPoint()
                flagFeature = True if len(intersectionList) > 1 else False
                for inter in intersectionList:
                    if flagFeature:
                        flagDict[inter] = self.tr('Contour id={c_id} intersects drainage id={d_id} in more than one point').format(
                            c_id=candidateId,
                            d_id=gid
                        )
                    newIntersection = {
                    'contour_id' : candidateId,
                    'intersection_point' : inter
                    }
                    intersectionDict[featid]['intersection_list'].append(newIntersection)
    
    def validateIntersections(self, intersectionDict, heightFieldName, threshold):
        """
        1- Sort list
        2- 
        """
        validatedIdsDict = dict()
        invalidatedIdsDict = dict()
        for id, values in intersectionDict.items():
            interList = values['intersection_list']
            if len(interList) <= 1:
                continue
            #sort list by distance from start point
            interList.sort(key=lambda x: x['intersection_point'].geometry().distance(values['start_point']))
            referenceElement = interList[0]
            for idx, elem in enumerate(interList[1::], start=1):
                elemen_id = elem.id()
                if int(elem[heightFieldName]) != threshold*idx + int(referenceElement[heightFieldName]):
                    invalidatedIdsDict[elemen_id] = elem
                else:
                    if elemen_id not in invalidatedIdsDict:
                        validatedIdsDict[elemen_id] = elem
        for id in validatedIdsDict:
            if id in invalidatedIdsDict:
                validatedIdsDict.pop(id)
        return validatedIdsDict, invalidatedIdsDict
    
    def validateContourPolygons(self, contourPolygonDict, contourPolygonIdx, threshold, heightFieldName, depressionValueDict=None):
        hilltopDict = self.buildHilltopDict(
            contourPolygonDict,
            contourPolygonIdx
            )
        invalidDict = dict()
        for hilltopGeom, hilltop in hilltopDict.items():
            localFlagList = []
            polygonList = hilltop['downhill']
            feat = hilltop['feat']
            if len(polygonList) < 2:
                break
            # sort polygons by area, from minimum to max
            polygonList.sort(key=lambda x: x.geometry().area())
            #pair comparison
            a, b = tee([feat]+polygonList)
            next(b, None)
            for elem1, elem2 in zip(a, b):
                if abs(elem1[heightFieldName]-elem2[heightFieldName]) != threshold:
                    elem1GeomKey = elem1.geometry().asWkb()
                    if elem1GeomKey not in invalidDict:
                        invalidDict[elem1GeomKey] = []
                    invalidDict[elem1GeomKey] += [self.tr(
                        'Difference between contour with values {id1} \
                        and {id2} do not match equidistance {equidistance}.\
                        Probably one contour is \
                        missing or one of the contours have wrong value.\n'
                    ).format(
                        id1=elem1[heightFieldName],
                        id2=elem2[heightFieldName],
                        equidistance=threshold
                    )]
        return invalidDict
    
    def buildHilltopDict(self, contourPolygonDict, contourPolygonIdx):
        hilltopDict = dict()
        buildDictAlias = lambda x: self.initiateHilltopDict(x, hilltopDict)
        # c loop to build contourPolygonDict
        list(map(buildDictAlias, contourPolygonDict.values()))
        # iterate over contour polygon dict and build hilltopDict
        for idx, feat in contourPolygonDict.items():
            geom = feat.geometry()
            bbox = geom.boundingBox()
            geomWkb = geom.asWkb()
            for candId in contourPolygonIdx.intersects(bbox):
                candFeat = contourPolygonDict[candId]
                candGeom = candFeat.geometry()
                if candId != idx and candGeom.within(geom):
                    hilltopDict.pop(geomWkb.asWkb())
                    break
                if candId != idx and candGeom.contains(geom) \
                    and candFeat not in hilltopDict[geomWkb]['donwhill']:
                    hilltopDict[geomWkb]['donwhill'].append(candFeat)
            return hilltopDict
    
    def initiateHilltopDict(self, feat, hilltopDict):
        hilltopDict[feat.geometry().asWkb()] = {
                'feat' : feat,
                'downhill': []
            }
    
    def buildTerrainPolygons(self, featList):
        pass

    def validateContourLines(self, contourLyr, contourAttrName, refLyr, feedback=None):
        """
        1. Validate contour connectivity;
        2. Build terrain polygons by contour value;
        3. Build terrain dict;
        4. Validate contours.
        """
        pass
    
    def validateSpatialRelations(self, ruleList, createSpatialIndex=True, feedback=None):
        """
        1. iterate over rule list and get all layers.
        2. build spatial index
        3. test rule
        """
        multiStepFeedback = QgsProcessingMultiStepFeedback(4, feedback) if feedback is not None else None
        if multiStepFeedback is not None:
            multiStepFeedback.setCurrentStep(0)
        spatialDict = self.buildSpatialDictFromRuleList(ruleList, feedback=multiStepFeedback)
        if multiStepFeedback is not None:
            multiStepFeedback.setCurrentStep(1)
        spatialRuleDict = self.buildSpatialRuleDict(ruleList, feedback=multiStepFeedback)
        if multiStepFeedback is not None:
            multiStepFeedback.setCurrentStep(2)
        self.buildSpatialRelationDictOnSpatialRuleDict(
            spatialDict=spatialDict,
            spatialRuleDict=spatialRuleDict,
            feedback=multiStepFeedback
        )
        if multiStepFeedback is not None:
            multiStepFeedback.setCurrentStep(3)
        flagList = self.identifyInvalidRelations(spatialDict, spatialRuleDict, feedback=multiStepFeedback):
        return flagList

    def buildSpatialDictFromRuleList(self, ruleList, feedback=None):
        """
        returns {
            'key formed by layer name and filter' : {
                'spatial_index' : QgsSpatialIndex
                'feature_id_dict' : {
                    'feat_id' : 'feat'
                }
            }
        }
        """
        progressStep = 100/len(ruleList) if ruleList else 0
        spatialDict = defaultdict(dict)
        for current, rule in enumerate(ruleList):
            if feedback is not None and feedback.isCanceled():
                break
            inputKey = '_'.join(rule['input_layer'].name(), rule['input_layer_filter'])
            candidateKey = '_'.join(rule['candidate_layer'].name(), rule['candidate_layer_filter'])
            for key in [inputKey, candidateKey]:
                if key not in spatialDict:
                    spatialDict[key]['spatial_index'], spatialDict[key]['feature_id_dict'] = self.layerHandler.buildSpatialIndexAndIdDict(
                        inputLyr=rule['input_layer'],
                        featureRequest=rule['input_layer_filter']
                    )
            if feedback is not None:
                feedback.setProgress(current * progressStep)
        return spatialDict
    
    def buildSpatialRuleDict(self, ruleList, feedback=None):
        """
        ruleList comes from the ui
        Rule list has the following format:
        ruleList = [
            {
                'input_layer': QgsVectorLayer,
                'input_layer_filter' : str,
                'predicate' : str,
                'candidate_layer' : QgsVectorLayer,
                'candidate_layer_filter' : str,
                'cardinality' : str,
                'feat_relation_list' : list of pairs of (featId, relatedFeatures),
                'flag_text' : str
            }
        ]

        outputs:
        { 'input_layer_input_layer_filter' : {
                        'input_layer': QgsVectorLayer,
                        'input_layer_filter' : str,
                        'rule_list' : [
                            {
                                'predicate' : str,
                                'candidate_layer' : QgsVectorLayer,
                                'candidate_layer_filter' : str,
                                'cardinality' : str,
                                'flag_text' : str,
                                'feat_relation_list' : list of pairs of (featId, relatedFeatures)
                            }
                        ]
                    }
        }
        """
        spatialRuleDict = defaultdict(
            lambda : {
                'input_layer' : None,
                'input_layer_filter' : '',
                'rule_list' : []
            }
        )
        progressStep = 100/len(ruleList) if ruleList else 0
        for current, rule in enumerate(ruleList):
            if feedback is not None and feedback.isCanceled():
                break
            key = '_'.join(rule['input_layer'].name(), rule['input_layer_filter'])
            spatialRuleDict[key]['input_layer'] = rule['input_layer']
            spatialRuleDict[key]['input_layer_filter'] = rule['input_layer_filter']
            spatialRuleDict[key]['rule_list'].append(
                {k:v for k, v in rule.items() if 'input' not in k}
            )
            if feedback is not None:
                feedback.setProgress(current * progressStep)
        return spatialRuleDict

    
    def buildSpatialRelationDictOnSpatialRuleDict(self, spatialDict, spatialRuleDict, feedback=None):
        """
        layerFeatureDict = {
            'layer_name' = {
                featId : QgsFeature
            }
        }
        spatialIndexDict = {
            'layer_name' : QgsSpatialIndex
        }
        spatialRuleDict = { 'input_layer_input_layer_filter' : {
                                                                    'input_layer': QgsVectorLayer,
                                                                    'input_layer_filter' : str,
                                                                    'rule_list' : [
                                                                        {
                                                                            'predicate' : str,
                                                                            'candidate_layer' : QgsVectorLayer,
                                                                            'candidate_layer_filter' : str,
                                                                            'cardinality' : str,
                                                                            'flag_text' : str
                                                                        }
                                                                    ]
                                                                }
        }

        """
        totalSteps = self.countSteps(spatialRuleDict, spatialDict)
        progressStep = 100/totalSteps if totalSteps else 0
        counter = 0
        for inputKey, inputDict in spatialRuleDict.items():
            if feedback is not None and feedback.isCanceled():
                break
            keyRuleList = ['_'.join(i['candidate_layer'], i['candidate_layer_filter'] for i in inputDict['rule_list']]
            for featId, feat in spatialDict[inputKey]['feature_id_dict']:
                if feedback is not None and feedback.isCanceled():
                    break
                for idx, rule in enumerate(inputDict['rule_list']):
                    if feedback is not None and feedback.isCanceled():
                        break
                    rule['feat_relation_list'].append( 
                        (
                            featId, self.relateFeatureAccordingToPredicate(
                                feat=feat,
                                rule=rule,
                                key=keyRuleList[idx],
                                predicate=rule['predicate'],
                                spatialDict=spatialDict
                            )
                        )
                    )
                    counter+=1
                    if feedback is not None:
                        feedback.setProgress(counter * progressStep)
    
    def countSteps(self, spatialRuleDict, spatialDict):
        """
        Counts the number of steps of execution.
        """
        steps = len(spatialRuleDict)
        for k,v in spatialRuleDict.items():
            steps += len(v['rule_list'])
            steps += len(spatialDict[k]['feature_id_dict'])
        return steps
    
    def prepareEngine(self, feat):
        """
        Prepairs the geometryEngine for spatial comparisons.

        returns geom (QgsGeometry), geom_BB (QgsRectangle), engine (QgsGeometryEngine)
        """
        geom = feat.geometry()
        geom_BB = geom.boundingBox()
        #geometry engine is the fastest way of comparing geometries in QGIS 3.x series
        engine = QgsGeometry.createGeometryEngine(geom.constGet())
        engine.prepareGeometry()
        return geom, geom_BB, engine
                
    def relateFeatureAccordingToPredicate(self, feat, rule, key, predicate, spatialDict):
        geom, geom_BB, engine = self.prepareEngine(feat)
        relationSet = set()
        predicate = rule['predicate']
        candidateSpatialIdx = spatialDict[key]['spatial_index']
        candidateFeatureDict = spatialDict[key]['feature_id_dict']
        for fid in candidateSpatialIdx.intersects(geom_BB):
            test_feat = candidateFeatureDict[fid]
            if getattr(engine, predicate)(test_feat.geometry().constGet()):
                relationSet.add(test_feat)
        return relationSet
    
    def parseCardinalityAndGetLambdaToIdentifyProblems(self, cardinality, necessity, isSameLayer=False):
        """
        Parses cardinality and returns a lambda to verify if the list of features 
        that relates to the considered feature violates rule.
        """
        if cardinality is None:
            lambdaCompair = lambda x: len(x) != 0
            return lambdaCompair
        min_card, max_card = cardinality.split('..')
        if max_card != '*'
            lambdaCompair = lambda x : len(x) < int(min_card)
        elif min_card == max_card:
            lambdaCompair = lambda x: len(x) != int(min_card)
        else:
            lambdaCompair = lambda x : len(x) < int(min_card) or len(x) > int(max_card)
        return lambdaCompair
    
    def identifyInvalidRelations(self, spatialDict, spatialRuleDict, feedback=None):
        """
        Identifies invalid spatial relations and returns a list with flags to be raised.
        """
        totalSteps = self.countSteps(spatialRuleDict, spatialDict)
        progressStep = 100/totalSteps if totalSteps else 0
        counter = 0
        invalidFlagList = []
        for inputKey, inputDict in spatialRuleDict:
            if feedback is not None and feedback.isCanceled():
                        break
            inputLyrName = inputDict['input_layer']
            for rule in inputDict['rule_list']:
                if feedback is not None and feedback.isCanceled():
                        break
                candidateLyrName = i['candidate_layer']
                candidateKey = '_'.join(candidateLyrName, i['candidate_layer_filter']
                sameLayer = True if inputKey == candidateKey else False
                lambdaCompair = self.parseCardinalityAndGetLambdaToIdentifyProblems(
                    cardinality=rule['cardinality'],
                    necessity=rule['necessity'],
                    isSameLayer=sameLayer
                )
                for featId, relatedFeatures in rule['feat_relation_list']:
                    if feedback is not None and feedback.isCanceled():
                        break
                    inputFeature=spatialDict[inputKey][featId]
                    if lambdaCompair(relatedFeatures):
                        if inputLyrName == candidateLyrName and inputFeature in relatedFeatures:
                            relatedFeatures.pop(inputFeature)
                        invalidFlagList += self.buildSpatialFlags(
                            inputFeature=inputFeature,
                            relatedFeatures=relatedFeatures,
                            flagText=rule['flag_text']
                        )
                    if feedback is not None:
                        feedback.setProgress(counter * progressStep)
                        counter += 1
        return invalidFlagList
    
    def buildSpatialFlags(self, inputLyrName, inputFeature, candidateLyrName, relatedFeatures, flagText):
        input_id = inputFeature.id()
        inputGeom = inputFeature.geometry()
        spatialFlags = []
        for feat in relatedFeatures:
            flagGeom = inputGeom.intersection(feat.geometry().constGet())
            flagText = self.tr('Feature from {input} with id {input_id} violates the following predicate with feature from {candidate} with id {candidate_id}: {predicate_text}').format(
                input=inputLyrName,
                input_id=input_id,
                candidate=candidateLyrName,
                candidate_id=feat.id(),
                predicate_text=flagText
            )
            spatialFlags.append(
                {
                    'flagGeom' : flagGeom,
                    'flagText' : flagText
                }
            )
        return spatialFlags


    

