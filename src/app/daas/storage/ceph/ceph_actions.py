"""Baseclass for ceph filestore providing ceph interaction"""

import os
from app.daas.storage.ceph.ceph_permissions import CephstorePermissions
from app.daas.storage.ceph.ceph_config import CephstoreConfig

FOLDER_KEYRING_LINUX = "/etc/ceph"
FOLDER_KEYRING_WINDOWS = "C:/ProgramData/ceph/keyring"
FILE_CONF_CEPH_LINUX = "/etc/ceph/ceph.conf"
FILE_CONF_CEPH_WINDOWS = "C:/ProgramData/ceph/ceph.conf"


class CephstoreActions(CephstorePermissions):
    """Baseclass for ceph filestore providing ceph interaction"""

    def __init__(self, config: CephstoreConfig):
        super().__init__(config)

    async def mount_inst(
        self, adr: str, userid: int, target: str, windows: bool
    ) -> tuple[int, str, str]:
        """Mount folder within instance"""
        mapping = await self.__get_folder_mapping(target)
        if mapping is None:
            return 1, "", "CephDirectoryMapping not found"
        src = mapping.src
        dst = mapping.dst_win if windows else mapping.dst_linux
        if target == "user":
            src = f"{src}/{userid}"
        filesystem = self.config.daasfs.name
        args = [f"client.{userid}", src, dst, filesystem]
        return await self.__fs_command(adr, "mount", args, windows)

    async def unmount_inst(
        self, adr: str, target: str, windows: bool
    ) -> tuple[int, str, str]:
        """Unmount folder within instance"""
        mapping = await self.__get_folder_mapping(target)
        if mapping is None:
            return 1, "", "CephDirectoryMapping not found"
        args = [mapping.dst_win if windows else mapping.dst_linux]
        return await self.__fs_command(adr, "unmount", args, windows)

    async def copy_ceph_config(
        self, adr: str, userid: int, windows: bool
    ) -> tuple[int, str, str]:
        """Copies ceph config to instance"""
        fsname = self.config.daasfs.name
        keydir = self.config.daasfs.folder_keyrings
        cfgfile = f"{keydir}/{fsname}/ceph.conf"
        dstfile = FILE_CONF_CEPH_LINUX
        if windows:
            dstfile = FILE_CONF_CEPH_WINDOWS
            cfgfile = f"{keydir}/{fsname}/ceph_windows_{userid}.conf"
        await self.__ensure_config_local(userid, cfgfile, windows)
        return await self.__fs_upload(adr, cfgfile, dstfile)

    async def copy_ceph_keyring(
        self, adr: str, userid: int, windows: bool
    ) -> tuple[int, str, str]:
        """Copies ceph config to instance"""
        secretpath = await self.__ensure_keyring_local(userid)
        if os.path.exists(secretpath):
            filename = f"ceph.client.{userid}.keyring"
            dstfile = f"{FOLDER_KEYRING_LINUX}/{filename}"
            if windows:
                dstfile = FOLDER_KEYRING_WINDOWS
            return await self.__ensure_keyring_remote(adr, userid, secretpath, dstfile)
        return 1, "", "Ceph Keyring is not present"

    async def __ensure_keyring_remote(
        self, adr: str, userid: int, secretpath: str, dstfile: str
    ) -> tuple[int, str, str]:
        if os.path.exists(secretpath):
            userdir = await self._get_local_user_folder(userid)
            if userdir != "":
                return await self.__fs_upload(adr, secretpath, dstfile)
            self._log_error(f"Userdirectory not available for {userid}")
        msg = "Secretpath does not exist"
        self._log_error(msg)
        return 1, "", msg

    async def __ensure_keyring_local(self, userid: int) -> str:
        keydir = await self.get_ceph_folder_keyrings()
        secretpath = f"{keydir}/ceph.client.{userid}.keyring"
        if os.path.exists(secretpath) is False:
            name = self.config.daasfs.name
            cmd = ["/public", "r", "/shared", "rw", f"/user/{userid}", "rw"]
            await self.grant_access(name, userid, cmd)
        return secretpath

    async def __ensure_config_local(self, userid: int, cfgfile: str, windows: bool):
        if os.path.exists(cfgfile) is False:
            if windows:
                await self.generate_ceph_conf_windows(userid)
            else:
                await self.generate_ceph_conf_linux()

    async def __fs_upload(
        self, adr: str, cfgfile: str, dstfile: str
    ) -> tuple[int, str, str]:
        # from daas_web.common.request_context import get_context
        #
        # ctx = get_context()
        # dbase = await ctx.get_database()
        # instance = await dbase.get_instance_by_adr(adr)
        # if instance is not None:
        #     return await instance.inst_vminvoke_upload(adr, cfgfile, dstfile)
        return 1, "", "No instance"

    async def __fs_command(
        self, adr: str, cmd: str, args: list, windows: bool
    ) -> tuple[int, str, str]:
        # from daas_web.common.request_context import get_context
        #
        # ctx = get_context()
        # dbase = await ctx.get_database()
        # instance = await dbase.get_instance_by_adr(adr)
        # if instance is not None:
        #     return await instance.inst_vminvoke_fs(adr, cmd, args, windows)
        return 1, "", "No instance"
