"""Admin Backend"""

from app.daas.common.enums import BackendName
from app.qweb.service.service_context import QwebBackend


class AdminBackend(QwebBackend):
    """Admin backend"""

    component: list = []

    def __init__(self):
        QwebBackend.__init__(
            self, name=BackendName.ADMIN.value, component=self.component
        )

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects database adapter"""
        self.connected = True
        return True

    async def disconnect(self) -> bool:
        """Disconnects database adapter"""
        self.connected = False
        return True
