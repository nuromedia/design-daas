"""Default Blueprints"""

import inspect
from quart import Blueprint
from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.testing.test_tasks import TestTask
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
from app.qweb.service.service_context import LayerObject


test_args_objs = ["id"]
test_args_perf = ["counter", "timestamp"]
test_backends = [BackendName.DB.value]
test_methods = ["POST"]
test_auth = AuthenticationMode.USER
test_objects = [
    LayerObject("entity", DBObject.OBJ.value, LayerName.DB.value),
]
infos = [
    BlueprintInfo(
        endpoint_id=20000,
        name="testing",
        url="/testing",
        methods=["GET"],
        auth_params=test_auth,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_HTML,
        override_target="layout-testing.html",
        content_type="text/html",
        static_args={"title": "Qweb"},
    ),
    BlueprintInfo(
        endpoint_id=20001,
        name="baseline0",
        url="/baseline0",
        methods=test_methods,
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.NONE,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=test_args_perf,
    ),
    BlueprintInfo(
        endpoint_id=20002,
        name="baseline1",
        url="/baseline1",
        methods=test_methods,
        auth_params=test_auth,
        conc_params=ConcurrencyMode.NONE,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=test_args_perf,
    ),
    BlueprintInfo(
        endpoint_id=20003,
        name="baseline2",
        url="/baseline2",
        methods=test_methods,
        auth_params=test_auth,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=test_args_perf,
    ),
    BlueprintInfo(
        endpoint_id=20004,
        name="baseline3",
        url="/baseline3",
        methods=test_methods,
        auth_params=test_auth,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=test_args_perf,
    ),
    BlueprintInfo(
        endpoint_id=20005,
        name="baseline4",
        url="/baseline4",
        methods=test_methods,
        auth_params=test_auth,
        conc_params=ConcurrencyMode.NONE,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=str(TestTask.TEST_GET_ENTITY),
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=test_args_perf,
        backends=test_backends,
        objects=test_objects,
    ),
    BlueprintInfo(
        endpoint_id=20006,
        name="baseline5",
        url="/baseline5",
        methods=test_methods,
        auth_params=test_auth,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=str(TestTask.TEST_GET_ENTITY),
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=test_args_perf,
        backends=test_backends,
        objects=test_objects,
    ),
    BlueprintInfo(
        endpoint_id=20007,
        name="baseline6",
        url="/baseline6",
        methods=test_methods,
        auth_params=test_auth,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=str(TestTask.TEST_GET_ENTITY),
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=test_args_perf,
        backends=test_backends,
        objects=test_objects,
    ),
    BlueprintInfo(
        endpoint_id=20108,
        name="dbtests",
        url="/dbtests",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_HTML,
        override_target="layout-testing-db.html",
        content_type="text/html",
    ),
    BlueprintInfo(
        endpoint_id=20109,
        name="db_getobject",
        url="/db_getobject",
        methods=test_methods,
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=str(TestTask.TEST_GET_ENTITY),
        content_type="application/json",
        request_args_mandatory=["id"],
        request_args_optional=test_args_perf,
        backends=test_backends,
        objects=test_objects,
    ),
    BlueprintInfo(
        endpoint_id=20110,
        name="errortest1",
        url="/errortest1",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.NONE,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        content_type="application/json",
        request_args_mandatory=test_args_objs,
        request_args_optional=[],
        request_args_common=[],
        request_args_query=["bla"],
    ),
    BlueprintInfo(
        endpoint_id=20111,
        name="testbrowser",
        url="/testbrowser",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_HTML,
        override_target="layout-browsertest.html",
        content_type="text/html",
        static_args={"title": "Browser-Test"},
        request_args_query=["iterations", "url"],
    ),
    BlueprintInfo(
        endpoint_id=20112,
        name="jstest",
        url="/js/test.js",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_JS,
        override_target="js/test.js",
        content_type="text/javascript",
    ),
    BlueprintInfo(
        endpoint_id=20113,
        name="csstest",
        url="/css/test.css",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_CSS,
        override_target="css/test.css",
        content_type="text/css",
    ),
    BlueprintInfo(
        endpoint_id=20114,
        name="test_debug",
        url="/debug",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_HTML,
        override_target="layout-debug.html",
        content_type="text/html",
        static_args={
            "title": "qweb debug",
        },
    ),
    BlueprintInfo(
        endpoint_id=20115,
        name="cssdebug",
        url="/css/debug.css",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_CSS,
        override_target="css/debug.css",
        content_type="text/css",
    ),
    BlueprintInfo(
        endpoint_id=20116,
        name="jsdebug",
        url="/js/debug.js",
        methods=["GET"],
        auth_params=AuthenticationMode.NONE,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.STATIC_TEMPLATE,
        processor_action=TemplateProcessorAction.STATIC_JS,
        override_target="js/debug.js",
        content_type="text/javascript",
    ),
]


async def default_handler():
    """Default Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


handler = BlueprintHandler(
    blueprints=Blueprint("routes_testing", __name__),
    infos=infos,
    testing=True,
    default_handler=default_handler,
)


# pylint: disable=unused-argument
@handler.blueprints.get("/debug")
async def test_debug():
    """Default debug-ui Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


# pylint: disable=unused-argument
@handler.blueprints.get("/testing")
async def testing():
    """Default Browsertest Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


# pylint: disable=unused-argument
@handler.blueprints.get("/testbrowser/<iterations>/<url>")
async def testbrowser(iterations: int, url: str):
    """Default Browsertest Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/js/test.js")
async def jstest():
    """Test js Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/css/test.css")
async def csstest():
    """Test css Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/css/debug.css")
async def cssdebug():
    """Debug css Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/js/debug.js")
async def jsdebug():
    """Debug js Endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/baseline0")
async def baseline0():
    """Baseline test 0"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/baseline1")
async def baseline1():
    """Baseline test 1"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/baseline2")
async def baseline2():
    """Baseline test 2"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/baseline3")
async def baseline3():
    """Baseline test 3"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/baseline4")
async def baseline4():
    """Baseline test 4"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/baseline5")
async def baseline5():
    """Baseline test 5"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/baseline6")
async def baseline6():
    """Baseline test 6"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/errortest1")
async def errortest1():
    """Error test 1"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.get("/errortest2")
async def errortest2():
    """Error test 2"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


# pylint: disable=unused-argument
@handler.blueprints.get("/dbtests")
async def dbtests():
    """Dbtest layout page"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


# pylint: disable=unused-argument
@handler.blueprints.post("/db_getobject")
async def db_getobject():
    """Dbtest endpoint"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
