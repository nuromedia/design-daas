"""VM Blueprints"""

import inspect

from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.storage.files.file_tasks import FileTask
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)
from app.qweb.processing.processor import ApiProcessorAction, ProcessorType
from quart import Blueprint
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.service.service_context import LayerObject


app_args_create = [
    "id",
    "name",
    "id_file",
    "id_template",
    "os_type",
    "installer",
    "installer_args",
    "installer_type",
    "target",
    "target_args",
    "version",
]
file_args_create = [
    "id",
    "filename",
    "filepath",
    "version",
    "os_type",
]
perf_args = ["counter", "timestamp"]
backends = [BackendName.FILE.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=80000,
        name="files_get",
        url="/files/get",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_GET.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.FILE.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=80001,
        name="files_delete",
        url="/files/delete",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_DELETE.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.FILE.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=80002,
        name="files_delete_shared",
        url="/files/delete_shared",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_DELETE_SHARED.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.FILE.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=80003,
        name="files_list",
        url="/files/list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_LIST.value,
        content_type="application/json",
        request_args_mandatory=["choice"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80004,
        name="files_create",
        url="/files/create",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_CREATE.value,
        content_type="application/json",
        request_args_mandatory=file_args_create,
        request_args_optional=[],
        request_args_file=["file"],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.FILE.value, LayerName.DB.value)],
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80005,
        name="files_update",
        url="/files/update",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_UPDATE.value,
        content_type="application/json",
        request_args_mandatory=file_args_create,
        request_args_file=["file"],
        request_args_optional=[],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.FILE.value, LayerName.DB.value)],
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80006,
        name="files_create_shared",
        url="/files/create_shared",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_CREATE_SHARED.value,
        content_type="application/json",
        request_args_mandatory=file_args_create,
        request_args_optional=[],
        request_args_file=["file"],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.FILE.value, LayerName.DB.value)],
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80007,
        name="files_update_shared",
        url="/files/update_shared",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.FILE_UPDATE_SHARED.value,
        content_type="application/json",
        request_args_mandatory=file_args_create,
        request_args_file=["file"],
        request_args_optional=[],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.FILE.value, LayerName.DB.value)],
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80008,
        name="app_get",
        url="/apps/get",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_GET.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=80009,
        name="app_delete",
        url="/apps/delete",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_DELETE.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=80010,
        name="app_delete_shared",
        url="/apps/delete_shared",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_DELETE_SHARED.value,
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=80011,
        name="app_list",
        url="/apps/list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_LIST.value,
        content_type="application/json",
        request_args_mandatory=["choice"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80012,
        name="app_create",
        url="/apps/create",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_CREATE.value,
        content_type="application/json",
        request_args_mandatory=app_args_create,
        request_args_optional=[],
        request_args_file=["file"],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80013,
        name="app_update",
        url="/apps/update",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_UPDATE.value,
        content_type="application/json",
        request_args_mandatory=app_args_create,
        request_args_file=["file"],
        request_args_optional=[],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80014,
        name="app_create_shared",
        url="/apps/create_shared",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_CREATE_SHARED.value,
        content_type="application/json",
        request_args_mandatory=app_args_create,
        request_args_optional=[],
        request_args_file=["file"],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=80015,
        name="app_update_shared",
        url="/apps/update_shared",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=FileTask.APP_UPDATE_SHARED.value,
        content_type="application/json",
        request_args_mandatory=app_args_create,
        request_args_file=["file"],
        request_args_optional=[],
        request_args_common=perf_args,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
        backends=backends,
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_files", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/files/get")
async def files_get():
    """Returns specified file object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/files/delete")
async def files_delete():
    """Deletes specified file object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/files/delete_shared")
async def files_delete_shared():
    """Deletes specified shared file object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/files/list")
async def files_list():
    """Lists specified file objects"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/files/create")
async def files_create():
    """Creates specified file object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/files/update")
async def files_update():
    """Update specified file object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/files/create_shared")
async def files_create_shared():
    """Creates specified shared file object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/files/update_shared")
async def files_update_shared():
    """Update specified shared file object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/get")
async def app_get():
    """Returns specified app object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/delete")
async def app_delete():
    """Deletes specified app object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/delete_shared")
async def app_delete_shared():
    """Deletes specified shared app object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/list")
async def app_list():
    """Lists specified app objects"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/create")
async def app_create():
    """Creates specified app object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/update")
async def app_update():
    """Update specified app object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/create_shared")
async def app_create_shared():
    """Creates specified shared app object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/apps/update_shared")
async def app_update_shared():
    """Update specified shared app object"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
