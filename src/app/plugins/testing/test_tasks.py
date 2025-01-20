"""DB Tasks"""

from dataclasses import asdict, is_dataclass
from quart import Response
from app.qweb.processing.processor import ProcessorRequest
from app.qweb.service.service_context import QwebProcessorContexts
from enum import Enum


class TestTask(Enum):
    """Test processor tasktype"""

    TEST_GET_ENTITY = "TEST_GET_ENTITY"


async def test_get_layer_entity(
    ctx: QwebProcessorContexts, proc_request: ProcessorRequest
) -> Response | dict | str:
    """Test task api"""
    req_objects = ctx.objects.objects
    if "entity" in req_objects:
        entity = req_objects["entity"]
        if isinstance(entity, dict):
            return entity
        if is_dataclass(entity) and not isinstance(entity, type):
            return asdict(entity)
    return {"Error": "Unknown error"}
