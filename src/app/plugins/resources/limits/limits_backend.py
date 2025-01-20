"""Resource limit Backend"""

from app.daas.common.enums import BackendName
from app.qweb.service.service_context import QwebBackend
from app.daas.resources.limits.ressource_limits import (
    RessourceLimits,
    RessourceLimitsConfig,
)


class LimitBackend(QwebBackend):
    """Resource limit backend"""

    cfg: RessourceLimitsConfig
    component: RessourceLimits

    def __init__(self, cfg_limit: RessourceLimitsConfig):
        self.cfg_limit = cfg_limit
        self.component = RessourceLimits(self.cfg_limit)
        QwebBackend.__init__(
            self, name=BackendName.LIMITS.value, component=self.component
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
