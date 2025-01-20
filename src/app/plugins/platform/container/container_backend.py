"""Container Backend"""

from app.daas.common.enums import BackendName
from app.daas.container.docker.DockerRequest import (
    DockerRequest,
    DockerRequestConfig,
    DockerServicesConfig,
)
from app.qweb.service.service_context import QwebBackend


class ContainerBackend(QwebBackend):
    """Container backend"""

    cfg: DockerRequestConfig
    component: DockerRequest

    def __init__(
        self, cfg_request: DockerRequestConfig, cfg_services: DockerServicesConfig
    ):
        self.cfg = cfg_request
        self.cfg_services = cfg_services
        self.component = DockerRequest(self.cfg, self.cfg_services)
        QwebBackend.__init__(
            self, name=BackendName.CONTAINER.value, component=self.component
        )

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects adapter"""
        if self.component is not None:
            self.connected = await self.component.connect()
            return self.connected
        return False

    async def disconnect(self) -> bool:
        """Disconnects adapter"""
        if self.component is not None:
            await self.component.disconnect()
            self.connected = self.component.connected
            return True
        return False
