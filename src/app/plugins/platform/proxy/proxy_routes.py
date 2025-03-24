"""Default Blueprints"""

import inspect
from quart import Blueprint
from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.platform.proxy.proxy_tasks import ProxyTask
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.processing.processor import (
    ApiProcessorAction,
    ProcessorType,
    WebsocketProcessorAction,
)
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)
from app.qweb.service.service_context import LayerObject


default_args = ["id", "id_env"]
perf_args = ["counter", "timestamp"]
backends = [BackendName.PROXY.value, BackendName.DB.value]
infos = [
    BlueprintInfo(
        endpoint_id=90000,
        name="viewer_template",
        url="/viewer/template/<id>",
        methods=["GET", "POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.HTML,
        processor_task=ProxyTask.VIEWER_TEMPLATE.value,
        content_type="text/html",
        request_args_mandatory=[],
        request_args_optional=["id_env"],
        request_args_query=["id"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYQUERY.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=90001,
        name="viewer_check",
        url="/viewer/check/<id_instance>",
        methods=["POST"],
        auth_params=AuthenticationMode.TOKEN,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ProxyTask.VIEWER_CHECK.value,
        content_type="application/json",
        request_args_mandatory=["token"],
        request_args_optional=[],
        request_args_query=["id_instance"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=90002,
        name="viewer_info",
        url="/viewer/info/<id_instance>",
        methods=["POST"],
        auth_params=AuthenticationMode.TOKEN,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ProxyTask.VIEWER_INFO.value,
        content_type="application/json",
        request_args_mandatory=["token"],
        request_args_optional=["resolutions"],
        request_args_query=["id_instance"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=90003,
        name="proxy_wss_viewer",
        url="/wss/connect/<id_instance>",
        methods=["POST"],
        auth_params=AuthenticationMode.TOKEN,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.WEBSOCKET,
        processor_action=WebsocketProcessorAction.VIEWER,
        processor_task=ProxyTask.VIEWER_PROXY_WS.value,
        websocket_request=True,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_query=["id_instance", "token"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=90004,
        name="viewer_connect",
        url="/viewer/connect",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ProxyTask.VIEWER_CONNECT.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "contype"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=90005,
        name="viewer_disconnect",
        url="/viewer/disconnect",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ProxyTask.VIEWER_DISCONNECT.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=90006,
        name="viewer_set_screen",
        url="/viewer/set_screen/<id_instance>",
        methods=["POST"],
        auth_params=AuthenticationMode.TOKEN,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=ProxyTask.VIEWER_SET_SCREEN.value,
        content_type="application/json",
        request_args_mandatory=["token", "contype", "resolution", "resize", "scale"],
        request_args_optional=[],
        request_args_query=["id_instance"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_proxy", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.route("/viewer/template/<id>")
async def viewer_template(id: str):
    """Get viewer template"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/viewer/connect")
async def viewer_connect():
    """Connects viewer"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/viewer/disconnect")
async def viewer_disconnect():
    """Disconnects viewer"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/viewer/set_screen/<id_instance>")
async def viewer_set_screen(id_instance: str):
    """Sets viewer screen settings"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/viewer/check/<id_instance>")
async def viewer_check(id_instance: str):
    """Check viewer connection"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/viewer/info/<id_instance>")
async def viewer_info(id_instance: str):
    """Returns viewer info for connection"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.websocket("/wss/connect/<id_instance>/<token>")
async def proxy_wss_viewer(id_instance: str, token: str):
    """Forward all sub-path WebSocket requests to guacamole"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
