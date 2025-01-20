"""Resource limit plugin"""

from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.resources.limits.ressource_limits import RessourceLimitsConfig
from app.plugins.core.db.db_layer import DatabaseObjectLayer
from app.plugins.resources.limits.limits_backend import LimitBackend
from app.plugins.resources.limits.limits_layer import LimitObjectLayer
from app.plugins.resources.limits.limits_tasks import (
    LimitTask,
    limit_get,
    limit_list,
    limit_put,
    limit_remove,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.resources.limits.limits_routes import handler


class LimitPlugin(PluginBase):
    """Resource limit plugin"""

    def __init__(self):
        cfgfile_db = self.read_toml_file(ConfigFile.LIMITS)
        self.cfg_limit = RessourceLimitsConfig(
            **cfgfile_db[ConfigSections.LIMITS.value]
        )
        self.backend = LimitBackend(self.cfg_limit)
        self.objlayer = LimitObjectLayer(name=self.backend.name, backend=self.backend)
        self.systasks = []
        self.apitasks = [
            (LimitTask.LIMIT_GET.value, limit_get),
            (LimitTask.LIMIT_PUT.value, limit_put),
            (LimitTask.LIMIT_REMOVE.value, limit_remove),
            (LimitTask.LIMIT_LIST.value, limit_list),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Late,
            False,
            backends=[self.backend],
            layers=[self.objlayer],
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
