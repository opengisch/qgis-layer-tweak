from qgis.PyQt.QtWidgets import QMessageBox


class DesktopTweaker:

    def __init__(self, desktop_iface):
        self.iface = desktop_iface

    def initGui(self):
        QMessageBox.warning(
            self.iface.mainWindow(),
            'qgis_layer_tweak plugin',
            'qgis_layer_tweak is a plugin for QGIS Server in the moment.',
        )

    def unload(self):
        pass