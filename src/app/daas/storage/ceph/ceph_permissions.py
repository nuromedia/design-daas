"""Baseclass for ceph permissions"""

import os
from app.daas.storage.ceph.ceph_base import CephstoreBase
from app.daas.storage.ceph.ceph_config import CephstoreConfig

# Globals
CMD_LINUX_CEPH = "/usr/bin/ceph"
CMD_LINUX_MOUNT = "/usr/bin/mount"
CMD_LINUX_UMOUNT = "/usr/bin/umount"


class CephstorePermissions(CephstoreBase):
    """Baseclass for ceph permissions"""

    def __init__(self, config: CephstoreConfig):
        super().__init__(config)

    async def grant_access(
        self,
        fsname: str,
        userid: int,
        caps: list[str],
    ) -> bool:
        """
        Grants access to ceph fs
        """
        # Check params
        if await self.__check_params_grant(fsname, userid) is False:
            return False
        secretpath = await self.__get_keyring_file(userid)
        auth_cmd = [CMD_LINUX_CEPH, "fs", "authorize", fsname, f"client.{userid}"]
        auth_cmd.extend(caps)
        code, credentials, str_err = await self.__run_cmd(auth_cmd)
        if code != 0:
            self._log_error(f"Error on ceph authorize: {credentials} {str_err}")
            return False
        await self.__write_keyring(secretpath, credentials)
        return True

    async def revoke_access(self, fsname: str, userid: int) -> bool:
        """
        Revokes access from ceph fs
        """
        # Check params
        if await self.__check_params_grant(fsname, userid) is False:
            return False
        keydir = self.config.daasfs.folder_keyrings
        secretpath = f"{keydir}/ceph.client.{userid}.keyring"
        auth_cmd = [CMD_LINUX_CEPH, "auth", "del", f"client.{userid}"]
        code, _, _ = await self.__run_cmd(auth_cmd)
        if code != 0:
            self._log_error(f"Exception on ceph auth: {auth_cmd}")
            return False
        if os.path.exists(secretpath):
            os.remove(secretpath)
        return True

    async def __get_keyring_file(self, userid: int) -> str:
        keydir = await self.get_ceph_folder_keyrings()
        return f"{keydir}/ceph.client.{userid}.keyring"

    async def __check_params_grant(self, fsname: str, userid: int) -> bool:
        if userid >= 0:
            if fsname != "":
                return True
        return False

    async def __write_keyring(self, filename: str, content: str):
        with open(
            filename,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(content)
