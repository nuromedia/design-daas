"""Configuration for objects"""

import json
from dataclasses import asdict, dataclass
from typing import Optional

from nest_asyncio import asyncio
from app.daas.common.enums import BackendName
from app.daas.common.model import Environment, File
from app.daas.objects.env_machine import MachineEnvironmentBase
from app.daas.objects.object_instance import InstanceObject
from app.daas.storage.filestore import Filestore
from app.qweb.common.qweb_tools import get_backend_component, get_database


@dataclass(kw_only=True)
class MachineConfigBase(MachineEnvironmentBase):
    """Configuration for objects"""

    async def configure_applist(
        self, obj: str, env: Optional[Environment], args: dict
    ) -> bool:
        """Configures applist"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        jsonargs = []
        if obj is not None and obj != "":
            jsonargs = json.loads(obj)
        if env is None:
            self.object_apps = jsonargs
            return await dbase.update_daas_object(self)
        if len(env.env_apps) == 0:
            env.env_apps = jsonargs
        else:
            env.env_apps.extend(jsonargs)
        return await dbase.update_environment(env)

    async def configure_tasklist(
        self, obj: str, env: Optional[Environment], args: dict
    ) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        jsonargs = []
        if obj is not None and obj != "":
            jsonargs = json.loads(obj)
        if env is None:
            self.object_tasks = jsonargs
            return await dbase.update_daas_object(self)
        if len(env.env_tasks) == 0:
            env.env_tasks = jsonargs
        else:
            env.env_tasks.extend(jsonargs)
        return await dbase.update_environment(env)

    async def configure_target(
        self, obj: str, env: Optional[Environment], args: dict
    ) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        jsonargs = {}
        if obj is not None and obj != "":
            data = json.loads(obj)
            if "name" in data and data["name"] != "":
                jsonargs = data
        if env is None:
            self.object_target = jsonargs
            return await dbase.update_daas_object(self)
        env.env_target = jsonargs
        return await dbase.update_environment(env)

    async def copy_installers(
        self,
        files: list[File],
        installers: list[str],
        userid: int,
        env: Optional[Environment],
        args: dict,
    ) -> bool:
        instance = await self._get_inst_by_env(env)
        self._log_info("Copy installers:")
        await self.set_extended_mode("Upload installers")
        if len(files) > 0 and instance is not None:
            for file in files:
                self._log_info(f"Filecopy: {file.id}")
                await instance.inst_vminvoke_upload(
                    file.localpath, self.is_windows(), False, file.name
                )
        await self.set_extended_mode("Installers uploaded")
        return True

    async def execute_tasks(
        self, installers: list[str], env: Optional[Environment], args: dict
    ) -> bool:
        tasks = self.object_tasks
        instance = await self._get_inst_by_env(env)
        if env is not None and env.env_tasks != []:
            tasks = env.env_tasks
        if instance is not None:
            # for installer in installers:
            #     ret = await instance.inst_vminvoke_ssh(installer, "")
            #     if ret is not None and ret.response_code == 200:
            #         msg = f"Installer executed! CMD: '{installer}' {ret.sys_log}"
            #         self._log_info(msg, ret.sys_exitcode)

            for task in tasks:
                ttype = task["type"]
                tcmd = task["cmd"]
                targs = task["args"]
                executed = await self.execute_task(instance, task, targs)
                msg = f"Task executed! Type: '{ttype}' CMD: '{tcmd}'"
                self._log_info(msg, executed)
                await self.set_extended_mode(f"Task executed: {ttype}")
            await self.set_extended_mode("Installation finished")
        else:
            self._log_info("Skipping task execution (instance=None)")
        return True

    async def execute_task(
        self, instance: InstanceObject, task: dict, reqargs: dict
    ) -> bool:
        ret = None
        ttype = "exec_app"
        if "type" in task:
            ttype = task["type"]
        cmd = task["cmd"]
        args = task["args"]
        if cmd != "":
            await self.set_extended_mode(f"Execute Task: {cmd}")

        if ttype == "exec_ssh":
            ret = await instance.inst_vminvoke_ssh(cmd, args)
        elif ttype == "exec_app":
            ret = await instance.inst_vminvoke_app(cmd, args)
        elif ttype == "exec_cmd":
            ret = await instance.inst_vminvoke_cmd(cmd, args)
        elif ttype == "os_install":
            ret = await instance.inst_vminvoke_ospackage("install", f"{cmd}")
        elif ttype == "os_uninstall":
            ret = await instance.inst_vminvoke_ospackage("uninstall", f"{cmd}")
        if ret is not None and ret.response_code == 200:
            return True
        if ret is not None:
            self._log_error(f"Execute TASK FAILED: {ret}")
        else:
            self._log_error(f"Execute TASK FAILED: {ret}")
        return False

    async def _get_inst_by_env(
        self, env: Optional[Environment]
    ) -> Optional[InstanceObject]:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if env is None:
            return await dbase.get_instance_by_objid(self.id)
        else:
            return await dbase.get_instance_by_envid(env.id)
