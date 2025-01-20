"""Host Backend"""

from app.daas.adapter.adapter_ssh import SshAdapterConfig
from app.daas.common.enums import BackendName
from app.daas.node.nodecontrol import NodeController, NodeControllerConfig
from app.qweb.service.service_context import QwebBackend


class NodeBackend(QwebBackend):
    """Database backend"""

    cfg: NodeControllerConfig
    nodecon: NodeController

    def __init__(self, cfg_dns: NodeControllerConfig, cfg_ssh: SshAdapterConfig):
        self.cfg_dns = cfg_dns
        self.cfg_ssh = cfg_ssh
        self.nodecon = NodeController(self.cfg_dns, self.cfg_ssh)
        QwebBackend.__init__(self, name=BackendName.NODE.value, component=self.nodecon)

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects database adapter"""
        if self.nodecon is not None:
            self.connected = self.nodecon.connect()
            return self.connected
        return False

    async def disconnect(self) -> bool:
        """Disconnects database adapter"""
        if self.nodecon is not None:
            self.nodecon.disconnect()
            self.connected = self.nodecon.connected
            return True
        return False
