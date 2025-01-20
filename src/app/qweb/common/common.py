from dataclasses import dataclass

from app.qweb.auth.auth_qweb import QwebUser
from app.qweb.blueprints.blueprint_info import BlueprintInfo
from app.qweb.processing.processor import ProcessorRequest
from app.qweb.service.service_context import QwebProcessorContexts


@dataclass
class TaskArgs:
    ctx: QwebProcessorContexts
    req: ProcessorRequest
    info: BlueprintInfo
    user: QwebUser


@dataclass
class SystemTaskArgs:
    args: dict
    id_task: str
    id_object: str
    id_instance: str
