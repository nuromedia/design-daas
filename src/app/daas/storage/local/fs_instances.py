""" Baseclass for instance filestore"""

import os
from app.daas.common.model import File, Instance
from app.daas.storage.local.fs_permissions import FilestorePermissions
from app.daas.storage.local.fs_config import FilestoreConfig
from app.qweb.common.qweb_tools import get_database

CMD_LINUX_CHMOD = "/usr/bin/chmod"
CMD_LINUX_XTERM = "/usr/bin/xterm"
CMD_LINUX_MKDIR = "mkdir"
CMD_LINUX_READFILE = "cat"
CMD_WIN_CMD = "cmd.exe"
CMD_WIN_MKDIR = "/c mkdir -p"
CMD_WIN_READFILE = "type"


class FilestoreInstances(FilestorePermissions):
    """Baseclass for instance filestore"""

    def __init__(self, config: FilestoreConfig):
        super().__init__(config)

    async def read_inst_file_status(
        self, adr: str, windows: bool, os_username: str
    ) -> tuple:
        """Read results from cmdline invocations"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        instance = await dbase.get_instance_by_adr(adr)
        cmd = CMD_WIN_READFILE
        if instance is not None:
            if windows is False:
                cmd = CMD_LINUX_READFILE
            statusfile = await self.get_inst_file_status(os_username, windows, False)
            ret = await instance.inst_vminvoke_ssh(cmd=cmd, args=f"{statusfile}")
            if ret is not None and ret.response_code == 200:
                return 0, ret.sys_log, ""
        return 1, "", "No instance"

    async def upload_file_to_instance(self, file: File, instance: Instance) -> bool:
        """Upload file to tmp folder"""
        srcfile = file.localpath
        dstfile = file.remotepath

        windows = False
        if instance.app.os_type in ("win10", "win11"):
            windows = True
        return await self.__upload_inst_file(
            adr=instance.host,
            filename=srcfile,
            folder=dstfile,
            windows=windows,
            remote_name=file.name,
        )

    async def upload_inst_file_upload(
        self, adr: str, filename: str, os_username: str, windows: bool
    ):
        """Uploads file to upload folder"""
        folder = await self.get_inst_folder_upload(adr, os_username, windows, True)
        return self.__upload_inst_file(adr, filename, folder, windows)

    async def upload_inst_file_tmp(
        self,
        adr: str,
        filename: str,
        os_username: str,
        windows: bool,
    ) -> bool:
        """Uploads file to tmp folder"""
        folder = await self.get_inst_folder_tmp(adr, os_username, windows, True)
        return await self.__upload_inst_file(adr, filename, folder, windows)

    # pylint: disable=too-many-arguments
    async def execute_inst_file_tmp(
        self,
        adr: str,
        name: str,
        os_username: str,
        os_password: str,
        windows: bool,
    ) -> int:
        """Executes file from tmp folder"""
        folder = await self.get_inst_folder_tmp(adr, os_username, windows, True)
        filename = f"{folder}/{name}"
        if windows:
            filename = f"C:\\Users\\{os_username}\\{folder}\\{name}"

        return await self.__execute_inst_file(
            adr, filename, os_username, os_password, windows
        )

    async def get_inst_folder_daas(
        self, adr: str, os_username: str, windows: bool, relative: bool
    ) -> str:
        """Returns configured daas folder"""
        folder = await self.__get_inst_folder_daas(os_username, windows, relative)
        assert await self.__ensure_inst_folder(adr, windows, folder)
        return folder

    async def get_inst_folder_env(
        self, adr: str, os_username: str, windows: bool, relative: bool
    ) -> str:
        """Returns configured env folder"""
        folder = await self.__get_inst_folder_env(os_username, windows, relative)
        assert await self.__ensure_inst_folder(adr, windows, folder)
        return folder

    async def get_inst_folder_status(
        self, adr: str, os_username: str, windows: bool, relative: bool
    ) -> str:
        """Returns configured status folder"""
        folder = await self.__get_inst_folder_status(os_username, windows, relative)
        assert await self.__ensure_inst_folder(adr, windows, folder)
        return folder

    async def get_inst_folder_tmp(
        self, adr: str, os_username: str, windows: bool, relative: bool
    ) -> str:
        """Returns configured tmp folder"""
        folder = await self.__get_inst_folder_tmp(os_username, windows, relative)
        assert await self.__ensure_inst_folder(adr, windows, folder)
        return folder

    async def get_inst_folder_upload(
        self, adr: str, os_username: str, windows: bool, relative: bool
    ) -> str:
        """Returns configured upload folder"""
        folder = await self.__get_inst_folder_upload(os_username, windows, relative)
        assert await self.__ensure_inst_folder(adr, windows, folder)
        return folder

    async def get_inst_file_status(
        self, os_username: str, windows: bool, relative: bool
    ) -> str:
        """
        Returns absolute filename within instance
        """
        name = self.config.instance_status_outfile_name
        folder = await self.__get_inst_folder_status(os_username, windows, relative)
        return await self.__get_inst_file(name, folder, windows)

    async def get_inst_file_tmp(
        self, name: str, os_username: str, windows: bool, relative: bool
    ) -> str:
        """
        Returns absolute filename within instance
        """
        folder = await self.__get_inst_folder_tmp(os_username, windows, relative)
        return await self.__get_inst_file(name, folder, windows)

    async def get_inst_file_upload(
        self, name: str, os_username: str, windows: bool, relative: bool
    ) -> str:
        """
        Returns absolute filename within instance
        """
        folder = await self.__get_inst_folder_upload(os_username, windows, relative)
        return await self.__get_inst_file(name, folder, windows)

    async def __get_inst_folder_daas(
        self, os_username: str, windows: bool, relative: bool
    ) -> str:
        if relative:
            return "daas"
        if windows:
            return f"C:\\Users\\{os_username}\\daas"
        if os_username == "root":
            return f"/{os_username}/daas"
        return f"/home/{os_username}/daas"

    async def __get_inst_folder_env(
        self, os_username: str, windows: bool, relative: bool
    ) -> str:
        daas_folder = await self.__get_inst_folder_daas(os_username, windows, relative)
        folder = f"{daas_folder}/{self.config.folder_inst_env}"
        if windows:
            folder = f"{daas_folder}\\{self.config.folder_inst_env}"
        return folder

    async def __get_inst_folder_status(
        self, os_username: str, windows: bool, relative: bool
    ) -> str:
        daas_folder = await self.__get_inst_folder_daas(os_username, windows, relative)
        folder = f"{daas_folder}/{self.config.folder_inst_status}"
        if windows:
            folder = f"{daas_folder}\\{self.config.folder_inst_status}"
        return folder

    async def __get_inst_folder_tmp(
        self, os_username: str, windows: bool, relative: bool
    ) -> str:
        daas_folder = await self.__get_inst_folder_daas(os_username, windows, relative)
        if windows:
            suffix = self.config.folder_tmp.replace("/", "\\")
            return f"{daas_folder}\\{suffix}"
        return f"{daas_folder}/{self.config.folder_tmp}"

    async def __get_inst_folder_upload(
        self, os_username: str, windows: bool, relative: bool
    ) -> str:
        daas_folder = await self.__get_inst_folder_daas(os_username, windows, relative)
        if windows:
            suffix = self.config.folder_upload.replace("/", "\\")
            return f"{daas_folder}\\{suffix}"
        return f"{daas_folder}/{self.config.folder_upload}"

    async def __ensure_inst_folder(self, adr: str, windows: bool, folder: str) -> bool:
        """Creates a remote folder"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)

        result = False
        instance = await dbase.get_instance_by_adr(adr)
        if instance is not None:
            cmd = CMD_LINUX_MKDIR
            args = f"-p {folder}"
            if windows:
                cmd = CMD_WIN_CMD
                args = f'{CMD_WIN_MKDIR} "{folder}"'
            ret = await instance.inst_vminvoke_ssh(cmd, args)
            if ret is not None and ret.response_code == 200:
                result = True
        return result

    async def __execute_inst_file(
        self,
        adr: str,
        filename: str,
        os_username: str,
        os_password: str,
        windows: bool,
    ) -> int:
        """
        Executes file within instance
        """
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        ret = None
        instance = await dbase.get_instance_by_adr(adr)
        prefix = ""
        if instance is not None:
            if windows:
                prefix = await self.__get_windows_prefix_pstools(
                    os_username, os_password
                )
                ret = await instance.inst_vminvoke_app(f"{prefix} {filename}", "")
            else:
                ret = await instance.inst_vminvoke_ssh(
                    CMD_LINUX_CHMOD, f"a+x {filename}"
                )
                if ret is not None and ret.response_code == 200:
                    ret = await instance.inst_vminvoke_app(
                        CMD_LINUX_XTERM, f"-e {filename}"
                    )
        if ret is not None and ret.response_code == 200:
            return 0
        return -1

    async def __get_inst_file(
        self,
        name: str,
        folder: str,
        windows: bool,
    ) -> str:
        """
        Returns absolute filename within instance
        """
        if windows:
            return f"{folder}\\{name}"
        return f"{folder}/{name}"

    async def get_filename_instance(
        self, filename: str, windows: bool, remote_name: str = ""
    ) -> str:
        result = ""
        DEFAULT_INST_PATH_WIN = "C:/Users/root/daas"
        DEFAULT_INST_PATH_LINUX = "/root/daas"
        folder = DEFAULT_INST_PATH_LINUX
        if windows:
            folder = DEFAULT_INST_PATH_WIN

        name = os.path.basename(filename)
        result = f"{folder}/{name}"
        if remote_name != "":
            result = f"{folder}/{remote_name}/{name}"
        return result

    async def __upload_inst_file(
        self, adr: str, filename: str, folder: str, windows: bool, remote_name: str = ""
    ) -> bool:
        """
        Upload file to instance
        """
        from app.daas.db.database import Database

        dbase = await get_database(Database)

        result = False
        instance = await dbase.get_instance_by_adr(adr)

        if instance is not None:
            if os.path.exists(filename) is False:
                return False
            name = os.path.basename(filename)
            norm_folder = f"{folder}/{name}"
            if remote_name != "":
                norm_folder = f"{folder}/{remote_name}"
            if windows:
                if remote_name != "":
                    norm_folder = f"{folder}/{remote_name}"
                else:
                    norm_folder = f"{folder}/{name}"
            ret = await instance.inst_vminvoke_upload(
                filename, instance.app.os_type in ("win10", "win11"), False
            )
            if ret is not None and ret.response_code == 200:
                result = True
        return result

    async def __get_windows_prefix_pstools(
        self,
        os_username: str,
        os_password: str,
    ):
        prefix_cmd = f"C:/Users/{os_username}/daas/env/pstools/psexec.exe"
        prefix_accept = "-nobanner -accepteula"
        prefix_session = "-i 1"
        prefix_creds = f"-u {os_username} -p {os_password}"
        return f"{prefix_cmd} {prefix_accept} {prefix_session} {prefix_creds}"
