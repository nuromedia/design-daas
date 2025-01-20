"""Phases Blueprints"""

import inspect

from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.platform.phases.phases_tasks import PhasesTask
from app.plugins.platform.phases.phases_tasks_config import ConfigurationTask
from app.plugins.platform.phases.phases_tasks_env import EnvironmentTask
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
backends = [BackendName.PHASES.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=110000,
        name="baseimage_create",
        url="/phases/baseimage_create",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_CREATE.value,
        content_type="application/json",
        request_args_mandatory=[
            "id",
            "obj_type",
            "name",
            "cores",
            "memsize",
            "disksize",
            "viewer_contype",
            "viewer_resolution",
        ],
        request_args_optional=[
            "os_type",
            "rootimage",
            "dockerfile",
            "kb",
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
        endpoint_id=110001,
        name="baseimage_clone",
        url="/phases/baseimage_clone",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_CLONE.value,
        content_type="application/json",
        request_args_mandatory=["id", "newid", "name"],
        request_args_optional=[
            "ceph_public",
            "ceph_shared",
            "ceph_user",
            "kb",
            "snapname",
        ],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("old", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("new", DBObject.NEWOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110002,
        name="baseimage_delete",
        url="/phases/baseimage_delete",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_DELETE.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110003,
        name="baseimage_start",
        url="/phases/baseimage_start",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_START.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=["connect"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110004,
        name="baseimage_stop",
        url="/phases/baseimage_stop",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_STOP.value,
        content_type="application/json",
        request_args_mandatory=["id_instance"],
        request_args_optional=["force"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110005,
        name="baseimage_finalize",
        url="/phases/baseimage_finalize",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_FINALIZE.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110006,
        name="baseimage_object_status",
        url="/phases/object_status",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_STATUS.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110007,
        name="baseimage_list",
        url="/phases/object_list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_LIST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["detailed", "onlyuser", "onlydaas"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=110008,
        name="environment_create",
        url="/phases/environment_create",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENV_CREATE.value,
        content_type="application/json",
        request_args_mandatory=["id", "name"],
        request_args_optional=["dockerfile"],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110009,
        name="environment_get",
        url="/phases/environment_get",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENV_GET.value,
        content_type="application/json",
        request_args_mandatory=["id", "name"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110010,
        name="environments_get",
        url="/phases/environments_get",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENVS_GET.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110011,
        name="environment_delete",
        url="/phases/environment_delete",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENV_DELETE.value,
        content_type="application/json",
        request_args_mandatory=["id", "name"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110012,
        name="environment_start",
        url="/phases/environment_start",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENV_START.value,
        content_type="application/json",
        request_args_mandatory=["id", "name"],
        request_args_optional=["connect"],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110013,
        name="environment_run",
        url="/phases/environment_run",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENV_RUN.value,
        content_type="application/json",
        request_args_mandatory=["id", "env"],
        request_args_optional=["connect"],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110014,
        name="environment_stop",
        url="/phases/environment_stop",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENV_STOP.value,
        content_type="application/json",
        request_args_mandatory=["id", "name"],
        request_args_optional=["force"],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110015,
        name="environment_finalize",
        url="/phases/environment_finalize",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=EnvironmentTask.PHASES_ENV_FINALIZE.value,
        content_type="application/json",
        request_args_mandatory=["id", "name"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110016,
        name="cfg_set_target",
        url="/phases/cfg_set_target",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ConfigurationTask.PHASES_CFG_SET_TARGET.value,
        content_type="application/json",
        request_args_mandatory=["id", "env", "target"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110017,
        name="cfg_applist",
        url="/phases/cfg_applist",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ConfigurationTask.PHASES_CFG_APPLIST.value,
        content_type="application/json",
        request_args_mandatory=["id", "env", "applist"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110018,
        name="cfg_tasklist",
        url="/phases/cfg_tasklist",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ConfigurationTask.PHASES_CFG_TASKLIST.value,
        content_type="application/json",
        request_args_mandatory=["id", "env", "tasklist"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110019,
        name="cfg_from_app",
        url="/phases/cfg_from_application",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ConfigurationTask.PHASES_CFG_FROM_APP.value,
        content_type="application/json",
        request_args_mandatory=["id", "env", "appid"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("obj", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("env", DBObject.ENVBYOBJ.value, LayerName.DB.value),
            LayerObject("app", DBObject.APP.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110020,
        name="baseimage_create_from_app",
        url="/phases/baseimage_create_from_app",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_CREATE_FROM_APP.value,
        content_type="application/json",
        request_args_mandatory=["id", "env", "appid", "name"],
        request_args_optional=["run"],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("new", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("app", DBObject.APP.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=110021,
        name="baseimage_clone_from_app",
        url="/phases/baseimage_clone_from_app",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=PhasesTask.PHASES_BASEIMAGE_CLONE_FROM_APP.value,
        content_type="application/json",
        request_args_mandatory=["newid", "env", "appid", "name"],
        request_args_optional=["id", "run"],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("old", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("new", DBObject.NEWOBJ.value, LayerName.DB.value),
            LayerObject("app", DBObject.APP.value, LayerName.DB.value),
            LayerObject("template", DBObject.OBJBYAPP.value, LayerName.DB.value),
        ],
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_phases", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/phases/baseimage_create")
async def baseimage_create():
    """Creates new object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/baseimage_clone")
async def baseimage_clone():
    """Clones object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/baseimage_start")
async def baseimage_start():
    """Starts object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/baseimage_stop")
async def baseimage_stop():
    """Stop object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/baseimage_delete")
async def baseimage_delete():
    """Deletes object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/baseimage_finalize")
async def baseimage_finalize():
    """Finalizes object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/object_status")
async def baseimage_object_status():
    """Returns object status"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/object_list")
async def baseimage_list():
    """Lists objects"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environment_create")
async def environment_create():
    """Create environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environment_get")
async def environment_get():
    """Returns environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environments_get")
async def environments_get():
    """Returns environment list"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environment_delete")
async def environment_delete():
    """Deletes environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environment_start")
async def environment_start():
    """Starts environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environment_run")
async def environment_run():
    """Runs environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environment_stop")
async def environment_stop():
    """Stops environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/environment_finalize")
async def environment_finalize():
    """Finalizes environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/cfg_set_target")
async def cfg_set_target():
    """Sets target for object or environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/cfg_applist")
async def cfg_applist():
    """Sets applist for object or environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/cfg_tasklist")
async def cfg_tasklist():
    """Sets tasklist for object or environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/cfg_from_application")
async def cfg_from_app():
    """Sets config from app for object or environment"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/baseimage_create_from_app")
async def baseimage_create_from_app():
    """Creates object from app"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/phases/baseimage_clone_from_app")
async def baseimage_clone_from_app():
    """Clones object from app"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
