"""Baseclass for environment functionality"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.common.model import Environment, File
from app.daas.container.docker.DockerRequest import DockerRequest
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.phase_container import ContainerPhase
from app.daas.storage.filestore import Filestore
from app.qweb.common.qweb_tools import get_backend_component, get_database
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass(kw_only=True)
class ContainerEnvironmentBase(ContainerPhase):
    """Baseclass for environment functionality"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Loggable.__init__(self, LogTarget.OBJECT)

    async def env_create(
        self, files: list[File] = [], installers: list[str] = [], args: dict = {}
    ) -> Optional[Environment]:
        """Derives new environment"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        store = await get_backend_component(BackendName.FILE, Filestore)
        userid = args["id_owner"]

        # Check env
        if "name" not in args:
            return None
        name = args["name"]
        old = await self.env_get(name, args)

        if old is not None:
            return None

        self._log_info(f"Syncing files to env {name}")
        for file in files:
            await store.upload_to_docker_folder(
                file.localpath, file.name, self.id, self.id_owner
            )
        if "file" in args and args["file"] is not None and args["file"].filename != "":
            dockerfile = await store.upload_user_envfile_docker(
                args["file"], name, self.id, self.id_owner, files, installers
            )
        else:
            dockerfile = await store.create_docker_envfile(
                self.id, userid, self.id, name, files, installers
            )
        self._log_info(f"Files synced to env {name}")

        id_backend = await self.get_environment_tag(name)
        code, _, _ = await api.docker_image_build(dockerfile, id_backend)
        if code != 0:
            self._log_error(f"Container was not build: {id_backend}", code)
            return None
        self._log_info(f"Container build success: {id_backend}", 0)
        env = self._create_new_environment(self, name, name, datetime.now())
        env.env_tasks = self.object_tasks
        env.env_apps = self.object_apps
        env.env_target = self.object_target
        await dbase.create_environment(env)
        if env is None:
            self._log_error(f"Database environment was None: {id_backend}", code)
            return None
        self._log_info(f"Environment created: {id_backend}", 0)
        return await self.env_get(name, args)

    async def env_finalize(self, env: Environment, args: dict) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        env.state = "environment-final"
        return await dbase.update_environment(env)

    async def env_get(self, name: str, args: dict = {}) -> Optional[Environment]:
        """Returns specified environment"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        return await dbase.get_environment_by_name(self.id, name)

    async def envs_get(self, args: dict) -> list[Environment]:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        return await dbase.get_environments_by_object(self.id)

    async def env_delete(self, env: Environment, args: dict = {}) -> bool:
        """Deletesspecified environment"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        store = await get_backend_component(BackendName.FILE, Filestore)
        userid = args["id_owner"]
        old = await self.env_get(env.name, args)
        if old is not None:
            await self.env_stop(env, True, args)
            await store.delete_docker_envfile(self.id, userid, self.id, env.name)
            id_backend = await self.get_environment_tag(env.name)
            await api.docker_image_delete(id_backend)
            deleted = await dbase.delete_environment(env)
            if deleted:
                self._log_info(f"Deleted environment {self.id_docker} ({env.name})")
                return True
        self._log_info(f"Environment {self.id_docker} ({env.name}) nopt deleted")
        return False

    async def env_stop(self, env: Environment, force: bool, args: dict = {}) -> bool:
        """Stops environment instance"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        instance_env = await dbase.get_instance_by_envid(env.id)
        await self._kill_object_tasks()
        if instance_env is not None:
            return await self.stop(instance_env, force)
        return True

    async def env_start_prepare(
        self, env: Environment, userid: int, keep_connections: bool = False
    ) -> bool:
        """Prepares object for a subsequent call to 'run'"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        store = await get_backend_component(BackendName.FILE, Filestore)
        instance_env = await dbase.get_instance_by_envid(env.id)
        if instance_env is not None and keep_connections is False:
            await self.stop(instance_env, True)
        dockerfile = await store.get_docker_envfile(userid, self.id, env.name)
        id_backend = await self.get_environment_tag(env.name)
        code, _, _ = await api.docker_image_build(dockerfile, id_backend)
        return code == 0

    async def env_start(
        self,
        env: Environment,
        userid: int,
        connect: bool,
        object_mode: str = "",
        args: dict = {},
        keep_connections: bool = False,
    ) -> Optional[InstanceObject]:
        """Starts environment instance"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        if await self.env_start_prepare(env, userid, keep_connections):
            environment_tag = await self.get_environment_tag(env.name)
            instance_env = await dbase.get_instance_by_envid(env.id)
            if instance_env is not None:
                if keep_connections is True:
                    # await asyncio.sleep(1)
                    oldtag = await self.get_container_tag()
                    await api.docker_container_stop(oldtag, True)
            code, container_id, _ = await api.docker_container_start(
                environment_tag,
                environment_tag,
                self.hw_cpus,
                self.hw_memory * 1024**1,
            )
            if code == 0 and container_id != "":
                if await self.env_start_finalize(
                    instance_env, env, userid, object_mode, keep_connections
                ):
                    instance_env = await dbase.get_instance_by_envid(env.id)
                    if instance_env is not None:
                        if instance_env.id_env is None:
                            instance_env.id_env = env.id
                            await instance_env.update()
                        return await self._return_connected_instance(connect)

        self._log_error("Environment not build correctly")
        return None

    async def env_start_finalize(
        self,
        instance_env: Optional[InstanceObject],
        env: Environment,
        userid: int,
        object_mode: str = "",
        keep_connections: bool = False,
    ) -> bool:
        """Finalizes object after prior call to 'run'"""
        if instance_env is None or keep_connections is False:
            instance = await self.insert_pending_instance(userid, env)
            await self.run_system_task_postboot(instance)
        else:
            # await asyncio.sleep(1)
            if instance_env is not None:
                api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
                environment_tag = await self.get_environment_tag(env.name)
                instance_env.host = await api.docker_get_container_ip(environment_tag)
                await instance_env.update()
                # await asyncio.sleep(1)
        if object_mode != "":
            self.object_mode = object_mode
        await self.set_extended_mode("done")
        self._log_info(f"Started environment {self.id_docker}")
        return True
