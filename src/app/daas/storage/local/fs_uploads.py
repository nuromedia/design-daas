"""Baseclass for uploads in the filestore"""

import os
import shutil
from werkzeug.datastructures import FileStorage
from app.daas.storage.local.fs_config import FilestoreConfig
from app.daas.storage.local.fs_instances import FilestoreInstances


class FilestoreUploads(FilestoreInstances):
    """Baseclass for uploads in the filestore"""

    def __init__(self, config: FilestoreConfig):
        super().__init__(config)

    async def delete_user_file_upload(self, id_file: str, userid: int) -> bool:
        """Deletes specified file"""
        dstfolder = await self.get_user_folder_upload(userid)
        dstfile = f"{dstfolder}/{id_file}.file"
        if os.path.exists(dstfile):
            os.remove(dstfile)
        assert os.path.exists(dstfile) is False
        return True

    async def delete_user_file_shared(self, id_file: str, userid: int) -> bool:
        """Deletes specified shared file"""
        dstfolder = await self.get_user_folder_shared(userid)
        dstfile = f"{dstfolder}/{id_file}.file"
        if os.path.exists(dstfile):
            os.remove(dstfile)
        assert os.path.exists(dstfile) is False
        return True

    async def upload_user_file(
        self, received_file: FileStorage, folder: str, name: str, userid: int
    ) -> bool:
        result = False
        fullname = f"{folder}/{name}"
        if received_file is not None:
            self._log_info(f"Persisting {name} to {fullname}")
            await received_file.save(fullname)
            if os.path.exists(fullname):
                self._log_info(f"  0 -> Persisted {name} to {fullname}")
                result = True
            else:
                self._log_info(f" -1 -> Failed to persist {name} to {fullname}")

        return result

    async def upload_user_file_tmp(self, received_file, name: str, userid: int) -> bool:
        """
        Upload file to tmp folder
        """
        folder = await self.get_user_folder_tmp(userid)
        return await self.upload_user_file(received_file, folder, name, userid)

    async def upload_user_file_upload(
        self, received_file, name: str, userid: int
    ) -> bool:
        """
        Upload file to user folder
        """
        folder = await self.get_user_folder_upload(userid)
        return await self.upload_user_file(received_file, folder, name, userid)

    async def upload_user_file_shared(
        self, received_file, name: str, userid: int
    ) -> bool:
        """
        Upload file to shared folder
        """
        folder = await self.get_user_folder_shared(userid)
        return await self.upload_user_file(received_file, folder, name, userid)

    async def upload_user_file_docker(
        self, received_file, name: str, subdir: str, userid: int
    ) -> bool:
        """
        Upload file to tmp folder
        """
        folder = await self.get_user_folder_docker(userid, subdir)
        return await self.upload_user_file(received_file, folder, name, userid)

    async def upload_to_docker_folder(
        self, srcfile: str, name: str, subdir: str, userid: int
    ) -> bool:
        """
        Upload file to tmp folder
        """
        folder = await self.get_user_folder_docker(userid, subdir)
        if os.path.exists(srcfile):
            shutil.copyfile(srcfile, f"{folder}/{name}")
            return True
        return False
