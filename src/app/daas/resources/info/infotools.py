"""Manages tasks"""

import json
import logging
import asyncio
from typing import Awaitable, Callable, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from app.qweb.service.service_tasks import ScheduledTask


def log_info(msg):
    """Logs messages"""
    full = f"TSKTLS: {msg}"
    logging.getLogger("daas.tasks").info(full)


class TaskType(Enum):
    """Specifies a task type"""

    RAW = 1
    PREPARED = 2


class PreparedTaskType(Enum):
    """Specifies a prepared task type"""

    UNKNOWN = 0
    WAIT_FOR_BOOT = 1
    REBOOT = 2
    WAIT_FOR_POSTBOOT = 3
    CONFIGURE_CONNECT = 4
    RUN_ENVTARGET = 5
    FINALIZE_OBJECT = 6
    FINALIZE_ENV = 7
    FINALIZE_ALL = 8
    DBPING_INSTANCE = 9
    FETCH_OBJINFO = 10
    TESTING_WAIT = 11


class TaskState(Enum):
    """Specifies a tasks state"""

    CREATED = 1
    WAITING = 2
    RUNNING = 3
    FINISHED = 4
    CANCELLED = 5
    ERROR = 6


@dataclass
class TaskArguments:
    """Arguments required by the Taskmanger"""

    func_call: Callable[["TaskArguments"], Awaitable[Any]]
    func_args: dict[str, Any]

    def tostring(self):
        """Converts object to string representation"""
        return (
            f"TaskArguments(Call={self.func_call.__name__}(args), "
            f"Args={self.func_args})"
        )

    def tojson(self) -> dict:
        """Converts object to json representation"""
        return {
            "func_call": f"{self.func_call.__name__}(args) -> Any",
            "func_args": self.func_args,
        }


@dataclass
class TaskResult:
    """Result obtained from function call"""

    result: Optional[Any] = None

    def tostring(self):
        """Converts object to string representation"""
        return f"TaskResult(Result={self.result})"

    def tojson(self) -> dict:
        """Converts object to json representation"""
        return {
            "result": self.result,
        }


@dataclass
class TaskDuration:
    """Defines duration of a task"""

    ts_start: datetime
    ts_stop: datetime
    isfinite: bool

    def tostring(self):
        """Converts object to string representation"""
        return (
            "TaskDuration("
            f"Finite={self.isfinite},Time='"
            f"{int(self.ts_start.timestamp())}-"
            f"{int(self.ts_stop.timestamp())}'"
            ")"
        )

    def tojson(self) -> dict:
        """Converts object to json representation"""
        stopts = 0
        if self.ts_stop is not None and self.ts_stop != datetime.max:
            stopts = self.ts_stop.timestamp()

        return {
            "ts_start": self.ts_start.timestamp(),
            "ts_stop": stopts,
            "isfinite": self.isfinite,
        }


@dataclass
class TaskInfo:
    """Stores a tasks runtime information"""

    name: str
    purpose: str
    tasktype: TaskType
    duration: TaskDuration
    state: TaskState = TaskState.CREATED
    resume_event: asyncio.Event = asyncio.Event()
    finalized: bool = False
    scheduled: bool = False

    def tostring(self):
        """Converts object to string representation"""
        return (
            "TaskInfo("
            f"Name='{self.name}'"
            f"Purpose='{self.purpose}'"
            f"Type={self.tasktype.value},"
            f"State={self.state.value},"
            f"Finalized={self.finalized},"
            f"Scheduled={self.finalized},"
            f"Duration={self.duration.tostring()}"
            ")"
        )

    def tojson(self) -> dict:
        """Converts object to json representation"""
        return {
            "Name": self.name,
            "Purpose": self.purpose,
            "Type": self.tasktype.value,
            "State": self.state.value,
            "Finalized": self.finalized,
            "Scheduled": self.finalized,
            "Duration": self.duration.tojson(),
        }


@dataclass
class TaskInfoResult:
    """Contains result info for tasks"""

    taskid: str
    started_at: datetime
    stopped_at: datetime
    purpose: str
    id_object: str
    id_instance: str
    id_owner: int
    state: str
    result: Optional[Any]

    def tojson(self) -> dict:
        """Converts object to json"""
        return {
            "id_task": self.taskid,
            "id_object": self.id_object,
            "id_instance": self.id_instance,
            "id_owner": self.id_owner,
            "result": self.result,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "task_purpose": self.purpose,
            "task_state": self.state,
        }


# pylint: disable=too-many-arguments
class TaskObject:
    """The actual TaskObject being controlled"""

    def __init__(
        self,
        task: asyncio.Task,
        args: TaskArguments,
        info: TaskInfo,
        id_owner: int,
        id_object: str,
        id_instance: str,
    ):
        self.args = args
        self.info = info
        self.task = task
        self.id_owner = id_owner
        self.id_object = id_object
        self.id_instance = id_instance
        self.result: TaskResult = TaskResult()

    async def join(self):
        """Joins the task until finished"""
        while True:
            if self.task.done():
                break
            if self.info.duration.ts_stop <= datetime.now():
                break
            await asyncio.sleep(0.2)
        if self.task.done() is False:
            await self.cancel()
            log_info(f"Task killed   : {self.info.name}")
        log_info(f"Task joined   : {self.info.name}")

    async def cancel(self):
        """Cancels current task"""
        if self.task is not None:
            self.task.cancel()

    def tostring(self):
        """Converts object to string representation"""
        return (
            f"Task(Info={self.info.tostring()}, "
            f"Args={self.args.tostring()},"
            f"Result={self.result.tostring()})"
        )

    def tojson(self) -> dict:
        """Converts object to json representation"""
        info = self.info.tojson()
        print(f"TOOLS_INFO: {info}")
        return {
            "info": info,
            "args": self.args.tojson(),
            "result": self.result.tojson(),
        }

    def toinfo(self) -> TaskInfoResult:
        """Converts object to json representation"""
        return create_taskinfo_result(self)


def create_taskinfo_result(task: ScheduledTask) -> TaskInfoResult:
    """Creates task info result"""
    state = "running"
    if task.finalized:
        state = "final"
    return TaskInfoResult(
        task.id_task,
        task.started_at,
        task.stopped_at,
        task.tasktype,
        task.id_object,
        task.id_instance,
        task.id_owner,
        state,
        {},
    )


@dataclass
class TaskCollection:
    """Collection of Tasks being maintained"""

    tasks_current: dict[str, ScheduledTask] = field(default_factory=dict)
    tasks_finalized: dict[str, ScheduledTask] = field(default_factory=dict)
    watchdog_task: Optional[asyncio.Task] = None
    watchdog_enabled: bool = False

    def get_task(self, taskid: str) -> Optional[ScheduledTask]:
        """Returns list of current tasks"""
        result = None

        if taskid in self.tasks_current:
            result = self.tasks_current[taskid]
        elif taskid in self.tasks_finalized:
            result = self.tasks_finalized[taskid]

        return result

    def tostring(self):
        """Converts object to string representation"""

        cur = []
        for _, val in self.tasks_current.items():
            cur.append(create_taskinfo_result(val).to_json())
        fin = []
        for _, val in self.tasks_finalized.items():
            fin.append(create_taskinfo_result(val).to_json())

        return (
            f"TaskCollection(current={cur}, "
            f"finalized={json.dumps(fin)},"
            f"watchdog_enabled={self.watchdog_enabled}),"
        )

    def tojson(self) -> dict:
        """Converts object to json representation"""
        cur = []
        for _, val in self.tasks_current.items():
            cur.append(val.toinfo().tojson())
        fin = []
        for _, val in self.tasks_finalized.items():
            fin.append(val.toinfo().tojson())
        return {
            "current": cur,
            "finalized": fin,
            "watchdog_enabled": self.watchdog_enabled,
        }
