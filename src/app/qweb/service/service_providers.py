"""Backend definitions"""

from typing import Optional
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.service.service_context import (
    LayerObject,
    ObjectContext,
    QwebBackend,
    QwebObjectLayer,
    ServiceComponent,
    CoreContext,
    BackendContext,
)
from app.qweb.auth.auth_qweb import QwebAuthenticatorBase
from app.qweb.service.service_tasks import QwebTaskManager


class ObjectLayerContextProvider(Loggable):
    """Object layer context provider"""

    def __init__(self):
        Loggable.__init__(self, LogTarget.QWEB)
        self.layers = {}

    def add(self, name: str, backend: QwebObjectLayer) -> bool:
        """Add new backend system"""
        result = False
        if name not in self.layers:
            if backend is not None:
                self.layers[name] = backend
                result = True
        return result

    def remove(self, name: str) -> bool:
        """Remove existing backend system"""
        result = False
        if name in self.layers:
            self.layers.pop(name)
            result = True
        return result

    def get(self, name: str) -> Optional[QwebObjectLayer]:
        """Get existing backend system"""
        result = None
        if name in self.layers:
            result = self.layers[name]
        return result

    async def create_context(
        self, needed: list[LayerObject], args: dict
    ) -> ObjectContext:
        """Dynamically creates Object Context based on a list of names"""
        resdict = {}
        keys = self.layers.keys()

        for comp in needed:
            if comp.layer in keys:
                resdict[comp.layer] = self.layers[comp.layer]
            else:
                raise ValueError("The specified layer does not exist")
        result = ObjectContext(components=resdict, objects={}, isvalid=True)
        await result.read_objects(needed, args)
        return result


class BackendContextProvider:
    """Backend context provider"""

    def __init__(self):
        self.backends = {}

    def add(self, name: str, backend: QwebBackend) -> bool:
        """Add new backend system"""
        result = False
        if name not in self.backends:
            if backend is not None:
                self.backends[name] = backend
                result = True
        return result

    def remove(self, name: str) -> bool:
        """Remove existing backend system"""
        result = False
        if name in self.backends:
            self.backends.pop(name)
            result = True
        return result

    def get(self, name: str) -> Optional[QwebBackend]:
        """Get existing backend system"""
        result = None
        if name in self.backends:
            result = self.backends[name]
        return result

    def create_context(self, needed: list[str]) -> BackendContext:
        """Dynamically creates Backend Context based on a list of names"""
        resdict = {}
        keys = self.backends.keys()

        for comp in needed:
            if comp in keys:
                resdict[comp] = self.backends[comp]
            else:
                raise ValueError("The specified backend does not exist")
        result = BackendContext(components=resdict, isvalid=True)
        return result


class CoreContextProvider:
    """Core context"""

    def __init__(self, manager: QwebTaskManager, authenticator: QwebAuthenticatorBase):
        self.manager = manager
        self.authenticator = authenticator
        self.components = {
            ServiceComponent.TASK: self.manager,
            ServiceComponent.AUTH: self.authenticator,
        }

    def create_context(self, needed: list[ServiceComponent]) -> CoreContext:
        """Dynamically creates Service Context based on a list of names"""
        resdict = {}
        keys = self.components.keys()

        for comp in needed:
            if comp in keys:
                resdict[comp] = self.components[comp]
            else:
                raise ValueError("The specified qweb component does not exist")
        result = CoreContext(components=resdict, isvalid=True)
        return result
