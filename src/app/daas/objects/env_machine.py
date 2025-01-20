"""Baseclass for environment functionality"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.common.model import Environment, File
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.phase_machine import MachinePhase
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.qweb.common.qweb_tools import get_backend_component, get_database
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.processing.processor import QwebResult


@dataclass(kw_only=True)
class MachineEnvironmentBase(MachinePhase):
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
        name = args["name"]

        snapshots = await self.vmsnapshot_list()
        if (
            isinstance(snapshots.response_data, dict)
            and len(snapshots.response_data["data"]) > 1
        ):
            self._log_info(f"Restore VM root snapshot: {self.id_proxmox}")
            response: QwebResult = await self.vmsnapshot_rollback("root")
            if response.response_code != 200:
                self._log_error(f"VM snapshot not restored: {self.id_proxmox}", 1)
                return None
            self._log_info(f"VM root snapshot restored: {self.id_proxmox}", 0)
        env = self._create_new_environment(self, name, name, datetime.now())
        env.env_tasks = self.object_tasks
        env.env_apps = self.object_apps
        env.env_target = self.object_target
        await dbase.create_environment(env)
        if env is None:
            self._log_error(f"Database environment was None: {self.id_proxmox}", 2)
            return None
        self._log_info(f"Environment created: {self.id_proxmox}", 0)
        return await self.env_get(name, args)

    async def env_finalize(self, env: Environment, args: dict) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        response = await self.vmsnapshot_create(env.name, "")
        if response is not None and response.response_code == 200:
            env.state = "environment-final"
            return await dbase.update_environment(env)
        return False

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
        old = await self.env_get(env.name, args)
        if old is not None:
            await self.env_stop(env, True, args)
            deleted = await dbase.delete_environment(env)
            if deleted:
                self._log_info(f"Deleted environment {self.id_docker} ({env.name})")
                return True
        self._log_info(f"Environment {self.id_docker} ({env.name}) not deleted")
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
        await self._kill_object_tasks()
        instance_env = await dbase.get_instance_by_envid(env.id)
        if instance_env is not None and keep_connections is False:
            await self.stop(instance_env, True)
        response = await self.vmsnapshot_rollback(env.name)
        if response is not None and response.response_code == 200:
            return True
        return False

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
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        if await self.env_start_prepare(env, userid, keep_connections):
            await self.set_extended_mode("env prepared")
            response, _ = await api.prox_vmstart(api.config_prox.node, self.id_proxmox)
            if response is not None and response.status == 200:
                if await self.env_start_finalize(
                    env, userid, object_mode, keep_connections
                ):
                    inst = await dbase.get_instance_by_envid(env.id)
                    if inst is not None:
                        return await self._return_connected_instance(connect)
        self._log_error("Environment not started correctly")
        return None

    async def env_start_finalize(
        self,
        env: Environment,
        userid: int,
        object_mode: str = "",
        keep_connections: bool = False,
    ) -> bool:
        """Finalizes object after prior call to 'run'"""
        if keep_connections is False:
            instance = await self.insert_pending_instance(userid, env)
            await self.run_system_task_postboot(instance)
        if object_mode != "":
            self.object_mode = object_mode
        if object_mode == "run-debug":
            await self.set_extended_mode("done")
        # else:
        #     await self.set_extended_mode("env started")

        self._log_info(f"Started environment {self.id_docker}")
        return True
