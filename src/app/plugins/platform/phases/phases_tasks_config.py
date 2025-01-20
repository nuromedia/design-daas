"""Phases Tasks"""

from enum import Enum
from app.daas.objects.object_application import ApplicationObject
from app.qweb.common.common import TaskArgs
from app.qweb.processing.processor import QwebResult
from app.daas.common.model import Application, Environment
from app.daas.objects.base_object import DaasBaseObject
from app.daas.objects.object_container import ContainerObject
from app.daas.objects.object_machine import MachineObject
from app.daas.common.ctx import (
    create_response_url_start,
    get_request_object,
    get_request_object_optional,
    log_task_arguments,
)


class ConfigurationTask(Enum):
    """Environment tasktype"""

    PHASES_CFG_APPLIST = "PHASES_CFG_APPLIST"
    PHASES_CFG_TASKLIST = "PHASES_CFG_TASKLIST"
    PHASES_CFG_SET_TARGET = "PHASES_CFG_SET_TARGET"
    PHASES_CFG_FROM_APP = "PHASES_CFG_FROM_APP"


async def cfg_set_target(args: TaskArgs) -> QwebResult:
    """Sets target for object or environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object_optional(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if isinstance(obj, MachineObject | ContainerObject):
        return await obj.cfg_set_target(reqargs["target"], env, reqargs)
    return QwebResult(400, {}, 1, f"Object has invalid type: {obj}")


async def cfg_applist(args: TaskArgs) -> QwebResult:
    """Sets applist for object or environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object_optional(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if isinstance(obj, MachineObject | ContainerObject):
        return await obj.cfg_applist(reqargs["applist"], env, reqargs)
    return QwebResult(400, {}, 1, f"Object has invalid type: {obj}")


async def cfg_tasklist(args: TaskArgs) -> QwebResult:
    """Sets tasklist for object or environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    env = get_request_object_optional(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if isinstance(obj, MachineObject | ContainerObject):
        return await obj.cfg_tasklist(reqargs["tasklist"], env, reqargs)
    return QwebResult(400, {}, 1, f"Object has invalid type: {obj}")


async def cfg_from_app(args: TaskArgs) -> QwebResult:
    """Sets config from app for object or environment"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    obj = get_request_object(args.ctx, "obj", DaasBaseObject)
    app = get_request_object(args.ctx, "app", ApplicationObject)
    env = get_request_object_optional(args.ctx, "env", Environment)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if isinstance(obj, MachineObject | ContainerObject):
        file = await app.get_file()
        files = []
        if file is not None:
            files.append(file)
        installer = await app.get_installer()
        installers = []
        if installer != "":
            installers.append(installer)
        return await obj.cfg_install(
            files, installers, reqargs["id_owner"], env, reqargs
        )
    return QwebResult(400, {}, 1, f"Object has invalid type: {obj}")
