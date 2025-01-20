"""Authenticates requests"""

from abc import abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Any, Optional
from app.qweb.blueprints.blueprint_info import AuthenticationMode, BlueprintInfo
from app.qweb.common.config import QwebAuthenticatorConfig
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.processing.processor import ProcessorRequest

DELAY_AUTH = 0.00


@dataclass
class QwebUser:
    """A qweb user"""

    id_user: int = -1
    name: str = "Unknown"
    authenticated: bool = False


class QwebAuthenticatorBase(Loggable):
    """Default authenticator"""

    config: QwebAuthenticatorConfig

    def __init__(self, config: QwebAuthenticatorConfig):
        self.config = config
        Loggable.__init__(self, LogTarget.AUTH)

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}" f"(type={self.config.authenticator_type})"
        )

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize component"""
        raise NotImplementedError("Not implemented")

    async def authenticate(
        self, req: ProcessorRequest, info: BlueprintInfo
    ) -> QwebUser:
        """Authenticates requests based on given information"""
        result = QwebUser()
        params = info.auth_params
        if params == AuthenticationMode.ALL:
            result = await self.verify_endpoint(req, info)
        elif params == AuthenticationMode.USER:
            result = await self.verify_user(req, info)
        elif params == AuthenticationMode.TOKEN:
            result = await self.verify_user(req, info)
        return result

    @abstractmethod
    async def verify_entity_ownership(self, entity: Optional[Any], owner: int) -> bool:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    async def verify_user(self, req: ProcessorRequest, info: BlueprintInfo) -> QwebUser:
        """Verifies only user"""
        raise NotImplementedError("Not implemented")

    @abstractmethod
    async def verify_endpoint(
        self, req: ProcessorRequest, info: BlueprintInfo
    ) -> QwebUser:
        """Verifies only endpoint"""
        raise NotImplementedError("Not implemented")

    async def _sleep(self, time_s: float):
        if time_s > 0:
            await asyncio.sleep(time_s)
