from dataclasses import asdict, dataclass
from typing import Optional
from quart import json
from app.daas.common.model import Environment, File
from app.daas.objects.object_application import ApplicationObject
from app.daas.objects.object_container import ContainerObject
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.object_machine import MachineObject
from app.daas.tasks.task_config import (
    ApplistObject,
    CloneTaskConfig,
    CreateTaskConfig,
    TargetObject,
    TasklistObject,
)
from app.plugins.platform.phases.enums import PhasesSystemTask
from app.qweb.common.qweb_tools import run_system_task
from app.qweb.logging.logging import LogTarget, Loggable


class CloneTaskBase(Loggable):
    def __init__(self, cfg: CloneTaskConfig | CreateTaskConfig):
        Loggable.__init__(self, LogTarget.AUTOMATION)
        self.cfg = cfg
        assert self.cfg is not None
        assert self.cfg.args is not None
        assert self.cfg.args.args is not None
        assert self.cfg.args.args["app"] is not None
        assert self.cfg.args.args["obj"] is not None
        assert self.cfg.args.args["inst"] is not None
        self.args = self.cfg.args.args
        assert self.args is not None
        assert isinstance(self.args["app"], ApplicationObject)
        assert isinstance(self.args["obj"], MachineObject | ContainerObject)
        assert isinstance(self.args["inst"], InstanceObject)
        self.app: ApplicationObject = self.args["app"]
        self.obj: MachineObject | ContainerObject = self.args["obj"]
        self.inst: InstanceObject = self.args["inst"]
        self.env: Optional[Environment] = None

    async def _get_files(
        self,
        app: ApplicationObject,
    ) -> list[File]:
        file = await app.get_file()
        files = []
        if file is not None:
            files.append(file)
        return files

    async def _get_installers(
        self,
        app: ApplicationObject,
    ) -> list[str]:
        installer = await app.get_installer()
        installers = []
        if installer != "":
            installers.append(installer)
        return installers

    async def _get_object_tasklist(self) -> str:
        ttype = self.app.installer_type
        cmd = self.app.installer
        args = self.app.installer_args
        obj = TasklistObject(ttype, cmd, args)
        return json.dumps([asdict(obj)])

    async def _get_object_applist(self) -> str:
        obj = ApplistObject("exec_app", self.app.target, self.app.target_args)
        return json.dumps([asdict(obj)])

    async def _get_object_target(self) -> str:
        obj = TargetObject(self.app.name, self.app.target, self.app.target_args)
        return json.dumps(asdict(obj))

    async def _create_envargs(self, args: dict) -> dict:
        envargs = args.copy()
        envargs["name"] = args["env"].lower()
        return envargs

    async def _update_state(self, msg: str, code: int = -1):
        self._log_info(msg, code)
        await self.obj.set_extended_mode(msg)

    async def _update_error(self, msg: str, code: int = -1):
        self._log_error(msg, code)
        await self.obj.set_extended_mode(msg)

    async def _wait_for_inst_baseimage(self):
        self._log_info("Waiting for instance to boot (baseimage)")
        await self._run_task_wait_for_inst()
        await self.obj.set_extended_mode("Object booted")

    async def _wait_for_inst_env(self):
        await self._run_task_wait_for_inst()
        await self.obj.set_extended_mode("Object started")
        self._log_info("Creating env")

    async def _run_task_wait_for_inst(self):
        ttype = PhasesSystemTask.PHASES_WAIT_FOR_INSTANCE.value
        task = await run_system_task(
            ttype, self.obj.id_owner, self.obj.id, self.inst.id
        )
        assert task is not None
        self._log_info("Waiting")
        await task.task
        self._log_info("Waited")

    async def _run_task_configure_connection(self):
        ttype = PhasesSystemTask.PHASES_CONFIGURE_CONNECTION.value
        task = await run_system_task(
            ttype, self.obj.id_owner, self.obj.id, self.inst.id
        )
        assert task is not None
        await task.task
