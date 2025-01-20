"""Phases Tasks"""

from enum import Enum
from typing import Optional
from app.daas.common.ctx import (
    create_response_url_start,
    get_request_object,
    get_request_object_optional,
    log_task_arguments,
)
from app.daas.common.enums import BackendName
from app.daas.objects.base_object import DaasBaseObject
from app.daas.objects.object_application import ApplicationObject
from app.daas.objects.object_container import (
    ContainerObject,
    get_empty_container_object,
)
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.object_machine import MachineObject, get_empty_machine_object
from app.daas.resources.info.sysinfo import Systeminfo
from app.plugins.platform.phases.enums import PhasesSystemTask
from app.qweb.common.common import TaskArgs
from app.qweb.common.qweb_tools import get_backend_component, run_system_task
from app.qweb.processing.processor import QwebResult

DEFAULT_VM_CORES = 4
DEFAULT_VM_MEMORY = 4 * 1024**1
DEFAULT_VM_DISKSIZE_WIN = 64 * 1024**3
DEFAULT_VM_DISKSIZE_LINUX = 32 * 1024**3
DEFAULT_VM_OS = "win10"
DEFAULT_VM_KB = "de"
DEFAULT_CNT_CORES = 2
DEFAULT_CNT_MEMORY = 2 * 1024**1
DEFAULT_CNT_DISKSIZE_WIN = 12 * 1024**2
DEFAULT_CNT_DISKSIZE_LINUX = 12 * 1024 * 2
DEFAULT_CNT_IMAGE = "wine"


class PhasesTask(Enum):
    """VM tasktype"""

    PHASES_BASEIMAGE_CREATE = "PHASES_BASEIMAGE_CREATE"
    PHASES_BASEIMAGE_CLONE = "PHASES_BASEIMAGE_CLONE"
    PHASES_BASEIMAGE_FINALIZE = "PHASES_BASEIMAGE_FINALIZE"
    PHASES_BASEIMAGE_DELETE = "PHASES_BASEIMAGE_DELETE"
    PHASES_BASEIMAGE_START = "PHASES_BASEIMAGE_START"
    PHASES_BASEIMAGE_STOP = "PHASES_BASEIMAGE_STOP"
    PHASES_BASEIMAGE_STATUS = "PHASES_BASEIMAGE_STATUS"
    PHASES_BASEIMAGE_LIST = "PHASES_BASEIMAGE_LIST"
    PHASES_BASEIMAGE_CLONE_FROM_APP = "PHASES_BASEIMAGE_CLONE_FROM_APP"
    PHASES_BASEIMAGE_CREATE_FROM_APP = "PHASES_BASEIMAGE_CREATE_FROM_APP"


async def baseimage_create(args: TaskArgs) -> QwebResult:
    """Creates object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", DaasBaseObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if entity is None:
        if reqargs["obj_type"] == "vm":
            entity = await get_empty_machine_object(args.user.id_user, **reqargs)
            return await entity.baseimage_create(reqargs)
        elif reqargs["obj_type"] == "container":
            entity = await get_empty_container_object(args.user.id_user, **reqargs)
            return await entity.baseimage_create(reqargs)
    return QwebResult(400, {}, 1, "object not created")


async def baseimage_clone(args: TaskArgs) -> QwebResult:
    """Clones object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    old = get_request_object(args.ctx, "old", DaasBaseObject)
    entity = get_request_object_optional(args.ctx, "new", DaasBaseObject)
    reqargs = args.req.request_context.request_args.copy()
    userid = args.user.id_user
    if entity is None:
        reqargs["id_owner"] = userid
        reqargs["cores"] = old.hw_cpus
        reqargs["memsize"] = old.hw_memory
        reqargs["disksize"] = old.hw_disksize
        entity = await _create_empty_object(reqargs, old, userid)
        if entity is not None:
            return await entity.baseimage_clone(reqargs["id"], reqargs)
        return QwebResult(400, {}, 1, "No object to clone from")
    return QwebResult(400, {}, 1, "object already exists")


async def baseimage_finalize(args: TaskArgs) -> QwebResult:
    """Finalizes object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", DaasBaseObject)
    if isinstance(entity, MachineObject | ContainerObject):
        return await entity.baseimage_finalize()
    return QwebResult(400, {}, 1, "LayerObject has invalid type")


async def baseimage_delete(args: TaskArgs) -> QwebResult:
    """Deletes object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", DaasBaseObject)
    if isinstance(entity, MachineObject | ContainerObject):
        return await entity.baseimage_delete()
    return QwebResult(400, {}, 1, "LayerObject has invalid type")


async def baseimage_start(args: TaskArgs) -> QwebResult:
    """Starts object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", DaasBaseObject)
    reqargs = args.req.request_context.request_args.copy()
    connect = "connect" in reqargs
    if isinstance(entity, MachineObject | ContainerObject):
        inst = await entity.baseimage_start(args.user.id_user, connect, "run-debug")
        if inst is not None:
            return await create_response_url_start(connect, inst.id)
    return QwebResult(400, {}, 1, "No instance")


async def baseimage_stop(args: TaskArgs) -> QwebResult:
    """Stops object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args.copy()
    force = reqargs["force"] != ""
    if entity is not None:
        if isinstance(entity.app, MachineObject | ContainerObject):
            return await entity.app.baseimage_stop(entity, force)
        return QwebResult(400, {}, 1, "LayerObject has invalid type")
    return QwebResult(400, {}, 2, "No instance")


async def baseimage_status(args: TaskArgs) -> QwebResult:
    """Returns current status of object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", DaasBaseObject)
    if isinstance(entity, MachineObject | ContainerObject):
        return await entity.baseimage_status()
    return QwebResult(400, {}, 1, "LayerObject has invalid type")


async def baseimage_list(args: TaskArgs) -> QwebResult:
    """Returns current status of objects"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    reqargs = args.req.request_context.request_args.copy()
    userid = args.user.id_user
    detailed = "detailed" in reqargs and reqargs["detailed"] != ""
    only_daas = "onlydaas" in reqargs and reqargs["onlydaas"] != ""
    only_user = -1
    if "onlyuser" in reqargs and reqargs["onlyuser"] != "":
        only_user = userid
    sysinfo = await get_backend_component(BackendName.INFO, Systeminfo)
    objs = await sysinfo.get_all_objects(detailed, only_daas, only_user)
    return QwebResult(200, objs)


async def baseimage_clone_from_app(args: TaskArgs) -> QwebResult:
    """Clones object from app"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    app = get_request_object(args.ctx, "app", ApplicationObject)
    old = get_request_object_optional(args.ctx, "old", DaasBaseObject)
    tpl = get_request_object_optional(args.ctx, "template", DaasBaseObject)
    entity = get_request_object_optional(args.ctx, "new", DaasBaseObject)
    reqargs = args.req.request_context.request_args.copy()
    obj = old
    if obj is None:
        obj = tpl
    assert obj is not None
    userid = args.user.id_user
    reqargs["id_owner"] = userid
    reqargs["cores"] = obj.hw_cpus
    reqargs["memsize"] = obj.hw_memory
    reqargs["disksize"] = obj.hw_disksize
    reqargs["newid"] = reqargs["newid"].lower()
    newid = reqargs["newid"]
    if app is not None:
        if entity is None:
            entity = await _create_empty_object(reqargs, obj, userid)
            if entity is not None:
                # if await has_numbers(newid):
                #     reqargs["newid"] = "foo"
                #     newid = reqargs["newid"]
                reqargs["id"] = newid
                entity.id = newid
                cloned = await entity.baseimage_clone(obj.id, reqargs)
                if cloned is not None and cloned.response_code == 200:
                    inst = await entity.baseimage_start(userid, True, "run-clone")
                    if inst is not None:
                        ttype = PhasesSystemTask.PHASES_CLONE_FROM_APP.value
                        targs = {"app": app, "obj": entity, "inst": inst, **reqargs}
                        await run_system_task(ttype, userid, newid, inst.id, targs)
                        return await create_response_url_start(True, inst.id)
                    return QwebResult(400, {}, 1, "Instance not created")
                return QwebResult(400, {}, 2, "Clone object failed")
            return QwebResult(400, {}, 3, "Clone object failed")
        return QwebResult(400, {}, 4, "Object exists")
    return QwebResult(400, {}, 5, "No app")


async def has_numbers(inputstring: str):
    return any(char.isdigit() for char in inputstring)


async def baseimage_create_from_app(args: TaskArgs) -> QwebResult:
    """Creates object from app"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    app = get_request_object(args.ctx, "app", ApplicationObject)
    entity = get_request_object_optional(args.ctx, "new", DaasBaseObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id"] = reqargs["id"].lower()
    userid = args.user.id_user
    reqargs["id_owner"] = userid
    newid = reqargs["id"]
    if app is not None:
        reqargs = await _append_default_ressources(reqargs, app)
        if entity is None:
            entity = await _create_empty_object_by_app(reqargs, app, userid)
            if entity is not None:
                entity.id = newid
                cloned = await entity.baseimage_create(reqargs)
                if cloned is not None and cloned.response_code == 200:
                    inst = await entity.baseimage_start(userid, True, "run-install")
                    if inst is not None:
                        ttype = PhasesSystemTask.PHASES_CREATE_FROM_APP.value
                        targs = {"app": app, "obj": entity, "inst": inst, **reqargs}
                        await run_system_task(ttype, userid, newid, inst.id, targs)
                        return await create_response_url_start(True, inst.id)
                    return QwebResult(400, {}, 1, "Instance not created")
                return QwebResult(400, {}, 2, "Clone object failed")
            return QwebResult(400, {}, 3, "Clone object failed")
        return QwebResult(400, {}, 4, "Object exists")
    return QwebResult(400, {}, 5, "No app")


async def _create_empty_object(
    reqargs: dict, old: DaasBaseObject, userid: int
) -> Optional[MachineObject | ContainerObject]:
    if old is not None:
        entity = None
        if old.object_type == "vm":
            entity = await get_empty_machine_object(userid, **reqargs)
        elif old.object_type == "container":
            entity = await get_empty_container_object(userid, **reqargs)
    return entity


async def _append_default_ressources(reqargs: dict, app: ApplicationObject) -> dict:
    if app.os_type in ("win10", "win11"):
        reqargs["cores"] = DEFAULT_VM_CORES
        reqargs["memsize"] = DEFAULT_VM_MEMORY
        reqargs["disksize"] = DEFAULT_VM_DISKSIZE_WIN
        reqargs["os_type"] = app.os_type
        reqargs["kb"] = DEFAULT_VM_KB
    elif app.os_type == "l26vm":
        reqargs["cores"] = DEFAULT_VM_CORES
        reqargs["memsize"] = DEFAULT_VM_MEMORY
        reqargs["disksize"] = DEFAULT_VM_DISKSIZE_LINUX
        reqargs["os_type"] = "l26"
        reqargs["kb"] = DEFAULT_VM_KB
    elif app.os_type == "l26":
        reqargs["cores"] = DEFAULT_CNT_CORES
        reqargs["memsize"] = DEFAULT_CNT_MEMORY
        reqargs["disksize"] = DEFAULT_CNT_DISKSIZE_WIN
        reqargs["rootimage"] = DEFAULT_CNT_IMAGE
        reqargs["os_type"] = app.os_type
    return reqargs


async def _create_empty_object_by_app(
    reqargs: dict, app: ApplicationObject, userid: int
) -> Optional[MachineObject | ContainerObject]:
    entity = None
    if app.os_type in ("win10", "win11"):
        entity = await get_empty_machine_object(userid, **reqargs)
        entity.os_type = app.os_type
        entity.os_installer = await entity.choose_template_root(entity.os_type)
    if app.os_type in ("l26vm"):
        entity = await get_empty_machine_object(userid, **reqargs)
        entity.os_type = app.os_type
        entity.os_installer = await entity.choose_template_root(entity.os_type)
    if app.os_type in ("l26"):
        entity = await get_empty_container_object(userid, **reqargs)
        entity.os_type = app.os_type
    return entity
