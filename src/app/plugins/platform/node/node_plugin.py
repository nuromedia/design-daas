"""Host plugin"""

from app.daas.adapter.adapter_ssh import SshAdapterConfig
from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.node.nodecontrol import NodeControllerConfig
from app.plugins.platform.node.node_backend import NodeBackend
from app.plugins.platform.node.node_routes import handler
from app.plugins.platform.node.node_tasks import (
    NodeTask,
    configure_dhcp,
    configure_iptables,
    invoke_upload,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase


class NodePlugin(PluginBase):
    """Host plugin"""

    def __init__(
        self,
    ):
        cfgfile_db = self.read_toml_file(ConfigFile.NODE)
        self.cfg_ssh = SshAdapterConfig(**cfgfile_db[ConfigSections.HOST_SSH.value])
        self.cfg_dns = NodeControllerConfig(**cfgfile_db[ConfigSections.HOST_DNS.value])
        self.backend = NodeBackend(self.cfg_dns, self.cfg_ssh)
        self.objlayer = None
        self.systasks = []
        self.apitasks = [
            (NodeTask.NODE_CONFIGURE_DHCP.value, configure_dhcp),
            (NodeTask.NODE_CONFIGURE_IPTABLES.value, configure_iptables),
            (NodeTask.NODE_INVOKE_UPLOAD.value, invoke_upload),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Platform,
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
