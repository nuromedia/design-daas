"""Container Backend"""

from app.daas.adapter.adapter_http import HttpAdapterConfig
from app.daas.common.enums import BackendName
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox, ProxmoxApiConfig
from app.daas.vm.proxmox.ProxmoxRestRequest import ProxmoxRestConfig
from app.qweb.service.service_context import QwebBackend


class VmBackend(QwebBackend):
    """Container backend"""

    cfg_api: ProxmoxApiConfig
    cfg_rest: ProxmoxRestConfig
    cfg_http: HttpAdapterConfig
    component: ApiProxmox

    def __init__(
        self,
        cfg_api: ProxmoxApiConfig,
        cfg_rest: ProxmoxRestConfig,
        cfg_http: HttpAdapterConfig,
    ):
        self.cfg_api = cfg_api
        self.cfg_rest = cfg_rest
        self.cfg_http = cfg_http
        self.component = ApiProxmox(self.cfg_api, self.cfg_rest, self.cfg_http)
        QwebBackend.__init__(self, name=BackendName.VM.value, component=self.component)

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects adapter"""
        if self.component is not None:
            self.connected = await self.component.connect()
            await self.component.configure_services()
            await self.component.connection_test()
            return self.connected
        return False

    async def disconnect(self) -> bool:
        """Disconnects adapter"""
        if self.component is not None:
            await self.component.disconnect()
            self.connected = self.component.connected
            return True
        return False
