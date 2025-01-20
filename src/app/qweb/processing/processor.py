"""Processor"""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import asdict, dataclass, is_dataclass
import traceback
from typing import Coroutine, Optional
from app.qweb.common.config import QuartConfig, QuartProcessorConfig
from quart import Request, Response, Websocket

from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.service.service_context import QwebProcessorContexts, ServiceComponent
from app.qweb.service.service_tasks import QwebTaskManager


class ProcessorType(Enum):
    """Processor type"""

    FILE = 1
    STATIC_TEMPLATE = 2
    API = 3
    WEBSOCKET = 4


class FileProcessorAction(Enum):
    """File action"""

    UNKNOWN = 1
    ROOT_FILE = 2
    STATIC_FILE = 3


class TemplateProcessorAction(Enum):
    """Template action"""

    UNKNOWN = 1
    STATIC_HTML = 2
    STATIC_JS = 3
    STATIC_CSS = 4


class WebsocketProcessorAction(Enum):
    """Websocket action"""

    UNKNOWN = 1
    VIEWER = 2
    EXTENSION = 3


class ApiProcessorAction(Enum):
    """Template action"""

    UNKNOWN = 1
    HTML = 2
    JSON = 3


@dataclass
class QwebResult:
    """Common response format for json results"""

    response_code: int
    response_data: dict | list | str
    sys_exitcode: int = 0
    sys_log: str = ""
    error_message: str = ""
    error_trace: str = ""
    response_url: str = ""
    id_instance: str = ""

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__} "
            f"(code={self.response_code},error={self.error_message})"
        )


@dataclass
class ProcessorRequestContext:
    """Processor Request context"""

    request_quart: Optional[Request]
    request_websocket: Optional[Websocket]
    request_args: dict


@dataclass
class ProcessorRequest:
    """Processor Request arguments"""

    url: str
    path: str
    bearer: str
    token: str
    proctype: ProcessorType
    apitask: str
    action: (
        FileProcessorAction
        | TemplateProcessorAction
        | ApiProcessorAction
        | WebsocketProcessorAction
    )
    content_type: str
    static_args: dict
    request_context: ProcessorRequestContext


class ProcessorBase(ABC, Loggable):
    """Baseclass for all Processors"""

    cfg_quart: QuartConfig
    cfg_proc: QuartProcessorConfig

    def __init__(self):
        Loggable.__init__(self, LogTarget.PROC)
        self._log_info("Processor initialized")
        self.cfg_quart = QuartConfig("", "", "", "", "")
        self.cfg_proc = QuartProcessorConfig("https", "cluster.daas-design.de", 443)
        self.template_args = {}

    def set_configs(self, cfg_quart: QuartConfig, cfg_proc: QuartProcessorConfig):
        self.cfg_quart = cfg_quart
        self.cfg_proc = cfg_proc
        self.template_args = {
            "hostproto": self.cfg_proc.hostproto,
            "hostip": self.cfg_proc.hostip,
            "hostport": self.cfg_proc.hostport,
        }

    def create_async_response(self, coro: Coroutine) -> Response | dict | str:
        """Synchronously retrieves asynchronous result"""
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(coro)
        result = loop.run_until_complete(future)
        return result

    async def get_context_object(self, name: str, ctx: QwebProcessorContexts) -> dict:
        """Returns specified object"""
        req_objects = ctx.objects.objects
        if name in req_objects:
            obj1 = req_objects[name]
            if isinstance(obj1, dict):
                return obj1
            if is_dataclass(obj1) and not isinstance(obj1, type):
                return asdict(obj1)
        return {}

    async def run_apitask(
        self, ctx: QwebProcessorContexts, proc_request: ProcessorRequest, info, user
    ):
        """Runs registerable api task"""
        from app.qweb.common.common import TaskArgs

        mancomp: QwebTaskManager = ctx.core.get(ServiceComponent.TASK)
        task = mancomp.get_task_endpoint(proc_request.apitask)
        if task != "":
            args = TaskArgs(ctx, proc_request, info, user)
            newtask = (task, [args], {})
            return await mancomp.run_apitask_concurrently(newtask)
        return {}

    def create_error_response(
        self, msg: str, status: int = 500, content_type: str = "text/html"
    ) -> Response:
        """Create error response"""
        return Response(response=msg, status=status, content_type=content_type)

    def create_error_dict(
        self,
        msg: str,
        status_http: int = 500,
        status_sys: int = 1,
        data: dict = {},
        exception: Optional[Exception] = None,
    ) -> QwebResult:
        """Create error dict"""
        from app.qweb.service.service_runtime import get_qweb_runtime

        runtime = get_qweb_runtime()
        conf = runtime.cfg_qweb.handler
        error_msg = ""
        if exception is not None:
            if conf.enable_debugging:
                error_msg = f"{type(exception).__qualname__}! {exception}"
        error_trace = ""
        if conf.enable_debugging and conf.enable_exceptions_echo:
            error_trace = traceback.format_exc()
        return QwebResult(status_http, data, status_sys, msg, error_msg, error_trace)

    @abstractmethod
    async def process(
        self, ctx: QwebProcessorContexts, proc_request: ProcessorRequest, info, user
    ) -> tuple[Response | dict | str, int]:
        """Proicess output"""
        raise NotImplementedError()
