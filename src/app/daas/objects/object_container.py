"""Configuration for a containerized app using Guacamole."""

import asyncio
from dataclasses import dataclass
from typing import Optional
from app.daas.common.model import Environment, File
from app.daas.db.db_mappings import ORMMappingType, ORMModelDomain
from app.daas.objects.config_factory import get_empty_object_dict
from app.daas.objects.config_container import ContainerConfigBase
from app.daas.objects.object_instance import InstanceObject
from app.qweb.common.qweb_tools import get_database
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.processing.processor import QwebResult


@ORMModelDomain(ORMMappingType.Container)
@dataclass(kw_only=True)
class ContainerObject(ContainerConfigBase):
    """Configuration for a containerized app using Guacamole."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Loggable.__init__(self, LogTarget.OBJECT)

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}"
            f"(id={self.id},name={self.id_user},"
            f"obj_type={self.object_type},os_type={self.os_type})"
        )

    async def baseimage_create(self, args: dict) -> QwebResult:
        assert await self.verify_demand(args["id_owner"])
        code, str_out, str_err = await self.create(args)
        status = 200 if code == 0 else 400
        return QwebResult(status, {}, code, f"{str_out}{str_err}")

    async def baseimage_clone(self, oldid: str, args: dict) -> QwebResult:
        assert await self.verify_demand(args["id_owner"])
        code, str_out, str_err = await self.clone(oldid, args)
        status = 200 if code == 0 else 400
        return QwebResult(status, {}, code, f"{str_out}{str_err}")

    async def baseimage_finalize(self) -> QwebResult:
        self.object_state = "baseimage-final"
        if await self.update():
            return QwebResult(200, {})
        return QwebResult(400, {}, 1, "Error during db update")

    async def environment_create(self, args: dict) -> QwebResult:
        env = await self.env_create([], [], args)
        if env is not None:
            return QwebResult(200, vars(env))
        return QwebResult(400, {}, 1, "Env not created")

    async def environment_finalize(self, env: Environment, args: dict) -> QwebResult:
        if await self.env_finalize(env, args):
            return QwebResult(200, {})
        return QwebResult(400, {}, 1, "Env not finalized")

    async def environment_delete(self, env: Environment, args: dict) -> QwebResult:
        if await self.env_delete(env, args):
            return QwebResult(200, vars(env))
        return QwebResult(400, {}, 1, "Env not deleted")

    async def environment_get(self, name: str, args: dict) -> QwebResult:
        env = await self.env_get(name, args)
        if env is not None:
            return QwebResult(200, vars(env))
        return QwebResult(400, {}, 1, "No env")

    async def environments_get(self, args: dict) -> QwebResult:
        envs = await self.envs_get(args)
        return QwebResult(200, [vars(env) for env in envs])

    async def environment_start(
        self,
        env: Environment,
        userid: int,
        connect: bool,
        object_mode: str = "",
        args: dict = {},
    ) -> Optional[InstanceObject]:
        """Starts environment instance"""
        assert await self.verify_demand(userid)
        inst = await self.env_start(env, userid, connect, object_mode, args, True)
        if inst is not None:
            return await self._return_connected_instance(connect)
        return None

    async def environment_run(
        self,
        env: Environment,
        userid: int,
        connect: bool,
        object_mode: str = "",
        args: dict = {},
    ) -> Optional[InstanceObject]:
        """Runs environment instance"""
        assert await self.verify_demand(userid)
        inst = await self.env_start(env, userid, connect, object_mode, args, True)
        if inst is not None:
            if object_mode != "":
                self.object_mode = "run-app"
                await self.update()
                await asyncio.sleep(1)
            if await self.execute_task(inst, env.env_target, args):
                await self.set_extended_mode("done")
            # else:
            # self._log_error("Execute task failed")
            return await self._return_connected_instance(connect)
        return None

    async def environment_stop(
        self, env: Environment, force: bool, args: dict
    ) -> QwebResult:
        if await self.env_stop(env, force, args):
            return QwebResult(200, {}, response_url="-")
        return QwebResult(400, {}, 1, "Env not stopped")

    async def cfg_applist(
        self, obj: str, env: Optional[Environment], args: dict
    ) -> QwebResult:
        if await self.configure_applist(obj, env, args):
            return QwebResult(200, {})
        return QwebResult(400, {}, 1, "Error on applist config")

    async def cfg_tasklist(
        self, obj: str, env: Optional[Environment], args: dict
    ) -> QwebResult:
        if await self.configure_tasklist(obj, env, args):
            return QwebResult(200, {})
        return QwebResult(400, {}, 1, "Error on tasklist config")

    async def cfg_set_target(
        self, obj: str, env: Optional[Environment], args: dict
    ) -> QwebResult:
        if await self.configure_target(obj, env, args):
            return QwebResult(200, {})
        return QwebResult(400, {}, 1, "Error on target config")

    async def cfg_installers_deploy(
        self,
        files: list[File],
        installers: list[str],
        userid: int,
        env: Optional[Environment],
        args: dict,
    ) -> QwebResult:
        if await self.copy_installers(files, installers, userid, env, args):
            return QwebResult(200, {})
        return QwebResult(400, {}, 1, "error on installer_deploy")

    async def cfg_installers_execute(
        self, installers: list[str], env: Optional[Environment], args: dict
    ) -> QwebResult:
        if await self.execute_tasks(installers, env, args):
            return QwebResult(200, {})
        return QwebResult(400, {}, 1, "error on installer_execute")

    async def cfg_install(
        self,
        files: list[File],
        installers: list[str],
        userid: int,
        env: Optional[Environment],
        args: dict,
    ) -> QwebResult:
        if await self.copy_installers(files, installers, userid, env, args):
            if await self.execute_tasks(installers, env, args):
                return QwebResult(200, {})
        return QwebResult(400, {}, 1, "error on installation")

    async def update(self) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        return await dbase.update_daas_object(self)


async def get_empty_container_object(userid: int, **kwargs) -> ContainerObject:
    """Creates empty Container object"""
    dict_args = await get_empty_object_dict(
        object_type="container", userid=userid, **kwargs
    )
    return ContainerObject(**dict_args)
