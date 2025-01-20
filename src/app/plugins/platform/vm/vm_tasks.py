"""VM Tasks"""

from enum import Enum
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.object_machine import MachineObject, get_empty_machine_object
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.qweb.common.common import TaskArgs
from app.qweb.processing.processor import QwebResult
from app.daas.common.ctx import (
    create_response_url_start,
    create_response_url_stop,
    get_backend_component,
    get_request_object,
    get_request_object_optional,
    log_task_arguments,
)


class VMTask(Enum):
    """VM tasktype"""

    VM_LIST = "VM_LIST"
    VM_STATUS = "VM_STATUS"
    VM_CONFIG_GET = "VM_CONFIG_GET"
    VM_CONFIG_SET_PRE = "VM_CONFIG_SET_PRE"
    VM_CONFIG_SET_POST = "VM_CONFIG_SET_POST"
    VM_SNAPSHOT_LIST = "VM_SNAPSHOT_LIST"
    VM_SNAPSHOT_CREATE = "VM_SNAPSHOT_CREATE"
    VM_SNAPSHOT_ROLLBACK = "VM_SNAPSHOT_ROLLBACK"
    VM_TEMPLATE_CONVERT = "VM_TEMPLATE_CONVERT"
    VM_START = "VM_START"
    VM_STOP = "VM_STOP"
    VM_DELETE = "VM_DELETE"
    VM_CREATE = "VM_CREATE"
    VM_CLONE = "VM_CLONE"


async def vmcreate(args: TaskArgs) -> QwebResult:
    """Create vm object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", MachineObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if entity is None:
        entity = await get_empty_machine_object(args.user.id_user, **reqargs)
        return await entity.baseimage_create(reqargs)
    return QwebResult(400, {}, 1, "object already exists")


async def vmclone(args: TaskArgs) -> QwebResult:
    """Clones vm object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    old = get_request_object(args.ctx, "old", MachineObject)
    entity = get_request_object_optional(args.ctx, "new", MachineObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if entity is None:
        if old is not None:
            reqargs["cores"] = old.hw_cpus
            reqargs["memsize"] = old.hw_memory
            reqargs["disksize"] = old.hw_disksize
            entity = await get_empty_machine_object(args.user.id_user, **reqargs)
            return await entity.baseimage_clone(reqargs["id"], reqargs)
        return QwebResult(400, {}, 1, "No object to clone from")
    return QwebResult(400, {}, 1, "object already exists")


async def vmdelete(args: TaskArgs) -> QwebResult:
    """Deletes vm object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    deleted = await entity.baseimage_delete()
    if deleted is True:
        return QwebResult(200, {})
    return QwebResult(400, {}, 1, "Object not deleted")


async def vmstart(args: TaskArgs) -> QwebResult:
    """Starts vm object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    reqargs = args.req.request_context.request_args
    connect = "connect" in reqargs
    inst = await entity.start(args.user.id_user, connect, "run-debug")
    if inst is not None:
        return await create_response_url_start(connect, inst.id)
    return QwebResult(400, {}, 1, "No instance")


async def vmstop(args: TaskArgs) -> QwebResult:
    """Starts vm object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    if isinstance(entity.app, MachineObject):
        stopped = await entity.app.stop(entity, True)
        return await create_response_url_stop(stopped)
    return QwebResult(400, {}, 1, "Invalid instance type")


async def vmconfig_get(args: TaskArgs) -> QwebResult:
    """Retrieves vm configuration"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    return await entity.vmconfig_get()


async def vmconfig_set_pre_install(args: TaskArgs) -> QwebResult:
    """Sets vm configuration (pre)"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    reqargs = args.req.request_context.request_args
    return await entity.vmconfig_set_pre_install(reqargs)


async def vmconfig_set_post_install(args: TaskArgs) -> QwebResult:
    """Sets vm configuration (post)"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    reqargs = args.req.request_context.request_args
    return await entity.vmconfig_set_post_install(reqargs)


async def vmsnapshot_list(args: TaskArgs) -> QwebResult:
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    return await entity.vmsnapshot_list()


async def vmsnapshot_create(args: TaskArgs) -> QwebResult:
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    reqargs = args.req.request_context.request_args
    return await entity.vmsnapshot_create(reqargs["snapname"], reqargs["desc"])


async def vmsnapshot_rollback(args: TaskArgs) -> QwebResult:
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    reqargs = args.req.request_context.request_args
    return await entity.vmsnapshot_rollback(reqargs["snapname"])


async def vmstatus(args: TaskArgs) -> QwebResult:
    """Get vm status from proxmox api"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    data = await entity.status()
    return QwebResult(200, data)


async def vmtemplate_convert(args: TaskArgs) -> QwebResult:
    """Converts vm object to template via proxmox api"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", MachineObject)
    reqargs = args.req.request_context.request_args
    return await entity.vmtemplate_convert(reqargs["disk"])


async def vmlist(args: TaskArgs) -> QwebResult:
    """Configure dhcp"""
    # TODO: Add detailed sorting for users and daas objects
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    api = get_backend_component(args.ctx, "vm", ApiProxmox)
    response, data = await api.prox_vmlist(api.config_prox.node)
    if response.status == 200 and "data" in data:
        return QwebResult(response.status, data["data"], 0, "")
    return QwebResult(response.status, {}, 0, "No data in api response")
