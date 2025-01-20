"""Manages tasks"""

import asyncio
import secrets
from datetime import datetime
from typing import Any, Optional
from app.qweb.common.enums import ScheduledTaskFilter
from app.qweb.common.errors import TaskExecutionError
from app.qweb.logging.logging import LogTarget, Loggable


class ScheduledTask(Loggable):
    id_task: str
    id_object: str
    id_instance: str
    id_owner: int
    task: asyncio.Task
    started_at: datetime
    stopped_at: datetime
    systask: bool
    running: bool
    success: bool
    result: Optional[Any]
    reason: str

    def __init__(
        self,
        name: str,
        id_task: str,
        task: asyncio.Task,
        systask: bool,
        id_owner: int,
        id_object: str = "",
        id_instance: str = "",
    ):
        Loggable.__init__(self, LogTarget.TASK)
        self.tasktype = name
        self.id_task = id_task
        self.id_owner = id_owner
        self.id_object = id_object
        self.id_instance = id_instance
        self.task = task
        self.systask = systask
        self.running = True
        self.success = False
        self.finalized = False
        self.result = None
        self.reason = ""
        self.started_at = datetime.now()
        self.stopped_at = self.started_at

    def to_json(self) -> dict:
        data = vars(self).copy()
        drop = ["task", "logger", "log_target", "result"]
        for name in drop:
            if name in data:
                data.pop(name)
        return data


class QwebTaskManager(Loggable):
    """handles concurrent tasks"""

    tasks_endpoint: dict[str, Any] = {}
    tasks_system: dict[str, Any] = {}
    scheduled_tasks: dict[str, ScheduledTask] = {}
    stopped_tasks: dict[str, ScheduledTask] = {}

    def __init__(self):
        Loggable.__init__(self, LogTarget.TASK)
        self.loop = asyncio.get_event_loop()

    def __repr__(self):
        return f"{self.__class__.__qualname__}" f"(tasks={len(self.tasks_endpoint)})"

    async def __run_task(self, task, *args, **kwargs):
        return await task(*args, **kwargs)

    async def __run_apitask(self, task, *args, **kwargs):
        assert task is not None
        return await task(*args, **kwargs)

    async def __run_systask(self, task, *args, **kwargs):
        assert task is not None
        return await task(*args, **kwargs)

    async def stop_scheduled_task(self, name: str) -> bool:
        return await self._stop_scheduled_task(name)

    async def get_tasks_by_taskid(self, id_task: str) -> list[ScheduledTask]:
        return list(
            filter(
                lambda obj: obj.id_task == id_task,
                self.scheduled_tasks.values(),
            )
        )

    async def get_tasks_by_object(self, id_object: str) -> list[ScheduledTask]:
        return list(
            filter(
                lambda obj: obj.id_object == id_object,
                self.scheduled_tasks.values(),
            )
        )

    async def get_tasks_by_instance(self, id_instance: str) -> list[ScheduledTask]:
        return list(
            filter(
                lambda obj: obj.id_instance == id_instance,
                self.scheduled_tasks.values(),
            )
        )

    async def _stop_scheduled_task(self, name: str) -> bool:
        result = False
        if name in self.scheduled_tasks:
            t = self.scheduled_tasks[name]
            return t.task.cancel()
        return result

    async def _remove_scheduled_task(self, name: str) -> bool:
        result = False
        if name in self.scheduled_tasks:
            self.scheduled_tasks.pop(name)
            result = True
        return result

    async def _remove_stopped_task(self, name: str) -> bool:
        result = False
        if name in self.stopped_tasks:
            self.stopped_tasks.pop(name)
            result = True
        return result

    async def _add_scheduled_task(self, task: ScheduledTask) -> bool:
        result = False
        if task is not None:
            self.scheduled_tasks[task.id_task] = task
            result = True
        return result

    async def _add_stopped_task(self, task: ScheduledTask) -> bool:
        result = False
        if task is not None:
            self.stopped_tasks[task.id_task] = task
            result = True
        return result

    async def get_scheduled_tasks(
        self, state: ScheduledTaskFilter
    ) -> dict[str, ScheduledTask]:
        result = {}
        if state == ScheduledTaskFilter.RUNNING or state == ScheduledTaskFilter.ALL:
            result.update(self.scheduled_tasks.copy())
        if state == ScheduledTaskFilter.FINAL or state == ScheduledTaskFilter.ALL:
            result.update(self.stopped_tasks.copy())
        return result

    async def get_status_scheduled_task(self):
        running = await self.get_scheduled_tasks(ScheduledTaskFilter.RUNNING)
        stopped = await self.get_scheduled_tasks(ScheduledTaskFilter.FINAL)
        self._log_info(f"TASKSTATE: {running} {stopped}")
        return {
            ScheduledTaskFilter.RUNNING.value: [
                x.to_json() for _, x in running.items()
            ],
            ScheduledTaskFilter.FINAL.value: [x.to_json() for _, x in stopped.items()],
        }

    async def get_scheduled_task(
        self,
        state: ScheduledTaskFilter,
        id_task: str,
        objectid: str,
        instid: str,
    ) -> Optional[ScheduledTask]:
        result = None
        tasklist = await self.get_scheduled_tasks(state)
        if id_task != "" and id_task in tasklist:
            return tasklist[id_task]
        for _, val in tasklist.items():
            if objectid != "":
                if objectid == val.id_object:
                    return val
            if instid != "":
                if instid == val.id_instance:
                    return val
        return result

    async def get_stopped_task(self, name: str) -> Optional[ScheduledTask]:
        if name in self.stopped_tasks:
            return self.stopped_tasks[name]
        return None

    async def filter_tasks(
        self,
        results: dict[str, ScheduledTask],
        id_owner: Optional[int] = 0,
        id_object: Optional[str] = "",
        id_instance: Optional[str] = "",
    ):
        """Filters tasklist"""
        accepted = {}
        for _, val in results.items():
            addme = False
            if id_owner in (0, val.id_owner):
                addme = True
            else:
                continue
            if id_object in ("", val.id_object):
                addme = True
            else:
                continue
            if id_instance in ("", val.id_instance):
                addme = True
            else:
                continue
            if addme:
                accepted[val] = val
        return accepted

    def add_task_endpoint(self, name: str, func: Any):
        """Adds new endpoint task"""
        self.tasks_endpoint[name] = func
        self._log_info(f"Add endpoint task: {name}")

    def add_task_system(self, name: str, func: Any):
        """Adds new system task"""
        self.tasks_system[name] = func
        self._log_info(f"Add system task: {name}")

    def get_task_endpoint(self, name: str) -> Optional[Any]:
        """Returns endpoint task specified by name"""
        if name in self.tasks_endpoint:
            return self.tasks_endpoint[name]
        return None

    def get_task_system(self, name: str) -> Optional[Any]:
        """Returns system task specified by name"""
        if name in self.tasks_system:
            return self.tasks_system[name]
        return None

    async def run_tasks_concurrently(self, tasks):
        """
        tasks: a list of tuples, where each tuple contains an instance, a method name, and its arguments.
        Example: [(instance1, "method1", arg1, arg2), (instance2, "method2", arg1)]
        """
        coroutines = [
            self.__run_task(getattr(instance, method_name), *args, **kwargs)
            for instance, method_name, args, kwargs in tasks
        ]
        created_tasks = [asyncio.create_task(coro) for coro in coroutines]
        results = await asyncio.gather(*created_tasks)
        return results

    async def run_apitasks_concurrently(self, tasks):
        """
        tasks: a list of tuples, where each tuple contains an instance, a method name, and its arguments.
        Example: [(instance1, "method1", arg1, arg2), (instance2, "method2", arg1)]
        """
        coroutines = [
            self.__run_apitask(method_name, *args, **kwargs)
            for method_name, args, kwargs in tasks
        ]
        created_tasks = [asyncio.create_task(coro) for coro in coroutines]
        results = await asyncio.gather(*created_tasks)
        return results

    async def run_apitask_concurrently(self, task):
        """
        tasks: a list of tuples, where each tuple contains an instance, a method name, and its arguments.
        Example: [(instance1, "method1", arg1, arg2), (instance2, "method2", arg1)]
        """
        method_name, args, kwargs = task
        created_task = asyncio.create_task(
            self.__run_apitask(method_name, *args, **kwargs)
        )
        result = await asyncio.gather(created_task)
        return result[0]

    async def run_systasks_concurrently(self, tasks):
        """
        tasks: a list of tuples, where each tuple contains an instance, a method name, and its arguments.
        Example: [(instance1, "method1", arg1, arg2), (instance2, "method2", arg1)]
        """
        coroutines = [
            self.__run_systask(method_name, *args, **kwargs)
            for method_name, args, kwargs in tasks
        ]
        created_tasks = [asyncio.create_task(coro) for coro in coroutines]
        results = await asyncio.gather(*created_tasks)
        return results

    async def start_systask(
        self,
        name: str,
        task: tuple,
        systask: bool,
        id_owner: int,
        id_object: str = "",
        id_instance: str = "",
    ) -> ScheduledTask:
        """
        tasks: a list of tuples, where each tuple contains an instance, a method name, and its arguments.
        Example: [(instance1, "method1", arg1, arg2), (instance2, "method2", arg1)]
        """
        from app.qweb.common.common import SystemTaskArgs

        # Use taskid from arguments if available
        coro, args, kwargs = task
        taskid = secrets.token_urlsafe(16)
        if isinstance(args, list):
            if isinstance(args[0], SystemTaskArgs):
                if args[0].id_task == "":
                    args[0].id_task = taskid
                else:
                    taskid = args[0].id_task
        task_rt = asyncio.create_task(
            self._task_runtime(name, taskid, coro, *args, **kwargs)
        )
        task_sched = ScheduledTask(
            name, taskid, task_rt, systask, id_owner, id_object, id_instance
        )
        await self._add_scheduled_task(task_sched)
        return task_sched

    async def _task_runtime(
        self, typename: str, id_task: str, method_name: str, *args, **kwargs
    ) -> Optional[ScheduledTask]:
        self._log_info(f"Task started   : {typename} ({id_task})", 0)
        info = await self.get_scheduled_task(
            ScheduledTaskFilter.RUNNING, id_task, "", ""
        )
        if info is not None:
            self._log_info(f"Task scheduled : {typename} ({id_task})", 0)
            try:
                info.result = await self.__run_systask(method_name, *args, **kwargs)
                info.success = True
                msg = f"{typename} ({id_task}) Result={info.result}"
                self._log_info(f"Task success   : {msg}", 0)
            except asyncio.CancelledError:
                info.result = None
                info.success = False
                info.reason = "Task cancelled"
                msg = f"{typename} ({id_task})"
                self._log_info(f"Task cancelled : {msg}", 1)
            except TaskExecutionError as exe:
                info.result = None
                info.success = False
                info.reason = f"TaskExecutionError: {exe.args[0]}"
                msg = f"{typename} ({id_task}) Reason={info.reason}"
                self._log_error(f"Task error     : {msg}", 2)
            except Exception as exe:
                info.result = None
                info.success = False
                info.reason = f"Unknown task error: {exe.args[0]}"
                msg = f"{typename} ({id_task}) Reason={info.reason}"
                self._log_error(f"Task error     : {msg}", 3)
            finally:
                info.running = False
                info.stopped_at = datetime.now()
                info.finalized = True
                await self._remove_scheduled_task(id_task)
                await self._add_stopped_task(info)
                self._log_info(f"Task finalized : {typename} ({id_task})", 0)
            return info
        self._log_error(f"Task error     : {typename} ({id_task})", 4)
        return None
