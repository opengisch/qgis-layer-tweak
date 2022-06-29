# -*- coding: utf-8 -*-

"""
***************************************************************************
    render_geojson.py
    ---------------------
    Date                 : June 2022
    Copyright            : (C) 2020 by OPENGIS.ch
    Email                : info@opengis.ch
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Clemens Rudert'
__date__ = 'June 2022'
__copyright__ = '(C) 2022, Clemens Rudert - OPENGIS.ch'

import os

from qgis.server import QgsServerFilter
from qgis.core import QgsMessageLog, Qgis, QgsProject, QgsVectorDataProvider, QgsRasterDataProvider,\
    QgsReadWriteContext, QgsMapLayer, QgsRasterLayer
from PyQt5.QtXml import QDomDocument

name = "TweakLayerServerPlugin"

class ParameterError(Exception):
    """A parameter exception that is raised will be forwarded to the client."""
    pass


class ServerTweakFilter(QgsServerFilter):

    def __init__(self, serverIface=None):
        QgsMessageLog.logMessage(
            "############################ IFACE... {}".format(
                str(serverIface)
            ),
            name,
            Qgis.Info
        )
        if serverIface:
            super().__init__(serverIface)
        self.iface = serverIface
        self.prefix_path = os.environ.get('QGIS_RENDERGEOJSON_PREFIX')

    def requestReady(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()
        layers = []
        QgsMessageLog.logMessage(
            "############################ REQUEST WAS... {}".format(
                params.get('REQUEST', '')
            ),
            name,
            Qgis.Info
        )
        if params.get('LAYERS', ''):
            layers = params['LAYERS'].split(',')
        if params.get('MAP0:LAYERS', ''):
            layers = params['MAP0:LAYERS'].split(',')
        for _, layer in QgsProject.instance().layerStore().mapLayers().items():
            if layer.shortName() in layers:
                QgsMessageLog.logMessage(
                    "############################ Found layer match RELOAD... {}".format(
                        ' - '.join(layers)
                    ),
                    name,
                    Qgis.Info
                )
                provider = layer.dataProvider()
                if isinstance(provider, QgsVectorDataProvider):
                    QgsMessageLog.logMessage(
                        "############################ Found layer is VECTOR",
                        name,
                        Qgis.Info
                    )
                    provider.reloadData()
                elif isinstance(provider, QgsRasterDataProvider):
                    QgsMessageLog.logMessage(
                        "############################ Found layer is RASTER",
                        name,
                        Qgis.Info
                    )
                    self.apply_data_source(layer)

    def set_data_source(self, layer, newProvider, newDatasource, extent):
        '''
        Method to write the new datasource to a raster Layer
        '''
        QgsMessageLog.logMessage(
            "############################ {}".format(layer.id()),
            name,
            Qgis.Info
        )
        XMLDocument = QDomDocument("style")
        XMLMapLayers = XMLDocument.createElement("maplayers")
        XMLMapLayer = XMLDocument.createElement("maplayer")
        context = QgsReadWriteContext()
        layer.writeLayerXml(XMLMapLayer, XMLDocument, context)
        # apply layer definition
        XMLMapLayer.firstChildElement("datasource").firstChild().setNodeValue(newDatasource)
        XMLMapLayer.firstChildElement("provider").firstChild().setNodeValue(newProvider)
        if extent:  # if a new extent (for raster) is provided it is applied to the layer
            XMLMapLayerExtent = XMLMapLayer.firstChildElement("extent")
            XMLMapLayerExtent.firstChildElement("xmin").firstChild().setNodeValue(str(extent.xMinimum()))
            XMLMapLayerExtent.firstChildElement("xmax").firstChild().setNodeValue(str(extent.xMaximum()))
            XMLMapLayerExtent.firstChildElement("ymin").firstChild().setNodeValue(str(extent.yMinimum()))
            XMLMapLayerExtent.firstChildElement("ymax").firstChild().setNodeValue(str(extent.yMaximum()))
        XMLMapLayers.appendChild(XMLMapLayer)
        XMLDocument.appendChild(XMLMapLayers)
        layer.readLayerXml(XMLMapLayer, context)
        layer.reload()
        QgsMessageLog.logMessage(
            "############################ {}".format(layer.id()),
            name,
            Qgis.Info
        )

    def apply_data_source(self, applyLayer):
        '''
        method to verify applying datasource/provider before definitive change to avoid qgis crashes
        '''
        # new layer import
        # fix_print_with_import
        QgsMessageLog.logMessage(
            "############################ Test Data Source",
            name,
            Qgis.Info
        )
        if isinstance(applyLayer, QgsRasterLayer):
                QgsMessageLog.logMessage(
                    "############################ Test Data Source for RASTER",
                    name,
                    Qgis.Info
                )
                probeLayer = QgsRasterLayer(applyLayer.source(), "probe")
                extent = probeLayer.extent()
        else:
            QgsMessageLog.logMessage(
                "############################ Test Data Source was NOT RASTER!",
                name,
                Qgis.Info
            )
            return None
        if not probeLayer.isValid():
            QgsMessageLog.logMessage(
                "############################ Test Data Source for RASTER is not valid!",
                name,
                Qgis.Info
            )
            return None

        newDatasource = probeLayer.source()
        newProvider = probeLayer.dataProvider().name()
        QgsMessageLog.logMessage(
            "############################ Test Data Source for RASTER: VALID",
            name,
            Qgis.Info
        )
        self.set_data_source(applyLayer, newProvider, newDatasource, extent)

    def sendResponse(self):
        pass

    def responseComplete(self):
        pass


class ServerTweaker:
    """Tweak Server behavior"""

    def __init__(self, server_iface):
        self.serverIface = server_iface
        server_iface.registerFilter(ServerTweakFilter(server_iface), 1)
