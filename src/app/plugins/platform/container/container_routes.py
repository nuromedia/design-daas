"""Container Blueprints"""

import inspect
from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.platform.container.container_tasks import ContainerTask
from app.qweb.processing.processor import ApiProcessorAction, ProcessorType
from quart import Blueprint
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.service.service_context import LayerObject
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)


default_args = ["id", "id_env"]
perf_args = ["counter", "timestamp"]
backends = [BackendName.CONTAINER.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=70000,
        name="docker_daemon_info",
        url="/container/daemon_info",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_DAEMON_INFO.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=70001,
        name="docker_image_inspect",
        url="/container/image_inspect",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_IMAGE_INSPECT.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=70002,
        name="docker_image_build",
        url="/container/image_build",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_IMAGE_BUILD.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=70003,
        name="docker_image_delete",
        url="/container/image_delete",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_IMAGE_DELETE.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=70004,
        name="docker_image_list",
        url="/container/image_list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_IMAGE_LIST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["onlyuser", "onlydaas", "detailed"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=70005,
        name="container_start",
        url="/container/container_start",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_START.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=["connect"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=70006,
        name="container_stop",
        url="/container/container_stop",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_STOP.value,
        content_type="application/json",
        request_args_mandatory=["id_instance"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=70007,
        name="docker_image_create",
        url="/container/image_create",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_IMAGE_CREATE.value,
        content_type="application/json",
        request_args_mandatory=[
            "id",
            "name",
            "cores",
            "memsize",
            "disksize",
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
        request_args_file=["dockerfile"],
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=70008,
        name="docker_image_create_root",
        url="/container/image_create_root",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_IMAGE_CREATE_ROOT.value,
        content_type="application/json",
        request_args_mandatory=[
            "id",
            "name",
            "cores",
            "memsize",
            "disksize",
            "rootimage",
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
        endpoint_id=70009,
        name="docker_image_clone",
        url="/container/image_clone",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_IMAGE_CLONE.value,
        content_type="application/json",
        request_args_mandatory=["id", "newid", "name"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("old", DBObject.OBJ.value, LayerName.DB.value),
            LayerObject("new", DBObject.NEWOBJ.value, LayerName.DB.value),
        ],
    ),
    BlueprintInfo(
        endpoint_id=70010,
        name="container_list",
        url="/container/container_list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_LIST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["onlyuser", "onlydaas", "detailed"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=70011,
        name="container_logs",
        url="/container/container_logs",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ContainerTask.CONT_LOG.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_container", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/container/daemon_info")
async def docker_daemon_info():
    """Returns info from utilized docker daemon"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/image_inspect")
async def docker_image_inspect():
    """Returns info from specified docker image"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/image_build")
async def docker_image_build():
    """Builds specified docker image"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/image_create")
async def docker_image_create():
    """Creates specified container object by using uploaded dockerfile"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/image_create_root")
async def docker_image_create_root():
    """Creates specified container object by using template file"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/image_clone")
async def docker_image_clone():
    """Clones container image"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/image_delete")
async def docker_image_delete():
    """Deletes specified docker image"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/image_list")
async def docker_image_list():
    """Lists docker images"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/container_start")
async def container_start():
    """Starts container"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/container_stop")
async def container_stop():
    """Stops container"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/container_list")
async def container_list():
    """Lists container"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/container/container_logs")
async def container_logs():
    """Returns container logs"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
