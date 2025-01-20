"""Info Backend"""

from app.daas.common.enums import BackendName
from app.daas.resources.info.config import SysteminfoConfig
from app.daas.resources.info.sysinfo import Systeminfo
from app.qweb.service.service_context import QwebBackend


class InfoBackend(QwebBackend):
    """Info backend"""

    component: Systeminfo

    def __init__(self, cfg: SysteminfoConfig):
        self.cfg = cfg
        self.component = Systeminfo(cfg)
        QwebBackend.__init__(
            self, name=BackendName.INFO.value, component=self.component
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
            await self.component.initialize()
            return True
        return False

    async def disconnect(self) -> bool:
        """Disconnects database adapter"""
        if self.component is not None:
            self.connected = False
            return True
        return False
