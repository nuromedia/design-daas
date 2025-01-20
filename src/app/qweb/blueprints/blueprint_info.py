"""Common Blueprint definitions"""

from dataclasses import dataclass, field
from enum import Enum

from app.qweb.processing.processor import (
    ApiProcessorAction,
    FileProcessorAction,
    ProcessorType,
    TemplateProcessorAction,
    WebsocketProcessorAction,
)


class ConcurrencyMode(Enum):
    """File action"""

    NONE = 1
    CTX_AND_AUTH = 2
    AUTH_AND_PROC = 3


class AuthenticationMode(Enum):
    """File action"""

    NONE = 0
    TOKEN = 1
    USER = 2
    ALL = 3


@dataclass
class BlueprintInfo:
    """Blueprint info"""

    endpoint_id: int
    name: str
    url: str
    methods: list[str]
    auth_params: AuthenticationMode
    conc_params: ConcurrencyMode
    processor_action: (
        FileProcessorAction
        | TemplateProcessorAction
        | ApiProcessorAction
        | WebsocketProcessorAction
    )
    processor: ProcessorType
    processor_task: str = ""
    content_type: str = "text/html"
    override_target: str = ""
    websocket_request: bool = False
    static_args: dict = field(default_factory=lambda: {})
    request_args_mandatory: list = field(default_factory=lambda: [])
    request_args_optional: list = field(default_factory=lambda: [])
    request_args_common: list = field(default_factory=lambda: [])
    request_args_query: list = field(default_factory=lambda: [])
    request_args_file: list = field(default_factory=lambda: [])
    backends: list = field(default_factory=lambda: [])
    objects: list = field(default_factory=lambda: [])

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}" f"(id={self.endpoint_id},name={self.name})"
        )
