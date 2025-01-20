"""Auth plugin"""

from app.daas.common.enums import ConfigFile, ConfigSections
from app.qweb.common.config import (
    QwebAuthenticatorConfig,
    QwebLocalAuthenticatorConfig,
    QwebRemoteAuthenticatorConfig,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.core.auth.auth_backend import AuthBackend
from app.plugins.core.auth.auth_routes import handler


class AuthPlugin(PluginBase):
    """Authplugin"""

    def __init__(
        self,
    ):
        sect_auth = ConfigSections.AUTH.value
        sect_local = ConfigSections.AUTH_LOCAL.value
        sect_remote = ConfigSections.AUTH_REMOTE.value
        cfgfile_auth = self.read_toml_file(ConfigFile.AUTH)
        cfglocal = QwebLocalAuthenticatorConfig(**cfgfile_auth[sect_auth][sect_local])
        cfgremote = QwebRemoteAuthenticatorConfig(
            **cfgfile_auth[sect_auth][sect_remote]
        )
        dictargs: dict = cfgfile_auth[sect_auth]
        if sect_local in dictargs:
            dictargs.pop(sect_local)
        if sect_remote in dictargs:
            dictargs.pop(sect_remote)
        self.cfg = QwebAuthenticatorConfig(
            **cfgfile_auth[sect_auth], local=cfglocal, remote=cfgremote
        )
        self.backend = AuthBackend(self.cfg)
        self.obj_layer = []
        self.systasks = []
        self.apitasks = []
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Core,
            False,
            backends=[self.backend],
            layers=self.obj_layer,
            handlers=self.handlers,
            systasks=self.systasks,
            apitasks=self.apitasks,
            authenticator=self.backend.auth,
            taskmanager=None,
        )

    async def plugin_start(self) -> bool:
        """Starts plugin"""
        return await self.backend.connect()

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return await self.backend.disconnect()
