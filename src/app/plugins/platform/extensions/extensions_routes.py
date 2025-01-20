"""Default Blueprints"""

import inspect
from quart import Blueprint
from app.daas.common.enums import BackendName
from app.plugins.platform.extensions.extensions_tasks import ExtensionsTask
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.processing.processor import ProcessorType, WebsocketProcessorAction
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)


default_args = ["id", "id_env"]
perf_args = ["counter", "timestamp"]
backends = [BackendName.EXTENSIONS.value, BackendName.DB.value]
infos = [
    BlueprintInfo(
        endpoint_id=150000,
        name="printer_ws",
        url="/extensions/printer_ws/<token>",
        methods=["POST"],
        auth_params=AuthenticationMode.TOKEN,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.WEBSOCKET,
        processor_action=WebsocketProcessorAction.EXTENSION,
        processor_task=ExtensionsTask.EXTENSIONS_WSS_PRINTER.value,
        websocket_request=True,
        content_type="text/html",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_query=["token"],
        request_args_common=perf_args,
        backends=backends,
        # objects=[LayerObject("entity", DBObject.INST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=150001,
        name="audio_ws",
        url="/extensions/audio_ws/<string:token>",
        methods=["POST"],
        auth_params=AuthenticationMode.TOKEN,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.WEBSOCKET,
        processor_action=WebsocketProcessorAction.EXTENSION,
        processor_task=ExtensionsTask.EXTENSIONS_WSS_AUDIO.value,
        websocket_request=True,
        content_type="text/html",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_query=["token"],
        request_args_common=perf_args,
        backends=backends,
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_extensions", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.websocket("/extensions/printer_ws/<token>")
async def printer_ws(token: str):
    """Forward all printer requests"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.websocket("/extensions/audio_ws/<string:token>")
async def audio_ws(token: str):
    """Forward all audio requests"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
