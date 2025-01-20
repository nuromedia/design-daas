"""Baseclass for docker filestore"""

import os
import shutil
from app.daas.common.model import File
from app.daas.storage.local.fs_config import FilestoreConfig
from app.daas.storage.local.fs_uploads import FilestoreUploads


class FilestoreDocker(FilestoreUploads):
    """Baseclass for docker filestore"""

    def __init__(self, config: FilestoreConfig):
        super().__init__(config)

    async def get_root_dockerfile(self, imagename: str) -> str:
        """
        Returns path of specified root image
        """
        dockerfile = ""
        if imagename == self.config.default_wine_image_name:
            dockerfile = f"{self.config.default_wine_image_folder}/Dockerfile"
        if imagename == self.config.default_x11vnc_image_name:
            dockerfile = f"{self.config.default_x11vnc_image_folder}/Dockerfile"
        assert os.path.exists(dockerfile)
        return dockerfile

    async def create_docker_envfile(
        self,
        objid: str,
        userid: int,
        imgname: str,
        envname: str,
        files: list[File] = [],
        installers: list[str] = [],
    ) -> str:
        """Copies specified Dockerfile into new environmental dockerfile"""
        assert self.dbase is not None
        result = ""
        obj = await self.dbase.get_daas_object(objid)
        if obj is None:
            return ""
        dstfolder = await self.get_user_folder_docker(userid, imgname)
        dstfile = f"{dstfolder}/Dockerfile.{envname}"
        with open(dstfile, "w", encoding="UTF-8") as file:
            file.write(f"FROM daas.{imgname}\n")
            if len(files) > 0:
                file.write("\n# COPY FILES\n")
                for fileobj in files:
                    file.write(
                        f"COPY {fileobj.name} {fileobj.remotepath}/{fileobj.name}\n"
                    )
            if len(installers) > 0:
                file.write("\n# RUN INSTALLERS\n")
                for installer in installers:
                    file.write(f"RUN {installer}\n")

        result = dstfile
        assert os.path.exists(result)
        return result

    async def update_docker_envfile(
        self,
        objid: str,
        userid: int,
        imgname: str,
        envname: str,
        files: list[File] = [],
        installers: list[str] = [],
    ) -> str:
        """Copies specified Dockerfile into new environmental dockerfile"""
        assert self.dbase is not None
        result = ""
        obj = await self.dbase.get_daas_object(objid)
        if obj is None:
            return ""
        dstfolder = await self.get_user_folder_docker(userid, imgname)
        dstfile = f"{dstfolder}/Dockerfile.{envname}"
        with open(dstfile, "r", encoding="UTF-8") as dockerfile:
            lines = dockerfile.readlines()

        for fileobj in files:
            newline = f"COPY {fileobj.name} {fileobj.remotepath}/{fileobj.name}\n"
            if newline not in lines:
                lines.append(newline)

        for installer in installers:
            newline = f"RUN {installer}\n"
            if newline not in lines:
                lines.append(newline)

        with open(dstfile, "w", encoding="UTF-8") as dockerfile:
            lines = dockerfile.writelines(lines)

        result = dstfile
        assert os.path.exists(result)
        return result

    async def upload_user_envfile_docker(
        self,
        received_file,
        name: str,
        subdir: str,
        userid: int,
        files: list[File] = [],
        installers: list[str] = [],
    ) -> str:
        """
        Upload file to tmp folder
        """
        folder = await self.get_user_folder_docker(userid, subdir)
        await self.upload_user_file(received_file, folder, f"Dockerfile.{name}", userid)
        dockerfile = await self.get_user_file_docker(subdir, userid, name)

        # Read the Dockerfile content
        await self.update_from_tag(dockerfile, subdir, userid, name)
        with open(dockerfile, "a", encoding="UTF-8") as file:
            if len(files) > 0:
                file.write("# COPY INSTALLERS\n")
                for fileobj in files:
                    file.write(
                        f"COPY {fileobj.name} {fileobj.remotepath}/{fileobj.name}\n"
                    )
            if len(installers) > 0:
                file.write("# RUN INSTALLERS\n")
                for installer in installers:
                    file.write(f"RUN {installer}\n")
        if len(files) > 0:
            for file in files:
                self._log_info(f"FILE: {file}")
        return dockerfile

    async def update_from_tag(
        self, dockerfile: str, subdir: str, userid: int, name: str
    ):
        """Updates from tag in dockerfile"""
        with open(dockerfile, "r", encoding="UTF-8") as file:
            dockerfile_content = file.read()
        lines = dockerfile_content.splitlines()
        new_dockerfile_content = []
        found_from_line = False
        subdir_lower = subdir.lower()
        newname = f"daas.{subdir_lower}"
        # if subdir != "":
        #     newname = f"daas-{userid}-{name}-{subdir}"
        for line in lines:
            if line.strip().startswith("FROM"):
                new_dockerfile_content.append(f"FROM {newname}\n")
                found_from_line = True
            else:
                new_dockerfile_content.append(line)
        if found_from_line:
            with open(dockerfile, "w", encoding="UTF-8") as file:
                file.write("\n".join(new_dockerfile_content))
        self._log_info(f"Updated FROM tag for {name} (owner={userid})")

    async def get_docker_envfile(self, userid: int, imgname: str, envname: str) -> str:
        """
        Returns path to environmental dockerfile
        """

        dstfolder = await self.get_user_folder_docker(userid, imgname)
        return f"{dstfolder}/Dockerfile.{envname}"

    async def delete_docker_envfile(
        self, id: str, userid: int, imgname: str, envname: str
    ) -> str:
        """Deletes specified envfile"""
        assert self.dbase is not None
        result = ""
        obj = await self.dbase.get_daas_object(id)
        if obj is None:
            return ""
        dstfolder = await self.get_user_folder_docker(userid, imgname)
        dstfile = f"{dstfolder}/Dockerfile.{envname}"
        if os.path.exists(dstfile):
            os.remove(dstfile)
        assert os.path.exists(result) is False
        return result

    async def copy_root_dockerfile(
        self, imagename: str, userid: int, subdir: str
    ) -> str:
        """
        Copies specified root image
        """
        # dockerfolder = ""
        # if imagename == self.config.default_wine_image_name:
        #     dockerfolder = f"{self.config.default_wine_image_folder}"
        # if imagename == self.config.default_x11vnc_image_name:
        #     dockerfolder = f"{self.config.default_x11vnc_image_folder}"
        dstfolder = await self.get_user_folder_docker(userid, subdir)

        # Copy as template
        with open(f"{dstfolder}/Dockerfile", "w", encoding="UTF-8") as file:
            file.write(f"FROM {imagename}\n")
        # copy folder
        # shutil.copytree(dockerfolder, dstfolder, dirs_exist_ok=True)

        assert os.path.exists(dstfolder)
        result = f"{dstfolder}/Dockerfile"
        assert os.path.exists(result)
        return result

    async def copy_user_dockerfile(
        self, dockerfile: str, userid: int, subdir: str
    ) -> str:
        """
        Copies specified dockerfile
        """
        dockerfolder = ""
        if os.path.exists(dockerfile) is False:
            return ""

        dockerfolder = os.path.dirname(dockerfile)
        dstfolder = await self.get_user_folder_docker(userid, subdir)

        if dockerfolder == dstfolder:
            shutil.copy(dockerfile, dstfolder)
        else:
            shutil.copytree(dockerfolder, dstfolder, dirs_exist_ok=True)

        assert os.path.exists(dstfolder)
        result = f"{dstfolder}/Dockerfile"
        assert os.path.exists(result)
        return result

    async def copy_user_dockerfile_env(
        self, dockerfile: str, userid: int, name: str, subdir: str
    ) -> str:
        """
        Copies specified dockerfile
        """
        dockerfolder = ""
        if os.path.exists(dockerfile) is False:
            return ""

        dockerfolder = os.path.dirname(dockerfile)
        dstfolder = await self.get_user_folder_docker(userid, subdir)
        dstfile = f"{dstfolder}/Dockerfile"
        if name != "":
            dstfile = f"{dstfolder}/Dockerfile.{name}"
        if dockerfolder == dstfolder:
            shutil.copy(dockerfile, dstfile)
        else:
            shutil.copytree(dockerfolder, dstfolder, dirs_exist_ok=True)

        assert os.path.exists(dstfile)
        return dstfile

    async def delete_user_folder_docker(self, userid: int, subdir: str) -> bool:
        """
        Deletes specified image
        """
        folder = await self.get_user_folder_docker(userid, subdir)
        shutil.rmtree(folder)

        assert os.path.exists(folder) is False
        return True
