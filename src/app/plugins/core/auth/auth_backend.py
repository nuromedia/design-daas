"""DB Backend"""

from typing import Optional
from app.daas.adapter.adapter_http import HttpAdapterConfig
from app.daas.auth.auth_daas_local import DaasLocalAuthenticator
from app.daas.auth.auth_daas_remote import DaasRemoteAuthenticator
from app.daas.common.enums import BackendName
from app.qweb.auth.auth_qweb import QwebAuthenticatorBase
from app.qweb.common.config import QwebAuthenticatorConfig
from app.qweb.service.service_context import QwebBackend


# pylint: disable=too-few-public-methods
class AuthBackend(QwebBackend):
    """Core backend"""

    cfg: QwebAuthenticatorConfig
    auth: QwebAuthenticatorBase

    def __init__(self, cfg: QwebAuthenticatorConfig):
        self.cfg = cfg
        if self.cfg.authenticator_type == "remote":
            self.cfg_http = HttpAdapterConfig(
                verify_tls=self.cfg.enable_verify_tls,
                logging=self.cfg.enable_logging,
                logrequests=self.cfg.enable_log_requests,
                logresults=self.cfg.enable_log_results,
            )
            self.auth = DaasRemoteAuthenticator(self.cfg, self.cfg_http)
        else:
            self.auth = DaasLocalAuthenticator(self.cfg)

        QwebBackend.__init__(self, name=BackendName.AUTH.value, component=self.auth)

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return state

    async def connect(self) -> bool:
        """Connects adapter"""
        self.connected = True
        return self.connected

    async def disconnect(self) -> bool:
        """Disconnects adapter"""
        self.connected = True
        return True
