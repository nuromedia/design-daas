"""VM plugin"""

from app.daas.adapter.adapter_http import HttpAdapterConfig
from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.vm.proxmox.ProxmoxApi import ProxmoxApiConfig
from app.daas.vm.proxmox.ProxmoxRestRequest import ProxmoxRestConfig
from app.plugins.platform.vm.vm_backend import VmBackend
from app.plugins.platform.vm.vm_tasks import (
    VMTask,
    vmclone,
    vmconfig_get,
    vmconfig_set_post_install,
    vmconfig_set_pre_install,
    vmcreate,
    vmdelete,
    vmlist,
    vmsnapshot_create,
    vmsnapshot_list,
    vmsnapshot_rollback,
    vmstart,
    vmstatus,
    vmstop,
    vmtemplate_convert,
)
from app.plugins.platform.vm.vm_tasks_sys import VMSystemTask, vmconfigure_proxmox_vnc
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.platform.vm.vm_routes import handler


class VmPlugin(PluginBase):
    """VM plugin"""

    def __init__(
        self,
    ):
        cfgfile_db = self.read_toml_file(ConfigFile.VM)
        self.cfg_api = ProxmoxApiConfig(**cfgfile_db[ConfigSections.VM_API.value])
        self.cfg_rest = ProxmoxRestConfig(**cfgfile_db[ConfigSections.VM_REST.value])
        self.cfg_http = HttpAdapterConfig(**cfgfile_db[ConfigSections.VM_HTTP.value])
        self.backend = VmBackend(self.cfg_api, self.cfg_rest, self.cfg_http)
        self.objlayer = None
        self.systasks = [
            (VMSystemTask.VM_CONFIGURE_PROXMOX_VNC.value, vmconfigure_proxmox_vnc),
        ]
        self.apitasks = [
            (VMTask.VM_LIST.value, vmlist),
            (VMTask.VM_STATUS.value, vmstatus),
            (VMTask.VM_CONFIG_GET.value, vmconfig_get),
            (VMTask.VM_CONFIG_SET_PRE.value, vmconfig_set_pre_install),
            (VMTask.VM_CONFIG_SET_POST.value, vmconfig_set_post_install),
            (VMTask.VM_SNAPSHOT_LIST.value, vmsnapshot_list),
            (VMTask.VM_SNAPSHOT_CREATE.value, vmsnapshot_create),
            (VMTask.VM_SNAPSHOT_ROLLBACK.value, vmsnapshot_rollback),
            (VMTask.VM_TEMPLATE_CONVERT.value, vmtemplate_convert),
            (VMTask.VM_START.value, vmstart),
            (VMTask.VM_STOP.value, vmstop),
            (VMTask.VM_DELETE.value, vmdelete),
            (VMTask.VM_CREATE.value, vmcreate),
            (VMTask.VM_CLONE.value, vmclone),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Platform,
            False,
            backends=[self.backend],
            layers=[],
            handlers=self.handlers,
            apitasks=self.apitasks,
            systasks=self.systasks,
            authenticator=None,
            taskmanager=None,
        )

    async def plugin_start(self) -> bool:
        """Starts plugin"""
        return await self.backend.connect()

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return await self.backend.disconnect()
