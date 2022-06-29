# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""


def classFactory(desktop_iface):
    from .tweak_desktop import DesktopTweaker

    return DesktopTweaker(desktop_iface)


def serverClassFactory(server_iface):
    from .tweak_server import ServerTweaker

    return ServerTweaker(server_iface)
