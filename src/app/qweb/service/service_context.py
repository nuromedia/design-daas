"""Service context"""

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class QwebBackend:
    """A registerable backend component"""

    name: str
    component: Any
    connected: bool = False
    registered: bool = False

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}"
            f"(name={self.name},"
            f"connected={self.connected},registered={self.registered})"
        )

    @abstractmethod
    def status(self) -> str:
        """Returns status message"""
        NotImplementedError()

    @abstractmethod
    async def connect(self) -> bool:
        """Connects database adapter"""
        NotImplementedError()

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnects database adapter"""
        NotImplementedError()


@dataclass
class LayerObject:
    """Registerable Layer object"""

    name: str
    objtype: str
    layer: str


@dataclass
class QwebObjectLayer(Loggable):
    """A registerable object layer component"""

    name: str
    backend: QwebBackend
    objects_returned: int

    def __init__(self, name: str, backend: QwebBackend):
        self.name = name
        self.objects_returned = 0
        self.backend = backend
        Loggable.__init__(self, LogTarget.LAYERS)

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}"
            f"(name={self.name},"
            f"backend={self.backend.name},"
            f"returned={self.objects_returned})"
        )

    def status(self) -> str:
        """Returns status message"""
        return self.__repr__()

    async def get_object(
        self,
        obj: LayerObject,
        args: dict,
    ) -> Optional[Any]:
        """Retrieves object from backend"""
        raise NotImplementedError("Abstract method not implemented: get_object")


@dataclass
class BackendContext:
    """A retrieved backend context"""

    components: dict[str, Any]
    isvalid: bool

    def get(self, comp: str):
        """Obtaines registered component"""
        if comp not in self.components:
            raise ValueError(f"The component was not available: {comp}")
        return self.components[comp]


@dataclass
class ObjectContext:
    """A retrieved backend context"""

    components: dict[str, QwebObjectLayer]
    objects: dict[str, Optional[Any]]
    isvalid: bool

    async def read_objects(self, needed: list[LayerObject], args: dict):
        """Reads object from backend"""

        for need in needed:
            objlayer = self.get_layer(need.layer)
            if objlayer is not None:
                obj = await objlayer.get_object(obj=need, args=args)
                if obj is not None:
                    self.objects[need.name] = obj

    def get_layer(self, comp: str):
        """Obtaines registered component"""
        if comp not in self.components:
            raise ValueError(f"The component was not available: {comp}")
        return self.components[comp]


class ServiceComponent(Enum):
    """Core components"""

    AUTH = 0
    TASK = 1


@dataclass
class CoreContext:
    """A retrieved core context"""

    components: dict
    isvalid: bool

    def get(self, comp: ServiceComponent):
        """Obtaines registered component"""
        if comp not in self.components:
            raise ValueError(f"The component was not available: {comp}")
        return self.components[comp]


@dataclass
class QwebProcessorContexts:
    """Parsed request contexts"""

    core: CoreContext
    backends: BackendContext
    objects: ObjectContext
