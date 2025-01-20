"""Phases Tasks"""

from app.daas.tasks.task_clone import CloneTaskConfig, CloneTask
from app.daas.tasks.task_create import CreateTask, CreateTaskConfig
from app.daas.tasks.task_postboot import PostbootConfig, PostbootTask
from app.qweb.common.common import SystemTaskArgs
from app.qweb.processing.processor import QwebResult


async def run_task_postboot(args: SystemTaskArgs) -> QwebResult:
    """Executes postboot actions"""
    task = PostbootTask(PostbootConfig(args, True, False, True))
    return await task.run()


async def run_task_connection_config(args: SystemTaskArgs) -> QwebResult:
    """Configures proxmox vnc via monitor commands"""
    task = PostbootTask(PostbootConfig(args, True, False, False))
    return await task.run()


async def run_task_wait_for_inst(args: SystemTaskArgs) -> QwebResult:
    """Waits for instance to boot"""
    task = PostbootTask(PostbootConfig(args, False, False, True))
    return await task.run()


async def run_task_app_create(args: SystemTaskArgs) -> QwebResult:
    """Creates new object from app"""
    task = CreateTask(CreateTaskConfig(args))
    return await task.run()


async def run_task_app_clone(args: SystemTaskArgs) -> QwebResult:
    """Clones app into new object"""
    task = CloneTask(CloneTaskConfig(args))
    return await task.run()
