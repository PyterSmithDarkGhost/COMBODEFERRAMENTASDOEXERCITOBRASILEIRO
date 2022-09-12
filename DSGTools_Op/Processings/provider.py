from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from qgis.PyQt.QtGui import QIcon
import os
from .makeMosaic import MakeMosaic
from .matchLayerAndFrame import MatchLayerAndFrame
from .insertMASACODE import ConvertEDGVtoMASACODE
class Provider(QgsProcessingProvider):

    def __init__(self):
        super(Provider, self).__init__()

    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(MakeMosaic())
        self.addAlgorithm(MatchLayerAndFrame())
        self.addAlgorithm(ConvertEDGVtoMASACODE())

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(
            Setting(
                self.name(),
                'ACTIVATE_DSGToolsOp',
                'Activate',
                True
            )
        )
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.RESULTS_GROUP_NAME,
            ProcessingConfig.tr("Results group name"),
            "results",
            valuetype=Setting.STRING,
            placeholder=ProcessingConfig.tr("Leave blank to avoid loading results in a predetermined group")
        ))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def id(self, *args, **kwargs):
        return 'DSGToolsOpProvider'

    def name(self, *args, **kwargs):
        return self.tr('DSGToolsOp')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.abspath(os.path.join(
                    os.path.dirname(__file__)
                )),
                '..',
                'icons',
                'dsg.png'
            )
        )
