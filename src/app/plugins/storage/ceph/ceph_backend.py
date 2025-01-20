"""Ceph Backend"""

from app.daas.common.enums import BackendName
from app.daas.storage.ceph.ceph_config import CephstoreConfig
from app.daas.storage.cephstore import Cephstore
from app.qweb.service.service_context import QwebBackend


class CephBackend(QwebBackend):
    """Ceph backend"""

    cfg_storage: CephstoreConfig
    component: Cephstore

    def __init__(self, cfg_storage: CephstoreConfig):
        self.cfg_storage = cfg_storage
        self.component = Cephstore(self.cfg_storage)
        QwebBackend.__init__(
            self, name=BackendName.CEPH.value, component=self.component
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
