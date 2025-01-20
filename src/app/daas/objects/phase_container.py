"""Baseclass for a containerized object using Guacamole."""

import os
from dataclasses import dataclass
from app.daas.common.enums import BackendName
from app.daas.common.model import DaasObject
from app.daas.container.docker.DockerRequest import DockerRequest
from app.daas.objects.base_container import ContainerBase
from app.daas.storage.filestore import Filestore
from app.qweb.common.qweb_tools import get_backend_component, get_database


@dataclass(kw_only=True)
class ContainerPhase(ContainerBase):
    """Configuration for a containerized object using Guacamole."""

    async def create(self, args: dict) -> tuple[int, str, str]:
        if await self._phase_new_check_args(args):
            if await self._phase_new_consume_args(args):
                if await self._check_resource_limit():
                    if await self._phase_new_create_files(args):
                        if await self._init_object_after_creation():
                            return 0, "", ""
                        return 1, "", "Error during object preparation"
                    return 2, "", "Local container files not created"
                return 3, "", "Insufficient ressource limits"
            return 4, "", "Error on argument consumption"
        return 5, "", "Required arguments missing"

    async def clone(self, oldid: str, args: dict) -> tuple[int, str, str]:
        if await self._phase_clone_check_args(args):
            old = await self._get_db_object(oldid)
            if old is not None:
                if await self._phase_clone_consume_args(old, args):
                    if await self._check_resource_limit():
                        if await self._phase_clone_create_files(old):
                            if await self._init_object_after_creation():
                                return 0, "", ""
                            return 1, "", "Error during object preparation"
                        return 2, "", "Local container files not created"
                    return 3, "", "Insufficient ressource limits"
                return 4, "", "Error on argument consumption"
            return 5, "", "No object to cllone from"
        return 6, "", "Required arguments missing"

    async def _phase_new_consume_args(self, args: dict) -> bool:
        self.os_type = "l26"
        self.id_user = args["name"]
        self.id_owner = args["id_owner"]
        self.hw_cpus = int(args["cores"])
        self.hw_memory = int(args["memsize"]) * 1024**1
        self.hw_disksize = int(args["disksize"]) * 1024**1
        self.id_docker = await self.get_container_tag()
        return True

    async def _phase_clone_consume_args(self, old: DaasObject, args: dict) -> bool:
        self.inherit_object_properties(old)
        self.id = args["newid"]
        self.id_user = args["name"]
        self.id_owner = args["id_owner"]
        self.hw_cpus = old.hw_cpus
        self.hw_memory = old.hw_memory
        self.hw_disksize = old.hw_disksize
        self.id_docker = await self.get_container_tag()
        return True

    async def _init_object_after_creation(self, keep_connections: bool = False) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if await self.start_prepare(keep_connections) is False:
            self._log_error("start_prepare was not successful")
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        code, _, _ = await api.docker_image_build(self.os_installer, self.id_docker)
        if code == 0:
            return await dbase.create_daas_object(self)
        self._log_error("create container object was not successful")
        return True

    async def _phase_clone_create_files(self, old: DaasObject) -> bool:
        api = await get_backend_component(BackendName.FILE, Filestore)
        self.os_installer = await api.copy_user_dockerfile(
            old.os_installer, self.id_owner, self.id
        )
        return self.os_installer != ""

    async def _phase_new_create_files(self, args: dict) -> bool:
        api = await get_backend_component(BackendName.FILE, Filestore)
        if "dockerfile" in args:
            dockerfile = args["dockerfile"]
            if dockerfile is not None and dockerfile != "":
                await api.upload_user_file_docker(
                    args["dockerfile"], "Dockerfile", self.id, self.id_owner
                )
                self.os_installer = await api.get_user_file_docker(
                    self.id, self.id_owner
                )
                if os.path.exists(self.os_installer):
                    return True
                self._log_error("No valid os_installer file", 1)
        if "rootimage" in args:
            rootimage = args["rootimage"]
            if rootimage is not None and rootimage != "":
                if rootimage == "wine":
                    self.os_wine = True
                self.os_installer = await api.copy_root_dockerfile(
                    rootimage, self.id_owner, self.id
                )
                return True
        return False

    async def _phase_clone_check_args(self, args: dict) -> bool:
        required = ["id", "newid", "name", "rootimage"]
        for k in required:
            if k in args is False:
                self._log_error(f"Required argument missing: {k}", 1)
                return False
        return await self._phase_new_check_id(args)

    async def _phase_new_check_args(self, args: dict) -> bool:
        required = ["id", "id_owner", "name", "cores", "memsize", "disksize"]
        for k in required:
            if k in args is False:
                self._log_error(f"Required argument missing: {k}", 1)
                return False
        if await self._phase_new_check_id(args):
            return await self._phase_new_check_dockerfile(args)
        return False

    async def _phase_new_check_dockerfile(self, args: dict) -> bool:
        if "rootimage" not in args and "dockerfile" not in args:
            self._log_error("No Dockerfile", 1)
            return False
        return True

    async def _phase_new_check_id(self, args: dict) -> bool:
        if "id" not in args:
            self._log_error(f"Invalid argument: id='{args['id']}'", 1)
            return False
        return True
