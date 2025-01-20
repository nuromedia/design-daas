"""Messaging Backend"""

from app.daas.adapter.adapter_ssh import SshAdapterConfig
from app.daas.common.config import InstanceControllerConfig
from app.daas.common.enums import BackendName
from app.daas.messaging.qmsg.hub_backend import QHubBackend, QHubConfigBackend
from app.qweb.service.service_context import QwebBackend


class MessagingBackend(QwebBackend):
    """Messaging backend"""

    cfg: QHubConfigBackend
    component: QHubBackend

    def __init__(
        self,
        cfg_main: InstanceControllerConfig,
        cfg_queue: QHubConfigBackend,
        cfg_ssh: SshAdapterConfig,
    ):
        self.cfg_main = cfg_main
        self.cfg_hub = cfg_queue
        self.cfg_ssh = cfg_ssh
        self.component = QHubBackend(self.cfg_hub)
        QwebBackend.__init__(
            self, name=BackendName.MESSAGING.value, component=self.component
        )

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects database adapter"""
        if self.component is not None:
            await self.component.start()
            return True
        return False

    async def disconnect(self) -> bool:
        """Disconnects database adapter"""
        if self.component is not None:
            await self.component.stop()
            self.connected = False
            return True
        return False
