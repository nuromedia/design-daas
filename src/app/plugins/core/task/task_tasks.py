"""Task tasks"""

from enum import Enum
from app.qweb.common.common import TaskArgs
from app.qweb.processing.processor import QwebResult
from app.qweb.service.service_tasks import ScheduledTask
from app.daas.common.ctx import (
    get_request_object,
    log_task_arguments,
)


class TaskTask(Enum):
    """VM tasktype"""

    TASK_GET = "TASK_GET"
    TASK_STOP = "TASK_STOP"
    TASK_LIST = "TASK_LIST"
    TASK_STATUS = "TASK_STATUS"


async def task_get(args: TaskArgs) -> QwebResult:
    """Returns specified task object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", ScheduledTask)
    if entity is not None:
        return QwebResult(200, entity.to_json())
    return QwebResult(400, {}, 1, "No task")


async def task_stop(args: TaskArgs) -> QwebResult:
    """Stops specified task object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", ScheduledTask)
    if entity is not None:
        stopped = entity.task.cancel()
        if stopped:
            return QwebResult(200, {})
    return QwebResult(400, {}, 1, "No task")


async def task_list(args: TaskArgs) -> QwebResult:
    """Lists specified task objects"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", dict)
    if entity is not None:
        return QwebResult(200, entity)
    return QwebResult(400, {}, 1, "No task")


async def task_status(args: TaskArgs) -> QwebResult:
    """Status of all task objects"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", dict)
    if entity is not None:
        return QwebResult(200, entity)
    return QwebResult(400, {}, 1, "No task")
