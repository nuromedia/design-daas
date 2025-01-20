"""DaaS local authenticator"""

from app.daas.auth.auth_daas import DaasAuthenticatorBase
from app.qweb.auth.auth_qweb import QwebAuthenticatorBase, QwebUser
from app.qweb.blueprints.blueprint_info import BlueprintInfo
from app.qweb.common.config import QwebAuthenticatorConfig
from app.qweb.processing.processor import ProcessorRequest

DELAY_AUTH = 0.02


class DaasLocalAuthenticator(DaasAuthenticatorBase):
    """DaaS local authenticator"""

    def __init__(self, config: QwebAuthenticatorConfig):
        DaasAuthenticatorBase.__init__(self, config)

    async def verify_user(self, req: ProcessorRequest, info: BlueprintInfo) -> QwebUser:
        """Verifies only user"""
        result = QwebUser()
        if self.config.enable_auth_user:
            # self._log_info(f"200 -> DaaS Local Auth for bearer {req.bearer} {info.url}")
            result = await self.return_default_user()
        else:
            result = await self.return_default_user()
        return result

    async def verify_endpoint(
        self, req: ProcessorRequest, info: BlueprintInfo
    ) -> QwebUser:
        """Verifies only endpoint"""
        result = QwebUser()
        if self.config.enable_auth_endpoint:
            # self._log_info(
            #     f"200 -> DaaS Local Auth for endpoint {req.bearer} ({info.url})"
            # )
            result = await self.return_default_user()
        else:
            result = await self.return_default_user()
        return result
