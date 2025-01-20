"""VM Blueprints"""

import inspect

from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.platform.vm.vm_tasks import VMTask
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)
from app.qweb.processing.processor import ApiProcessorAction, ProcessorType
from quart import Blueprint
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.service.service_context import LayerObject


perf_args = ["counter", "timestamp"]
backends = [BackendName.VM.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=60000,
        name="vmlist",
        url="/vm/list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_LIST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["onlyuser", "onlydaas", "detailed"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=60001,
        name="vmstatus",
        url="/vm/status",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_STATUS.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60002,
        name="vmconfig_get",
        url="/vm/config_get",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_CONFIG_GET.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60003,
        name="vmconfig_set_pre_install",
        url="/vm/config_set_pre_install",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_CONFIG_SET_PRE.value,
        content_type="application/json",
        request_args_mandatory=[
            "id",
            "name",
            "os_type",
            "cores",
            "memsize",
            "disksize",
            "iso_installer",
            "keyboard_layout",
        ],
        request_args_optional=["ceph_pool"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60004,
        name="vmconfig_set_post_install",
        url="/vm/config_set_post_install",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_CONFIG_SET_POST.value,
        content_type="application/json",
        request_args_mandatory=["id", "name", "keyboard_layout"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60005,
        name="vmsnapshot_list",
        url="/vm/snapshot_list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_SNAPSHOT_LIST.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60006,
        name="vmsnapshot_create",
        url="/vm/snapshot_create",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_SNAPSHOT_CREATE.value,
        content_type="application/json",
        request_args_mandatory=["id", "snapname", "desc"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60007,
        name="vmsnapshot_rollback",
        url="/vm/snapshot_rollback",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_SNAPSHOT_ROLLBACK.value,
        content_type="application/json",
        request_args_mandatory=["id", "snapname"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60008,
        name="vmtemplate_convert",
        url="/vm/template_convert",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_TEMPLATE_CONVERT.value,
        content_type="application/json",
        request_args_mandatory=["id", "disk"],
        request_args_optional=["kb"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60009,
        name="vmstart",
        url="/vm/start",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_START.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env"],
        request_args_optional=["connect"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60010,
        name="vmstop",
        url="/vm/stop",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_STOP.value,
        content_type="application/json",
        request_args_mandatory=["id_instance"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60011,
        name="vmdelete",
        url="/vm/delete",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_DELETE.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60012,
        name="vmcreate",
        url="/vm/create",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_CREATE.value,
        content_type="application/json",
        request_args_mandatory=[
            "id",
            "name",
            "cores",
            "memsize",
            "disksize",
            "kb",
            "os_type",
            "viewer_contype",
            "viewer_resolution",
        ],
        request_args_optional=[
            "ceph_public",
            "ceph_shared",
            "ceph_user",
            "viewer_resize",
            "viewer_scale",
        ],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=60012,
        name="vmclone",
        url="/vm/vm",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=VMTask.VM_CLONE.value,
        content_type="application/json",
        request_args_mandatory=["id", "newid", "name", "kb"],
        request_args_optional=["ceph_public", "ceph_shared", "ceph_user", "snapname"],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("old", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("new", DBObject.NEWOBJ.value, LayerName.DB.value),
        ],
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_vm", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/vm/template_convert")
async def vmtemplate_convert():
    """Converts vm object into template via proxmox api"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/snapshot_create")
async def vmsnapshot_create():
    """Creates snapshots for a specific vm via proxmox api"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/snapshot_rollback")
async def vmsnapshot_rollback():
    """Restores snapshots of a vm via proxmox api"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/snapshot_list")
async def vmsnapshot_list():
    """Lists all snapshots of a vm via proxmox api"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/list")
async def vmlist():
    """Get vm list from proxmox api"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/status")
async def vmstatus():
    """Get vm status from proxmox api"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/config_get")
async def vmconfig_get():
    """Retrieves vm configuration"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/config_set_pre_install")
async def vmconfig_set_pre_install():
    """Sets vm configuration (pre)"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/config_set_post_install")
async def vmconfig_set_post_install():
    """Sets vm configuration (post)"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/start")
async def vmstart():
    """Starts vm object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/stop")
async def vmstop():
    """Stops vm object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/create")
async def vmcreate():
    """Creates vm object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/clone")
async def vmclone():
    """Creates vm object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/vm/delete")
async def vmdelete():
    """Deletes vm object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
