"""Limit Tasks"""

from dataclasses import asdict
from enum import Enum
from app.daas.common.enums import BackendName
from app.daas.common.model import RessourceInfo
from app.daas.resources.limits.ressource_limits import RessourceLimits
from app.qweb.common.common import TaskArgs
from app.qweb.common.qweb_tools import get_backend_component
from app.qweb.processing.processor import QwebResult
from app.daas.common.ctx import get_request_object_optional, log_task_arguments


class LimitTask(Enum):
    """Limit tasktype"""

    LIMIT_GET = "LIMIT_GET"
    LIMIT_PUT = "LIMIT_PUT"
    LIMIT_REMOVE = "LIMIT_REMOVE"
    LIMIT_LIST = "LIMIT_LIST"


async def limit_get(args: TaskArgs) -> QwebResult:
    """Returns specified limit"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", RessourceInfo)
    if entity is not None:
        return QwebResult(200, asdict(entity))
    return QwebResult(400, {}, 1, "No limit found")


async def limit_put(args: TaskArgs) -> QwebResult:
    """Stores limit for user"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    reqargs = args.req.request_context.request_args
    entity = RessourceInfo(
        reqargs["id_owner"],
        reqargs["vm_max"],
        reqargs["container_max"],
        reqargs["obj_max"],
        reqargs["cpu_max"],
        reqargs["mem_max"],
        reqargs["dsk_max"],
    )
    limiter = await get_backend_component(BackendName.LIMITS, RessourceLimits)
    await limiter.put_user_limit(reqargs["id_owner"], entity)
    return QwebResult(200, {})


async def limit_remove(args: TaskArgs) -> QwebResult:
    """Removes limit for user"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", RessourceInfo)
    limiter = await get_backend_component(BackendName.LIMITS, RessourceLimits)
    if entity is not None:
        await limiter.remove_user_limit(entity.id_owner)
    return QwebResult(200, {})


async def limit_list(args: TaskArgs) -> QwebResult:
    """Lists limits for user"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", list)
    if isinstance(entity, list):
        return QwebResult(200, entity)
    return QwebResult(400, {}, 1, "Result has invalid type (list)")
