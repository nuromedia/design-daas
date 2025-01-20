"""DB Backend"""

from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.db.db_manager import DatabaseManager
from app.qweb.service.service_context import QwebBackend
from app.daas.common.config import DatabaseConfig


# pylint: disable=too-few-public-methods
class DatabaseBackend(QwebBackend):
    """Database backend"""

    cfg: DatabaseConfig
    component: DatabaseManager
    # repos: Optional[Database] = None

    def __init__(self, cfg: DatabaseConfig):
        self.cfg = cfg
        # self.repos = None
        self.component = DatabaseManager(cfg)
        QwebBackend.__init__(self, name=BackendName.DB.value, component=self.component)

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects database adapter"""
        if self.component is not None:
            self.connected = await self.component.connect()
            return self.connected
        return False

    async def disconnect(self) -> bool:
        """Disconnects database adapter"""
        if self.component is not None:
            await self.component.disconnect()
            self.connected = self.component.connected
            return True
        return False
