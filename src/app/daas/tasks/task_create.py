"""Task to create objects within a background task"""

from typing import Optional
from nest_asyncio import asyncio
from app.daas.objects.object_container import ContainerObject
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.object_machine import MachineObject
from app.daas.tasks.base_clonetask import CloneTaskBase
from app.daas.tasks.task_config import CreateTaskConfig
from app.qweb.common.qweb_tools import get_database
from app.qweb.processing.processor import QwebResult


class CreateTask(CloneTaskBase):
    """Task to create objects within a background task"""

    def __init__(self, cfg: CreateTaskConfig):
        super().__init__(cfg)

    async def run(self) -> QwebResult:
        self._log_info("Enter create task")
        if await self._handle_state_baseimage():
            if await self._handle_state_environment(self.args):
                return QwebResult(200, {})
            return QwebResult(400, {}, 1, "Error on handle_env()")
        return QwebResult(400, {}, 2, "Error on handle_baseimage()")

    async def _handle_state_baseimage(self) -> bool:
        await self._update_state("Wait for instance boot (baseimage)")
        await self._wait_for_inst_baseimage()
        await self._update_state("Finalize baseimage")
        finalized = await self.obj.baseimage_finalize()
        if finalized is None or finalized.response_code != 200:
            await self._update_state("Error on Finalize")
            return False
        await self._update_state("Finalized baseimage")
        return True

    async def _handle_state_environment(self, args: dict) -> bool:
        assert await self._create_env(args)
        assert await self._configure_connection()
        assert await self._configure_env(args)
        assert await self._install_env(args)
        assert await self._finalize_env(args)
        assert await self._run_env(args)
        return True

    async def _create_env(self, args: dict) -> bool:
        await self._wait_for_inst_env()
        await self._update_state(f"Create environment: {args['env']}")
        envargs = await self._create_envargs(args)
        self.env = await self.obj.env_create([], [], envargs)
        if self.env is None:
            await self._update_error(f"Environment not created: {args['env']}")
            return False
        await self._update_state(f"Created environment: {args['env']}")
        return True

    async def _configure_connection(self) -> bool:
        await self._update_state("Configure connections")
        await self._run_task_configure_connection()
        await self._upgrade_to_env_connection()
        await self._update_state("Configured connection")
        await asyncio.sleep(2)
        return True

    async def _configure_env(self, args: dict) -> bool:
        await self._update_state(f"Configure environment: {args['env']}")
        tasklist = await self._get_object_tasklist()
        applist = await self._get_object_applist()
        target = await self._get_object_target()
        await self.obj.cfg_tasklist(tasklist, self.env, args)
        await self.obj.cfg_applist(applist, self.env, args)
        await self.obj.cfg_set_target(target, self.env, args)
        return await self.obj.update()

    async def _install_env(self, args: dict) -> bool:
        await self._update_state(f"Install environment: {args['env']}")
        files = await self._get_files(self.app)
        installers = await self._get_installers(self.app)
        installed = await self.obj.cfg_install(
            files, installers, args["id_owner"], self.env, args
        )
        if installed is None or installed.response_code != 200:
            await self._update_error(
                f"Error in Configure environment: {args['env']}", 1
            )
            return False
        return True

    async def _finalize_env(self, args: dict) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        assert self.env is not None
        await self._update_state(f"Finalize environment: {args['env']}")
        await self.obj.env_finalize(self.env, args)
        await dbase.update_environment(self.env)
        await self._run_task_configure_connection()
        return True

    async def _run_env(self, args: dict) -> Optional[InstanceObject]:
        assert self.env is not None
        await self._update_state(f"Run environment: {args['env']}")
        return await self.obj.environment_run(
            self.env, args["id_owner"], True, "run-app", args
        )

    async def _upgrade_to_env_connection(self) -> bool:
        from app.daas.db.database import Database

        await self._update_state("Upgrade to env connection")
        dbase = await get_database(Database)
        assert self.env is not None
        obj = await dbase.get_daas_object(self.obj.id)
        inst = await dbase.get_instance_by_id(self.inst.id)
        assert inst is not None
        inst.id_env = self.env.id
        inst.env = self.env
        updated = await dbase.update_instance(inst)
        assert updated
        assert isinstance(obj, MachineObject | ContainerObject)
        self.obj = obj
        self.inst = inst
        await self._update_state("Upgraded to env connection")
        return updated
