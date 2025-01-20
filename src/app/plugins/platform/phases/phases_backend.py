"""Phases Backend"""

from app.daas.common.enums import BackendName
from app.qweb.service.service_context import QwebBackend


class PhasesBackend(QwebBackend):
    """Phases backend"""

    component: dict

    def __init__(self):
        self.component = {}
        QwebBackend.__init__(
            self, name=BackendName.PHASES.value, component=self.component
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
            self.connected = True
            return self.connected
        return False

    async def disconnect(self) -> bool:
        """Disconnects adapter"""
        if self.component is not None:
            self.connected = False
            return True
        return False
