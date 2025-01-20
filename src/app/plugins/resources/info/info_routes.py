"""VM Blueprints"""

import inspect
from app.daas.common.enums import BackendName
from app.plugins.resources.info.info_tasks import InfoTask
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)
from app.qweb.processing.processor import ApiProcessorAction, ProcessorType
from quart import Blueprint
from app.qweb.blueprints.blueprint_handler import BlueprintHandler


perf_args = ["counter", "timestamp"]
backends = [BackendName.INFO.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=120000,
        name="dashboard_info",
        url="/monitoring/dashboard_info",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_DASHBOARD.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120001,
        name="get_monitor_info",
        url="/monitoring/get_monitor_info",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120002,
        name="get_monitor_info_tasks",
        url="/monitoring/get_monitor_info_tasks",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_TASKS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120003,
        name="get_monitor_info_apps",
        url="/monitoring/get_monitor_info_apps",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_APPS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120004,
        name="get_monitor_info_files",
        url="/monitoring/get_monitor_info_files",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_FILES.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120005,
        name="get_monitor_info_websockets",
        url="/monitoring/get_monitor_info_websockets",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_SOCKETS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120006,
        name="get_monitor_info_host",
        url="/monitoring/get_monitor_info_host",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_HOST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120007,
        name="get_monitor_info_objects",
        url="/monitoring/get_monitor_info_objects",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_OBJECTS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120008,
        name="get_monitor_info_utilization",
        url="/monitoring/get_monitor_info_utilization",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_UTILIZATION.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
    BlueprintInfo(
        endpoint_id=120009,
        name="get_monitor_info_limits",
        url="/monitoring/get_monitor_info_limits",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InfoTask.INFO_MONITORING_LIMITS.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_info", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/monitoring/dashboard_info")
async def dashboard_info():
    """Returns dashboardinfo state"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info")
async def get_monitor_info():
    """Returns monitor info"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_tasks")
async def get_monitor_info_tasks():
    """Returns monitor info tasks"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_apps")
async def get_monitor_info_apps():
    """Returns app infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_files")
async def get_monitor_info_files():
    """Returns file infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_websockets")
async def get_monitor_info_websockets():
    """Returns websocket infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_host")
async def get_monitor_info_host():
    """Returns host infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_objects")
async def get_monitor_info_objects():
    """Returns object infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_utilization")
async def get_monitor_info_utilization():
    """Returns resource utilization infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/monitoring/get_monitor_info_limits")
async def get_monitor_info_limits():
    """Returns resource limit infos"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
