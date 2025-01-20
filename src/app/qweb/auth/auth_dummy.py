"""Authenticates requests"""

from app.qweb.auth.auth_qweb import QwebAuthenticatorBase, QwebUser
from app.qweb.blueprints.blueprint_info import BlueprintInfo
from app.qweb.common.config import QwebAuthenticatorConfig
from app.qweb.processing.processor import ProcessorRequest

DELAY_AUTH = 0.3
DUMMY_USER = 5


class QwebDummyAuthenticator(QwebAuthenticatorBase):
    """Dummy authenticator"""

    config: QwebAuthenticatorConfig

    def __init__(self, config: QwebAuthenticatorConfig):
        QwebAuthenticatorBase.__init__(self, config)

    async def initialize(self) -> bool:
        """Initialize component"""
        return True

    async def verify_user(self, req: ProcessorRequest, info: BlueprintInfo) -> QwebUser:
        """Verifies only user"""
        result = QwebUser(id_user=DUMMY_USER, name="dummy", authenticated=True)
        if self.config.enable_auth_user:
            print(f"Dummy Auth for bearer {info.url}")
            await self._sleep(DELAY_AUTH)
        return result

    async def verify_endpoint(
        self, req: ProcessorRequest, info: BlueprintInfo
    ) -> QwebUser:
        """Verifies only endpoint"""
        result = QwebUser(id_user=DUMMY_USER, name="dummy", authenticated=True)
        print(f"Dummy Auth for endpoint {info.url}")
        if self.config.enable_auth_endpoint:
            await self._sleep(DELAY_AUTH)
        return result
