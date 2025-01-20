"""Default Blueprints"""

import inspect
from quart import Blueprint
from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.platform.node.node_tasks import NodeTask
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    ConcurrencyMode,
    BlueprintInfo,
)
from app.qweb.processing.processor import ApiProcessorAction, ProcessorType
from app.qweb.service.service_context import LayerObject

default_args = ["id", "id_env"]
perf_args = ["counter", "timestamp"]
backends = [BackendName.NODE.value, BackendName.DB.value]
infos = [
    BlueprintInfo(
        endpoint_id=50000,
        name="node_vmconfigure_dhcp",
        url="/node/vmconfigure_dhcp",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=NodeTask.NODE_CONFIGURE_DHCP.value,
        content_type="text/html",
        request_args_mandatory=default_args,
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYID.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=50001,
        name="node_vmconfigure_iptables",
        url="/node/vmconfigure_iptables",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=NodeTask.NODE_CONFIGURE_IPTABLES.value,
        content_type="text/html",
        request_args_mandatory=default_args,
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYID.value, LayerName.DB.value)],
    ),
    BlueprintInfo(
        endpoint_id=50002,
        name="node_vminvoke_upload",
        url="/node/vminvoke_upload",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.AUTH_AND_PROC,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=NodeTask.NODE_INVOKE_UPLOAD.value,
        content_type="text/html",
        request_args_mandatory=["file"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", DBObject.INSTBYID.value, LayerName.DB.value)],
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_node", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/node/vmconfigure_dhcp")
async def node_vmconfigure_dhcp():
    """Configures dhcp for specified instance"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/node/vmconfigure_iptables")
async def node_vmconfigure_iptables():
    """Configures iptables for specified instance"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/node/vminvoke_upload")
async def node_vminvoke_upload():
    """Uploads file to host"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
