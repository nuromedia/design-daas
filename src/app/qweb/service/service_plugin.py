"""Plugin definitions"""

from abc import abstractmethod
from enum import Enum
import os
import tomllib
from typing import Any, Optional
from app.daas.common.enums import ConfigFile
from app.qweb.auth.auth_qweb import QwebAuthenticatorBase
from app.qweb.blueprints.blueprint_handler import BlueprintHandler
from app.qweb.common.config import QwebConfig
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.service.service_context import QwebBackend, QwebObjectLayer
from app.qweb.service.service_runtime import get_qweb_runtime
from app.qweb.service.service_tasks import QwebTaskManager


class LoadOrder(Enum):
    Early = 1
    Core = 2
    Platform = 4
    Realtime = 5
    Storage = 6
    Late = 7


class PluginBase(Loggable):
    """Test plugin"""

    name: str
    taskmanager: Optional[QwebTaskManager]
    authenticator: Optional[QwebAuthenticatorBase]
    backends: list[QwebBackend]
    layers: list[QwebObjectLayer]
    handlers: list[BlueprintHandler]
    apitasks: list[tuple[str, Any]]
    systasks: list[tuple[str, Any]]

    def __init__(
        self,
        name: str,
        order: LoadOrder,
        testing: bool,
        backends: list[QwebBackend],
        layers: list[QwebObjectLayer],
        handlers: list[BlueprintHandler],
        apitasks: list[tuple[str, Any]],
        systasks: list[tuple[str, Any]],
        taskmanager: Optional[QwebTaskManager],
        authenticator: Optional[QwebAuthenticatorBase],
    ):
        self.name = name
        self.load_order = order
        self.testing = testing
        self.taskmanager = taskmanager
        self.authenticator = authenticator
        self.backends = backends
        self.layers = layers
        self.handlers = handlers
        self.apitasks = apitasks
        self.systasks = systasks
        self.registered = False
        self.started = False
        Loggable.__init__(self, LogTarget.PLUGIN)

    def __repr__(self) -> str:
        auth = self.authenticator is not None
        return (
            f"{self.name}({auth},"
            f"{len(self.backends)},"
            f"{len(self.layers)},"
            f"{len(self.handlers)},"
            f"{len(self.apitasks)})"
        )

    def status(self, extended: bool = False) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.started and self.registered:
            state = "Active"
        if extended is True:
            bstates = []
            for backend in self.backends:
                bstates.append(f"{backend.name}={backend.status()}")
            state = (
                f"{state} (Backends=({','.join(bstates)}),"
                f"Layers={len(self.layers)},"
                f"Handlers={len(self.handlers)},"
                f"ApiTasks={len(self.apitasks)},"
                f"AuthManager={self.authenticator},"
                f"TaskManager={self.taskmanager},"
                f"Testing={self.testing},"
                f"LoadOrder={self.load_order},"
            )
        return state

    @abstractmethod
    async def plugin_start(self) -> bool:
        """Starts plugin"""
        raise NotImplementedError("Not implemented")

    @abstractmethod
    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        raise NotImplementedError("Not implemented")

    async def start(self) -> bool:
        """Starts plugin"""
        self._log_info(f"Start plugin '{self.name}'")
        if self.started is False:
            self.started = await self.plugin_start()
            return self.started
        return self.started

    async def stop(self) -> bool:
        """Stops plugin"""
        self._log_info(f"Stop plugin '{self.name}'")
        if self.started is True:
            ret = await self.plugin_stop()
            self.started = False
            return ret
        return False

    def get_qweb_config(self) -> QwebConfig:
        """Retrieves qweb config"""
        runtime_qweb = get_qweb_runtime()
        return runtime_qweb.cfg_qweb

    def read_toml_file(self, file: str | ConfigFile) -> dict[str, Any]:
        """Reads toml file from config folder"""
        qweb_conf = self.get_qweb_config()
        config_path = qweb_conf.quart.config_folder
        if isinstance(file, ConfigFile):
            file = file.value
        fullname = f"{config_path}/{file}"
        if os.path.exists(fullname):
            with open(file=fullname, mode="rb") as pointer:
                return tomllib.load(pointer)
        return {}

    def register(self):
        """Registers itself at runtime"""
        runtime_qweb = get_qweb_runtime()
        if self.registered is False and runtime_qweb is not None:
            if self.taskmanager is not None:
                runtime_qweb.services.manager = self.taskmanager
            if self.authenticator is not None:
                runtime_qweb.services.authenticator = self.authenticator
            runtime_qweb.add_handlers(self.handlers)
            for backend in self.backends:
                runtime_qweb.add_backend(backend)
            runtime_qweb.add_object_layers(self.layers)
            runtime_qweb.add_apitasks(self.apitasks)
            runtime_qweb.add_systasks(self.systasks)
            self._log_info(f"Load  plugin '{self.name}'")
            self.registered = True
