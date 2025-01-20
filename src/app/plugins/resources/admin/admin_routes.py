"""VM Blueprints"""

import inspect
from quart import Blueprint
from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.core.task.task_layer import ServiceObject
from app.plugins.resources.admin.admin_tasks import AdminTask
from app.plugins.resources.limits.limits_layer import LimitObject
from app.qweb.processing.processor import ApiProcessorAction, ProcessorType
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)
from app.qweb.service.service_context import LayerObject


perf_args = ["counter", "timestamp"]
backends = [BackendName.ADMIN.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=140000,
        name="get_admin_monitor_info",
        url="/admin/get_monitor_info",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140001,
        name="get_admin_monitor_info_tasks",
        url="/admin/get_monitor_info_tasks",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_TASKS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140002,
        name="get_admin_monitor_info_apps",
        url="/admin/get_monitor_info_apps",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_APPS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140003,
        name="get_admin_monitor_info_files",
        url="/admin/get_monitor_info_files",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_FILES.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140004,
        name="get_admin_monitor_info_websockets",
        url="/admin/get_monitor_info_websockets",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_SOCKETS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140005,
        name="get_admin_monitor_info_host",
        url="/admin/get_monitor_info_host",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_HOST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140006,
        name="get_admin_monitor_info_objects",
        url="/admin/get_monitor_info_objects",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_OBJECTS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140007,
        name="get_admin_monitor_info_utilization",
        url="/admin/get_monitor_info_utilization",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_UTILIZATION.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140008,
        name="get_admin_monitor_info_limits",
        url="/admin/get_monitor_info_limits",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_MONITORING_LIMITS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=["id_owner"],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=140008,
        name="admin_assign_object_to_user",
        url="/admin/assign_obj_to_user",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_ASSIGN_OBJ_TO_USER.value,
        content_type="application/json",
        request_args_mandatory=["id", "owner"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=140008,
        name="admin_assign_app",
        url="/admin/assign_app",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_ASSIGN_APP.value,
        content_type="application/json",
        request_args_mandatory=["appid", "owner"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.APP.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=140009,
        name="admin_task_list",
        url="/admin/tasklist",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_TASK_LIST.value,
        content_type="application/json",
        request_args_mandatory=["id_owner", "id_object", "id_instance", "state"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("entity", ServiceObject.TASKLIST.value, LayerName.TASK.value)
        ],
    ),
    BlueprintInfo(
        endpoint_id=140010,
        name="admin_task_stop",
        url="/admin/taskstop",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=AdminTask.ADMIN_TASK_STOP.value,
        content_type="application/json",
        request_args_mandatory=["id_owner", "id_task", "id_object", "id_instance"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", ServiceObject.TASK.value, LayerName.TASK.value)],
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_admin", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/admin/get_monitor_info")
async def get_admin_monitor_info():
    """Returns monitor info"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_tasks")
async def get_admin_monitor_info_tasks():
    """Returns monitor info tasks"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_apps")
async def get_admin_monitor_info_apps():
    """Returns app infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_files")
async def get_admin_monitor_info_files():
    """Returns file infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_websockets")
async def get_admin_monitor_info_websockets():
    """Returns websocket infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_host")
async def get_admin_monitor_info_host():
    """Returns host infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_objects")
async def get_admin_monitor_info_objects():
    """Returns object infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_utilization")
async def get_admin_monitor_info_utilization():
    """Returns resource utilization infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/get_monitor_info_limits")
async def get_admin_monitor_info_limits():
    """Returns resource limit infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/assign_obj_to_user")
async def admin_assign_object_to_user():
    """Assigns object to user"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/assign_app")
async def admin_assign_app():
    """Assigns app"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/tasklist")
async def admin_task_list():
    """Lists tasks for user, object or instance"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/admin/taskstop")
async def admin_task_stop():
    """Stops task by user, object or instance"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
