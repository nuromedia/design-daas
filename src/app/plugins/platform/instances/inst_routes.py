"""Phases Blueprints"""

import inspect

from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.platform.instances.inst_tasks import InstanceTask
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
backends = [BackendName.FILE.value, BackendName.INSTANCES.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=110000,
        name="vminvoke_app",
        url="/inst/vminvoke_app",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_APP.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "cmd", "args"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110001,
        name="vminvoke_cmd",
        url="/inst/vminvoke_cmd",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_CMD.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "cmd", "args"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110002,
        name="vminvoke_ssh",
        url="/inst/vminvoke_ssh",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_SSH.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "cmd", "args"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110003,
        name="vminvoke_action",
        url="/inst/vminvoke_action",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_ACTION.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "cmd", "args"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110004,
        name="vminvoke_resolution",
        url="/inst/vminvoke_resolution",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_RESOLUTION.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "cmd", "args"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110005,
        name="vminvoke_ospackage",
        url="/inst/vminvoke_ospackage",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_OSPACKAGE.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "cmd", "args"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110006,
        name="vminvoke_upload",
        url="/inst/vminvoke_upload",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_UPLOAD.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env"],
        request_args_optional=["execute"],
        request_args_file=["file"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110007,
        name="vminvoke_filesystem",
        url="/inst/vminvoke_cephfs",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_FILESYSTEM.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "cmd", "args"],
        request_args_optional=["ceph_public", "ceph_shared", "ceph_user"],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110008,
        name="vminvoke_list",
        url="/inst/list",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_LIST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTLIST.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110009,
        name="vminvoke_test_icmp",
        url="/inst/connection_test_icmp",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_TEST_ICMP.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110010,
        name="vminvoke_test_ssh",
        url="/inst/connection_test_ssh",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_TEST_SSH.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYOBJ.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=110011,
        name="vminvoke_rtt",
        url="/inst/vminvoke_rtt",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=InstanceTask.INST_VMINVOKE_RTT.value,
        content_type="application/json",
        request_args_mandatory=["id", "id_env", "iter", "name", "cmd", "args"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_instances", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/inst/vminvoke_app")
async def vminvoke_app():
    """Invokes (non-blocking) app command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_cmd")
async def vminvoke_cmd():
    """Invokes (blocking) command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_ssh")
async def vminvoke_ssh():
    """Invokes (blocking) command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_action")
async def vminvoke_action():
    """Invokes (blocking) action command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_resolution")
async def vminvoke_resolution():
    """Invokes (blocking) resolution command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_ospackage")
async def vminvoke_ospackage():
    """Invokes (blocking) action command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_upload")
async def vminvoke_upload():
    """Invokes (blocking) action command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_filesystem")
async def vminvoke_filesystem():
    """Invokes (blocking) action command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/list")
async def vminvoke_list():
    """Invokes (blocking) action command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/connection_test_icmp")
async def vminvoke_test_icmp():
    """Invokes (blocking) icmp test command ()ping)"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/connection_test_ssh")
async def vminvoke_test_ssh():
    """Invokes (blocking) ssh test command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/inst/vminvoke_rtt")
async def vminvoke_rtt():
    """Invokes (blocking) roundtrip command"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
