"""Ceph plugin"""

from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.storage.ceph.ceph_config import CephstoreConfig, CephstoreFilesystemConfig
from app.plugins.storage.ceph.ceph_backend import CephBackend
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.platform.vm.vm_routes import handler


class CephPlugin(PluginBase):
    """Ceph plugin"""

    def __init__(
        self,
    ):
        cfgfile_db = self.read_toml_file(ConfigFile.CEPH)
        self.cfg_storage = CephstoreConfig(
            **cfgfile_db[ConfigSections.CEPH_STORE.value]
        )
        self.backend = CephBackend(self.cfg_storage)
        self.objlayer = None
        self.systasks = []
        self.apitasks = []
        self.handlers = []
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Storage,
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
