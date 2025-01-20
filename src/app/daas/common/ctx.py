"""CTX helpers"""

from typing import Optional, Type, TypeVar

import aiohttp
from app.qweb.auth.auth_qweb import QwebUser
from app.qweb.blueprints.blueprint_info import BlueprintInfo
from app.qweb.common.qweb_tools import get_database
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.processing.processor import ProcessorRequest, QwebResult
from app.qweb.service.service_context import QwebProcessorContexts


T = TypeVar("T")
log = Loggable(LogTarget.ANY)


def get_backend_component(
    ctx: QwebProcessorContexts, name: str, ret_type: Type[T]
) -> T:
    backend = ctx.backends.get(name)
    if backend is not None and backend.component is not None:
        if isinstance(backend.component, ret_type):
            return backend.component
    raise TypeError(f"Backend has invalid type: {name} -> {ret_type}")


def get_request_backend(ctx: QwebProcessorContexts, name: str, ret_type: Type[T]) -> T:
    node = ctx.backends.get(name)
    if node is not None:
        if isinstance(node, ret_type):
            return node
    raise TypeError(f"Backend has invalid type: {name} -> {ret_type}")


def get_request_object(ctx: QwebProcessorContexts, name: str, ret_type: Type[T]) -> T:
    req_objects = ctx.objects.objects
    if name in req_objects:
        entity = req_objects[name]
        if isinstance(entity, ret_type):
            return entity
        raise TypeError(f"LayerObject has invalid type: {name} {type(entity)}")
    raise TypeError(f"LayerObject is not available: {name} {ret_type}")


def get_request_object_optional(
    ctx: QwebProcessorContexts, name: str, ret_type: Type[T]
) -> Optional[T]:
    req_objects = ctx.objects.objects
    if name in req_objects:
        entity = req_objects[name]
        if isinstance(entity, ret_type):
            return entity
        raise TypeError(f"LayerObject has invalid type: {name} {type(entity)}")
    return None


async def create_response_by_data_attribute(
    data: dict, response: Optional[aiohttp.ClientResponse], include_data: bool = True
) -> QwebResult:
    if response is not None:
        if response.status != 200:
            return await create_response_by_http(response, data, include_data)
    if "data" in data:
        if include_data:
            return QwebResult(200, data)
        return QwebResult(200, {})
    return QwebResult(500, {}, 1, "No data in api response")


async def create_response_by_data_length(
    data: dict, include_data: bool = True
) -> QwebResult:
    if len(data) > 0:
        if include_data:
            return QwebResult(200, data)
        return QwebResult(200, {})
    return QwebResult(500, {}, 1, "No data elements in api response")


async def create_response_by_exitstatus(
    data: dict, response: Optional[aiohttp.ClientResponse], include_data: bool = True
) -> QwebResult:
    if response is not None:
        if response.status != 200:
            return await create_response_by_http(response, data, include_data)
    if "exitstatus" in data:
        if data["exitstatus"] == "OK":
            if include_data:
                return QwebResult(200, data, 0, "")
            return QwebResult(200, {}, 0, "")
        return QwebResult(400, {}, 1, data["exitstatus"])
    return QwebResult(500, {}, 1, "No exitstatus in api response")


async def create_response_by_http(
    response: aiohttp.ClientResponse, data: dict, include_data: bool = True
) -> QwebResult:
    if response.status == 200:
        if include_data:
            return QwebResult(200, data, 0, "")
        return QwebResult(200, {}, 0, "")
    return QwebResult(response.status, {}, 2, f"{response.reason}")


async def create_response_url_stop(stopped: bool) -> QwebResult:
    if stopped:
        return QwebResult(200, {}, response_url="-")
    return QwebResult(400, {}, 1, "Not stopped")


async def create_response_url_start(connect: bool, id_instance: str) -> QwebResult:
    from app.daas.db.database import Database

    dbase = await get_database(Database)
    inst = await dbase.get_instance_by_id(id_instance)
    if connect:
        if inst is not None and inst.id_con is not None:
            con = await dbase.get_guacamole_connection(inst.id_con)
            if con is not None:
                return QwebResult(
                    200, {}, response_url=con.viewer_url, id_instance=inst.id
                )
        return QwebResult(400, {}, 1, "instance or connection missing")
    return QwebResult(200, {})


async def remove_args(args: dict, exclude_params: list[str]) -> dict:
    for param in exclude_params:
        if param in args:
            args.pop(param)
    return args


def log_task_arguments(
    ctx: QwebProcessorContexts,
    req: ProcessorRequest,
    info: BlueprintInfo,
    user: QwebUser,
):
    msg = f"TaskArgs({ctx}, {req}, {info}, {user})"
    log._log_debug(msg)
