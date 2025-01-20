"""Baseclass for a containerized object using Guacamole."""

from dataclasses import dataclass
from typing import Optional
from app.daas.common.ctx import create_response_by_data_length
from app.daas.common.enums import BackendName
from app.daas.container.docker.DockerRequest import DockerRequest
from app.daas.objects.base_object import DaasBaseObject
from app.daas.objects.object_instance import InstanceObject
from app.qweb.common.qweb_tools import get_backend_component, get_database
from app.qweb.processing.processor import QwebResult


@dataclass(kw_only=True)
class ContainerBase(DaasBaseObject):
    """Configuration for a containerized object using Guacamole."""

    async def start(
        self,
        userid: int,
        connect: bool = False,
        object_mode: str = "",
        keep_connections: bool = False,
    ) -> Optional[InstanceObject]:
        """Start the application."""
        assert await self.verify_demand(userid)
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        tag = await self.get_container_tag()
        if await self.start_prepare(keep_connections):
            code, _, _ = await api.docker_container_start(
                self.id_docker, tag, self.hw_cpus, self.hw_memory * 1024, False, [], []
            )
            if code == 0:
                if await self.start_finalize(userid, True, object_mode=object_mode):
                    return await self._return_connected_instance(connect)
        return None

    async def stop(self, instance: InstanceObject, force: bool) -> bool:
        """Stop and delete the instance."""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        if await self.stop_prepare(instance, force):
            tag = await self.get_container_tag()
            if instance.id_env is not None and instance.id_env != "":
                env = await dbase.get_environment(instance.id_env)
                if env is not None:
                    tag = await self.get_environment_tag(env.name)
            await api.docker_container_stop(tag, force)
            return await self.stop_finalize(instance)
        return True

    async def status_container(self) -> QwebResult:
        """Returns status information"""
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        tag = await self.get_container_tag()
        data = await api.docker_image_inspect(tag)
        return await create_response_by_data_length(data, True)

    async def image_build(self) -> QwebResult:
        """Builds specified docker image"""
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        tag = await self.get_container_tag()
        code, str_out, str_err = await api.docker_image_build(self.os_installer, tag)
        return QwebResult(200, {}, code, f"{str_out}{str_err}")

    async def image_delete(self) -> QwebResult:
        """Deletes specified docker image"""
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        tag = await self.get_container_tag()
        code, str_out, str_err = await api.docker_image_delete(tag)
        return QwebResult(200, {}, code, f"{str_out}{str_err}")
