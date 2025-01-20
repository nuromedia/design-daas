"""Phases Tasks"""

from enum import Enum
from app.qweb.common.common import TaskArgs
from app.qweb.processing.processor import QwebResult
from app.daas.common.model import Environment
from app.daas.objects.base_object import DaasBaseObject
from app.daas.objects.object_container import ContainerObject
from app.daas.objects.object_machine import MachineObject
from app.daas.common.ctx import (
    create_response_url_start,
    get_request_object,
    get_request_object_optional,
    log_task_arguments,
)


class EnvironmentTask(Enum):
    """Environment tasktype"""

    PHASES_ENV_CREATE = "PHASES_ENV_CREATE"
    PHASES_ENV_FINALIZE = "PHASES_ENV_FINALIZE"
    PHASES_ENV_DELETE = "PHASES_ENV_DELETE"
    PHASES_ENV_RUN = "PHASES_ENV_RUN"
    PHASES_ENV_START = "PHASES_ENV_START"
    PHASES_ENV_STOP = "PHASES_ENV_STOP"
    PHASES_ENV_GET = "PHASES_ENV_GET"
    PHASES_ENVS_GET = "PHASES_ENVS_GET"


async def environment_create(args: TaskArgs) -> QwebResult:
    """Creates environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object_optional(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if env is None:
        if isinstance(obj, MachineObject):
            return await obj.environment_create(reqargs)
        if isinstance(obj, ContainerObject):
            return await obj.environment_create(reqargs)
    return QwebResult(400, {}, 1, "Env already exists")


async def environment_get(args: TaskArgs) -> QwebResult:
    """Returns environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if isinstance(env, Environment):
        if isinstance(obj, MachineObject):
            return await obj.environment_get(reqargs["name"], reqargs)
        if isinstance(obj, ContainerObject):
            return await obj.environment_get(reqargs["name"], reqargs)
    return QwebResult(400, {}, 1, "No env")


async def environments_get(args: TaskArgs) -> QwebResult:
    """Returns environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", DaasBaseObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if isinstance(entity, MachineObject):
        return await entity.environments_get(reqargs)
    if isinstance(entity, ContainerObject):
        return await entity.environments_get(reqargs)
    return QwebResult(400, {}, 1, "No envs")


async def environment_finalize(args: TaskArgs) -> QwebResult:
    """Finalizes environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if isinstance(obj, MachineObject):
        return await obj.environment_finalize(env, reqargs)
    if isinstance(obj, ContainerObject):
        return await obj.environment_finalize(env, reqargs)
    return QwebResult(400, {}, 1, "Env not finalized")


async def environment_delete(args: TaskArgs) -> QwebResult:
    """Deletes environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object_optional(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if env is not None and isinstance(env, Environment):
        if isinstance(obj, MachineObject):
            return await obj.environment_delete(env, reqargs)
        if isinstance(obj, ContainerObject):
            return await obj.environment_delete(env, reqargs)
    return QwebResult(400, {}, 1, "No env")


async def environment_start(args: TaskArgs) -> QwebResult:
    """Starts environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    connect = "connect" in reqargs and reqargs["connect"] != ""
    objmode = "run-debug"
    if env is not None and isinstance(env, Environment):
        inst = None
        if isinstance(obj, MachineObject):
            inst = await obj.environment_start(
                env, reqargs["id_owner"], connect, objmode, reqargs
            )
        if isinstance(obj, ContainerObject):
            inst = await obj.environment_start(
                env, reqargs["id_owner"], connect, objmode, reqargs
            )
        if inst is not None:
            return await create_response_url_start(connect, inst.id)
        return QwebResult(400, {}, 1, "No instance")
    return QwebResult(400, {}, 1, "No env")


async def environment_run(args: TaskArgs) -> QwebResult:
    """Runs environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    connect = "connect" in reqargs and reqargs["connect"] != ""
    objmode = "run-app"
    if env is not None and isinstance(env, Environment):
        inst = None
        if isinstance(obj, MachineObject | ContainerObject):
            inst = await obj.environment_run(
                env, reqargs["id_owner"], connect, objmode, reqargs
            )
        if inst is not None:
            return await create_response_url_start(connect, inst.id)
        return QwebResult(400, {}, 1, "No instance")
    return QwebResult(400, {}, 1, "No env")


async def environment_stop(args: TaskArgs) -> QwebResult:
    """Deletes environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object_optional(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    force = True if "force" in reqargs else False
    if env is not None and isinstance(env, Environment):
        if isinstance(obj, MachineObject | ContainerObject):
            return await obj.environment_stop(env, force, reqargs)
    return QwebResult(400, {}, 1, "No env")
