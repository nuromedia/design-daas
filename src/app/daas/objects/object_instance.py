"""Instance Object"""

from dataclasses import dataclass
from typing import Optional
from app.daas.common.model import GuacamoleConnection
from app.daas.db.db_mappings import ORMMappingType, ORMModelDomain
from app.daas.objects.config_factory import get_empty_connection
from app.daas.objects.phase_instance import InstancePhase
from app.qweb.common.qweb_tools import get_database
from app.qweb.logging.logging import LogTarget, Loggable


@ORMModelDomain(ORMMappingType.Instance)
@dataclass(kw_only=True)
class InstanceObject(InstancePhase):
    """Instance Object"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Loggable.__init__(self, LogTarget.INST)

    def __repr__(self):
        return f"{self.__class__.__qualname__}" f"(id={self.id})"

    async def connect(
        self, contype: str, keep_connections: bool = False
    ) -> Optional[GuacamoleConnection]:
        """Connects the viewer"""
        await self.connect_prepare(keep_connections)
        contype = await self._get_contype_from_object_mode()
        con = await get_empty_connection(
            id_instance=self.id, contype=contype, hostname=self.host
        )
        await self._persist_connection(con)
        await self.connect_finalize(con)
        return con

    async def disconnect(self, force: bool) -> bool:
        """Disconnects the instance."""
        self._log_info(f"Disconnecting {self.id} (force={force})")
        return await self._delete_connection()

    async def connect_prepare(self, keep_connections: bool = False) -> bool:
        """Prepares object for a subsequent call 'connect'"""
        if self.id_con is not None:
            con = await self._get_db_connection()
            if con is not None and keep_connections is False:
                return await self._delete_connection()
            return True
        return False

    async def connect_finalize(self, con: GuacamoleConnection) -> bool:
        """Finalizes object after a prior call 'connect'"""
        self.id_con = con.id
        self.id_app = self.app.id
        self._log_info(f"Instance {self.id} connected ({con.protocol})")
        return await self.update()

    async def _get_db_connection(self) -> Optional[GuacamoleConnection]:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if self.id_con is not None:
            return await dbase.get_guacamole_connection(self.id_con)
        return None

    async def _delete_connection(self) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        return await dbase.delete_connection(self)

    async def _persist_connection(self, con: GuacamoleConnection) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        return await dbase.create_guacamole_connection(con)

    async def update(self) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        return await dbase.update_instance(self)
