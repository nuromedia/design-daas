"""Extensions Backend"""

from app.daas.common.enums import BackendName
from app.daas.proxy.proxy_extensions import ProxyExtensions, ProxyExtensionsConfig
from app.qweb.service.service_context import QwebBackend


class ExtensionsBackend(QwebBackend):
    """Extensions backend"""

    cfg_ext: ProxyExtensionsConfig
    component: ProxyExtensions

    def __init__(
        self,
        cfg_ext: ProxyExtensionsConfig,
    ):
        self.cfg_ext = cfg_ext
        self.component = ProxyExtensions(self.cfg_ext)
        QwebBackend.__init__(
            self, name=BackendName.EXTENSIONS.value, component=self.component
        )

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects adapter"""
        if self.component is not None:
            self.connected = self.component.connect()
            return self.connected
        return False

    async def disconnect(self) -> bool:
        """Disconnects adapter"""
        if self.component is not None:
            self.component.disconnect()
            self.connected = self.component.connected
            return True
        return False
