"""Configuration for objects"""

import json
from dataclasses import dataclass
from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.common.model import Environment, File
from app.daas.objects.env_container import ContainerEnvironmentBase
from app.daas.objects.object_instance import InstanceObject
from app.daas.storage.filestore import Filestore
from app.qweb.common.qweb_tools import get_backend_component, get_database


@dataclass(kw_only=True)
class ContainerConfigBase(ContainerEnvironmentBase):
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
            if len(self.object_apps) == 0:
                self.object_apps = jsonargs
            else:
                self.object_apps.extend(jsonargs)
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
            if len(self.object_tasks) == 0:
                self.object_tasks = jsonargs
            else:
                self.object_tasks.extend(jsonargs)
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
        store = await get_backend_component(BackendName.FILE, Filestore)
        instance = await self._get_inst_by_env(env)
        tasks = self.object_tasks
        if env is not None:
            tasks = env.env_tasks
        self._log_info("Copy installers:")

        name = ""
        if env is not None:
            name = env.name
        for file in files:
            await store.upload_to_docker_folder(
                file.localpath, file.name, self.id, self.id_owner
            )
            await store.create_docker_envfile(
                self.id, userid, self.id, name, files, installers
            )
        await self.set_extended_mode("Upload installers")
        if len(files) > 0 and instance is not None:
            for file in files:
                self._log_info(f"Filecopy: {file.id}")
                # filename, norm_folder, False
                await instance.inst_vminvoke_upload(
                    file.localpath, self.is_windows(), False
                )
                await store.upload_file_to_instance(file, instance)
        await self.set_extended_mode("Installers uploaded")
        self._log_info(f"Executing tasks: {tasks}")
        tasks = self.object_tasks
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
            #     await instance.inst_vminvoke_app(installer, "")
            #     msg = f"Installer executed! CMD: '{installer}'"
            for task in tasks:
                ttype = task["type"]
                cmd = task["cmd"]
                executed = await self.execute_task(instance, task, args)
                msg = f"Task executed! Type: '{ttype}' CMD: '{cmd}'"
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
            await self.set_extended_mode(f"Installing {cmd}")
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
