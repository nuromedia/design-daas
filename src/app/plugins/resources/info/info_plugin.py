"""Info plugin"""

from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.resources.info.config import SysteminfoConfig
from app.plugins.resources.info.info_backend import InfoBackend
from app.plugins.resources.info.info_tasks import (
    InfoTask,
    dashboard_info,
    monitoring_info,
    monitoring_info_apps,
    monitoring_info_files,
    monitoring_info_host,
    monitoring_info_limits,
    monitoring_info_objects,
    monitoring_info_sockets,
    monitoring_info_tasks,
    monitoring_info_utilization,
)
from app.plugins.resources.info.info_routes import handler


class InfoPlugin(PluginBase):
    """Info plugin"""

    def __init__(self):
        cfgfile_db = self.read_toml_file(ConfigFile.INFO)
        self.cfg = SysteminfoConfig(**cfgfile_db[ConfigSections.INFO_SYS.value])
        self.backend = InfoBackend(self.cfg)
        self.objlayer = None
        self.systasks = []
        self.apitasks = [
            (InfoTask.INFO_DASHBOARD.value, dashboard_info),
            (InfoTask.INFO_MONITORING.value, monitoring_info),
            (InfoTask.INFO_MONITORING_TASKS.value, monitoring_info_tasks),
            (InfoTask.INFO_MONITORING_APPS.value, monitoring_info_apps),
            (InfoTask.INFO_MONITORING_FILES.value, monitoring_info_files),
            (InfoTask.INFO_MONITORING_SOCKETS.value, monitoring_info_sockets),
            (InfoTask.INFO_MONITORING_HOST.value, monitoring_info_host),
            (InfoTask.INFO_MONITORING_OBJECTS.value, monitoring_info_objects),
            (InfoTask.INFO_MONITORING_UTILIZATION.value, monitoring_info_utilization),
            (InfoTask.INFO_MONITORING_LIMITS.value, monitoring_info_limits),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Late,
            False,
            backends=[self.backend],
            layers=[],
            handlers=self.handlers,
            systasks=self.systasks,
            apitasks=self.apitasks,
            authenticator=None,
            taskmanager=None,
        )

    async def plugin_start(self) -> bool:
        """Starts plugin"""
        return await self.backend.connect()

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return await self.backend.disconnect()
