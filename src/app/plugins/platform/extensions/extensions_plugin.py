"""Extensions plugin"""

from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.proxy.proxy_extensions import ProxyExtensionsConfig
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.platform.extensions.extensions_routes import handler
from app.plugins.platform.extensions.extensions_backend import ExtensionsBackend
from app.plugins.platform.extensions.extensions_tasks import (
    ExtensionsTask,
    audio_ws,
    printer_ws,
)


class ExtensionsPlugin(PluginBase):
    """Extensionsplugin"""

    def __init__(
        self,
    ):
        cfgfile_ext = self.read_toml_file(ConfigFile.EXTENSIONS)
        self.cfg_proxy = ProxyExtensionsConfig(
            **cfgfile_ext[ConfigSections.EXTENSIONS.value]
        )
        self.backend = ExtensionsBackend(self.cfg_proxy)
        self.objlayer = None
        self.systasks = []
        self.apitasks = [
            (ExtensionsTask.EXTENSIONS_WSS_PRINTER.value, printer_ws),
            (ExtensionsTask.EXTENSIONS_WSS_AUDIO.value, audio_ws),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Platform,
            False,
            backends=[self.backend],
            layers=[],
            handlers=self.handlers,
            systasks=self.systasks,
            apitasks=self.apitasks,
            authenticator=None,
            taskmanager=None,
        )

    async def plugin_start(self) -> bool:
        """Starts plugin"""
        return await self.backend.connect()

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return await self.backend.disconnect()
