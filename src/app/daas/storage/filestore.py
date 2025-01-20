"""Filestore component to manage local and remote file access"""

from app.daas.storage.local.fs_config import FilestoreConfig
from app.daas.storage.local.fs_docker import FilestoreDocker


class Filestore(FilestoreDocker):
    """Filestore to keep track of files"""

    def __init__(self, config: FilestoreConfig):

        super().__init__(config)

    async def initialize(self) -> bool:
        """Create intial folders"""
        init_db = await self.initialize_database()
        init_fs = await self.initialize_filesystem()
        init_perm = await self.initialize_permissions()
        success = init_fs and init_perm and init_db
        if success is False:
            self._log_error("Filestore NOT initialized")
        return success

    async def connect(self):
        """Connects the component"""
        self.connected = await self.initialize()
        return self.connected

    async def disconnect(self) -> bool:
        """Disconnects the component"""
        self.connected = False
        return True
