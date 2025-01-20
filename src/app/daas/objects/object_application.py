"""Object for a virtualized app using Guacamole."""

from dataclasses import dataclass
from typing import Optional
from app.daas.db.db_mappings import ORMMappingType, ORMModelDomain
from app.qweb.common.qweb_tools import get_database
from app.qweb.logging.logging import LogTarget, Loggable
from app.daas.common.model import Application, File


@ORMModelDomain(ORMMappingType.Application)
@dataclass(kw_only=True)
class ApplicationObject(Application):
    """Object for a virtualized app using Guacamole."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Loggable.__init__(self, LogTarget.OBJECT)

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}"
            f"(id={self.id},name={self.id},"
            f"os_type={self.os_type})"
        )

    async def get_file(self) -> Optional[File]:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if self.id_file is not None:
            file = await dbase.get_file(self.id_file)
            if file is not None:
                return file
        return None

    async def change_owner(self, owner: int) -> bool:
        """Adjusts app to new owner"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        self.id_owner = owner
        await dbase.update_application(self)
        return True

    async def get_installer(self) -> str:
        if self.installer_type in ("os_install"):
            installer = f"apt install -y {self.installer} {self.installer_args}"
        elif self.installer_type in ("os_uninstall"):
            installer = f"apt remove -y {self.installer} {self.installer_args}"
        elif self.installer_type in ("exec_cmd", "exec_app", "exec_ssh"):

            prefix = ""
            if self.os_type not in ("win10", "win11"):
                prefix = f"chmod a+x {self.installer} ; "
            installer = f"{prefix} {self.installer} {self.installer_args}"
        else:
            installer = ""
        return installer
