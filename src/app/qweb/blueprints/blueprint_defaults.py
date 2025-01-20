"""Default Blueprints"""

import inspect
from quart import Blueprint
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
    ConcurrencyMode,
)
from app.qweb.processing.processor import (
    FileProcessorAction,
    ProcessorType,
    TemplateProcessorAction,
)

infos = [
    BlueprintInfo(
        endpoint_id=10000,
        name="index",
        url="/",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_HTML,
        override_target="layout.html",
        content_type="text/html",
        static_args={"title": "Qweb"},
    ),
    BlueprintInfo(
        endpoint_id=10001,
        name="index_debug",
        url="/debug",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_HTML,
        override_target="layout.html",
        content_type="text/html",
        static_args={"title": "Qweb"},
    ),
    BlueprintInfo(
        endpoint_id=10002,
        name="favicon",
        methods=["GET"],
        url="/favicon.ico",
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.FILE,
        processor_action=FileProcessorAction.ROOT_FILE,
        content_type="*/*",
    ),
    BlueprintInfo(
        endpoint_id=10003,
        name="robots",
        methods=["GET"],
        url="/robots.txt",
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.FILE,
        processor_action=FileProcessorAction.ROOT_FILE,
        content_type="text/html",
    ),
]
handler = BlueprintHandler(
    blueprints=Blueprint("routes_default", __name__),
    infos=infos,
    testing=False,
    default_handler=None,
)


@handler.blueprints.post("/")
async def index():
    """Default Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/debug")
async def index_debug():
    """Default Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/robots.txt")
async def robots():
    """Endpoint for crawlers"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/favicon.ico")
async def favicon():
    """Default Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
