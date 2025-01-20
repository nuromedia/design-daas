"""VM Blueprints"""

import inspect

from app.daas.common.enums import BackendName, LayerName
from app.plugins.core.db.db_layer import DBObject
from app.plugins.platform.vm.vm_tasks import VMTask
from app.plugins.resources.limits.limits_layer import LimitObject, LimitObjectLayer
from app.plugins.resources.limits.limits_tasks import LimitTask
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
backends = [BackendName.LIMITS.value, BackendName.DB.value]

infos = [
    BlueprintInfo(
        endpoint_id=130000,
        name="limits_get",
        url="/limits/get",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=LimitTask.LIMIT_GET.value,
        content_type="application/json",
        request_args_mandatory=["id_owner"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("entity", LimitObject.BYOWNER.value, LayerName.LIMIT.value)
        ],
    ),
    BlueprintInfo(
        endpoint_id=130001,
        name="limits_put",
        url="/limits/put_limit",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=LimitTask.LIMIT_PUT.value,
        content_type="application/json",
        request_args_mandatory=[
            "id_owner",
            "vm_max",
            "container_max",
            "obj_max",
            "cpu_max",
            "mem_max",
            "dsk_max",
        ],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("entity", LimitObject.BYOWNER.value, LayerName.LIMIT.value)
        ],
    ),
    BlueprintInfo(
        endpoint_id=130002,
        name="limits_remove",
        url="/limits/remove_limit",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=LimitTask.LIMIT_REMOVE.value,
        content_type="application/json",
        request_args_mandatory=["id_owner"],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[
            LayerObject("entity", LimitObject.BYOWNER.value, LayerName.LIMIT.value)
        ],
    ),
    BlueprintInfo(
        endpoint_id=130003,
        name="limits_list",
        url="/limits/list_limits",
        methods=["POST"],
        auth_params=AuthenticationMode.ALL,
        conc_params=ConcurrencyMode.CTX_AND_AUTH,
        processor=ProcessorType.API,
        processor_action=ApiProcessorAction.JSON,
        processor_task=LimitTask.LIMIT_LIST.value,
        content_type="application/json",
        request_args_mandatory=[],
        request_args_optional=[],
        request_args_common=perf_args,
        backends=backends,
        objects=[LayerObject("entity", LimitObject.LIST.value, LayerName.LIMIT.value)],
    ),
]


handler = BlueprintHandler(
    blueprints=Blueprint("routes_limits", __name__),
    infos=infos,
    testing=True,
    default_handler=None,
)


@handler.blueprints.post("/limits/get_limit")
async def limits_get():
    """Returns specified limit"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/limits/put_limit")
async def limits_put():
    """Stores specified limit"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/limits/remove_limit")
async def limits_remove():
    """Removes specified limit"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)


@handler.blueprints.post("/limits/list_limits")
async def limits_list():
    """Lists specified limit"""
    frame = inspect.currentframe()
    return await handler.handle_frame(frame)
