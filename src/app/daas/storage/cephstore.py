"""Ceph-based Filestore to keep track of files"""

from app.daas.storage.ceph.ceph_actions import CephstoreActions
from app.daas.storage.ceph.ceph_config import CephstoreConfig


class Cephstore(CephstoreActions):
    """Ceph-based Filestore to keep track of files"""

    def __init__(self, config: CephstoreConfig):
        super().__init__(config)

    async def initialize(self) -> bool:
        """
        Initializes ceph-based filesystems locally
        """
        if self.config.enabled is False:
            self._log_info("Ceph Filesystem   : Disabled via config")
            return True
        mounted = await super().mount_ceph_folder()
        if mounted is not None:
            mount_dir = await self.get_ceph_folder()
            self._log_info(f"Ceph Filesystem   : Mounted to {mount_dir}")
            await self.generate_ceph_conf_linux()
            return True
        return False

    async def connect(self):
        """Connects the component"""
        self.connected = await self.initialize()
        return self.connected

    async def disconnect(self) -> bool:
        """Disconnects the component"""
        self.connected = False
        return True
