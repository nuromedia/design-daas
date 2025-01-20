"""Baseclass for filestore"""

import os
import uuid
from app.daas.storage.local.fs_config import FilestoreConfig
from app.qweb.common.qweb_tools import get_database
from app.qweb.logging.logging import LogTarget, Loggable


class FilestoreBase(Loggable):
    """Baseclass for filestore"""

    def __init__(self, config: FilestoreConfig):
        Loggable.__init__(self, LogTarget.FILES_LOCAL)
        self.dbase = None
        self.config = config

    async def initialize_filesystem(self) -> bool:
        """Create intial folders"""
        await self.__ensure_required_folder(self.config.folder_tmp)
        await self.__ensure_required_folder(self.config.folder_upload)
        await self.__ensure_required_folder(self.config.folder_shared)
        await self.__ensure_required_folder(self.config.folder_docker)
        return True

    async def initialize_database(self) -> bool:
        from app.daas.db.database import Database

        self.dbase = await get_database(Database)
        return self.dbase is not None

    async def get_base_folder_endpoint_info(self) -> str:
        """Returns configured endpoint_info folder (absolute)"""
        folder = os.path.abspath(self.config.folder_endpoint_info)
        await self.__ensure_required_folder(folder)
        return folder

    async def get_filesize(self, file: str):
        """Returns size of file in bytes"""
        file_stats = os.stat(file)
        return file_stats.st_size

    async def get_base_randfile_tmp(self) -> str:
        """Creates unique filename in tmp folder"""
        unique_name = uuid.uuid4().hex
        folder = await self.get_base_folder_tmp()
        absfile = f"{folder}/{unique_name}"
        assert os.path.exists(absfile) is False
        return absfile

    async def get_base_randfile_upload(self) -> str:
        """Creates unique filename in upload folder"""
        unique_name = uuid.uuid4().hex
        folder = await self.get_base_folder_upload()
        absfile = f"{folder}/{unique_name}"
        assert os.path.exists(absfile) is False
        return absfile

    async def get_user_randfile_tmp(self, userid: int) -> str:
        """Creates unique filename in tmp folder"""
        unique_name = uuid.uuid4().hex
        folder = await self.get_user_folder_tmp(userid)
        absfile = f"{folder}/{unique_name}"
        assert os.path.exists(absfile) is False
        return absfile

    async def get_user_randfile_upload(self, userid: int) -> str:
        """Creates unique filename in upload folder"""
        unique_name = uuid.uuid4().hex
        folder = await self.get_user_folder_upload(userid)
        absfile = f"{folder}/{unique_name}"
        assert os.path.exists(absfile) is False
        return absfile

    async def get_user_file_tmp(self, name: str, userid: int) -> str:
        """Returns absolute filename in tmp folder"""
        folder = await self.get_user_folder_tmp(userid)
        absfile = f"{folder}/{name}"
        assert os.path.exists(absfile)
        return absfile

    async def get_user_file_upload(self, name: str, userid: int) -> str:
        """Returns asbsolute filename in upload folder"""
        folder = await self.get_user_folder_upload(userid)
        absfile = f"{folder}/{name}"
        assert os.path.exists(absfile)
        return absfile

    async def get_user_file_shared(self, name: str, userid: int) -> str:
        """Returns asbsolute filename in shared user folder"""
        folder = await self.get_user_folder_shared(userid)
        absfile = f"{folder}/{name}"
        assert os.path.exists(absfile)
        return absfile

    async def get_user_file_docker(self, name: str, userid: int, env: str = "") -> str:
        """Returns asbsolute filename in upload folder"""
        folder = await self.get_user_folder_docker(userid, name)
        absfile = f"{folder}/Dockerfile"
        if env != "":
            absfile = f"{absfile}.{env}"
        assert os.path.exists(absfile)
        return absfile

    async def get_user_folder_tmp(self, userid: int) -> str:
        """Returns configured user folder (tmp)"""
        folder = await self.get_base_folder_tmp()
        userfolder = f"{folder}/{userid}"
        await self.__ensure_required_folder(userfolder)
        return userfolder

    async def get_user_folder_upload(self, userid: int) -> str:
        """Returns configured user folder (upload)"""
        folder = await self.get_base_folder_upload()
        userfolder = f"{folder}/{userid}"
        await self.__ensure_required_folder(userfolder)
        return userfolder

    async def get_user_folder_shared(self, userid: int) -> str:
        """Returns configured shared user folder (upload)"""
        folder = await self.get_base_folder_shared()
        sharedfolder = f"{folder}/{userid}"
        await self.__ensure_required_folder(sharedfolder)
        return sharedfolder

    async def get_user_folder_docker(self, userid: int, subdir: str = "") -> str:
        """Returns configured user folder (docker)"""
        folder = await self.get_base_folder_docker()
        userfolder = f"{folder}/{userid}"
        if subdir != "":
            userfolder = f"{folder}/{userid}/{subdir}"
        await self.__ensure_required_folder(userfolder)
        return userfolder

    async def get_base_folder_tmp(self) -> str:
        """Returns configured tmp folder (absolute)"""
        folder = os.path.abspath(self.config.folder_tmp)
        await self.__ensure_required_folder(folder)
        return folder

    async def get_base_folder_upload(self) -> str:
        """Returns configured upload folder (absolute)"""
        folder = os.path.abspath(self.config.folder_upload)
        await self.__ensure_required_folder(folder)
        return folder

    async def get_base_folder_shared(self) -> str:
        """Returns configured shared folder (absolute)"""
        folder = os.path.abspath(self.config.folder_shared)
        await self.__ensure_required_folder(folder)
        return folder

    async def get_base_folder_docker(self) -> str:
        """Returns configured docker folder (absolute)"""
        folder = os.path.abspath(self.config.folder_docker)
        await self.__ensure_required_folder(folder)
        return folder

    async def __ensure_required_folder(self, folder: str):
        if os.path.exists(folder) is False:
            os.makedirs(folder)
        assert os.path.exists(folder)
