# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DSGTools Op
                                 A QGIS plugin
 Ferramentas para planejamento militar do Exército Brasileiro
                             -------------------
        begin                : 2017-01-01
        copyright            : (C) 2017 by Diego Benincasa
        email                : benincasa.diego@eb.mil.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from .dsgtoolsop import DSGToolsOp

def classFactory(iface):
    return DSGToolsOp(iface)
