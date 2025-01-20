"""Default Blueprints"""

import inspect
from quart import Blueprint
from app.daas.common.enums import BackendName
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)
from app.qweb.processing.processor import (
    ApiProcessorAction,
    ProcessorType,
    TemplateProcessorAction,
)


test_args = ["counter", "timestamp"]
test_backends = [BackendName.DB.value]
test_methods = ["POST"]
infos = [
    BlueprintInfo(
        endpoint_id=40000,
        name="get_login",
        url="/login",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_HTML,
        override_target="login.html",
        content_type="text/html",
        static_args={"title": "Login"},
    ),
    BlueprintInfo(
        endpoint_id=40001,
        name="post_login",
        url="/login",
        methods=["POST"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=ApiProcessorAction.JSON,
        content_type="text/html",
        request_args_mandatory=["username", "password"],
    ),
    BlueprintInfo(
        endpoint_id=40002,
        name="jslogin",
        url="/js/login.js",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_JS,
        override_target="js/login.js",
        content_type="text/javascript",
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_auth", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


# pylint: disable=unused-argument
@handler.blueprints.get("/login")
async def get_login():
    """Default Browsertest Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


# pylint: disable=unused-argument
@handler.blueprints.post("/login")
async def post_login():
    """Default Browsertest Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/js/login.js")
async def jslogin():
    """js login endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
