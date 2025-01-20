import os
from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.db.database import Database
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.daas.common.config import DatabaseConfig
from app.plugins.core.db.db_backend import DatabaseBackend
from app.plugins.core.db.db_layer import DatabaseObjectLayer
from app.qweb.service.service_runtime import get_qweb_runtime


# pylint: disable=too-few-public-methods
class DatabasePlugin(PluginBase):
    """DB plugin"""

    def __init__(
        self,
    ):
        runtime = get_qweb_runtime()
        cfgfile_db = self.read_toml_file(ConfigFile.DB)
        self.cfg = DatabaseConfig(**cfgfile_db[ConfigSections.DB.value])
        if self.cfg.data_path.startswith("/") is False:
            self.cfg.data_path = (
                f"{runtime.cfg_qweb.sys.root_path}"
                f"/{runtime.cfg_qweb.sys.data_path}"
                f"/{self.cfg.data_path}"
            )

        self.backend = DatabaseBackend(self.cfg)
        self.objlayer = DatabaseObjectLayer(
            name=self.backend.name, backend=self.backend
        )
        self.systasks = []
        self.apitasks = []
        self.handlers = []
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Core,
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
        connected = await self.backend.connect()
        if connected:
            db = Database()
            await db.connect()
            await db.load_demo_apps()
        return connected

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return await self.backend.disconnect()
