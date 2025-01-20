"""Baseclass for a virtualized object using Guacamole."""

from dataclasses import dataclass
from typing import Optional

from app.daas.common.ctx import (
    create_response_by_data_attribute,
    create_response_by_exitstatus,
)
from app.daas.common.enums import BackendName
from app.daas.objects.base_object import DaasBaseObject
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.config_factory import (
    create_args_config,
    create_args_post_install,
    create_args_pre_install,
)
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.qweb.common.qweb_tools import get_backend_component
from app.qweb.processing.processor import QwebResult


@dataclass(kw_only=True)
class MachineBase(DaasBaseObject):
    """Configuration for a virtualized object using Guacamole."""

    async def start(
        self,
        userid: int,
        connect: bool = False,
        object_mode: str = "",
        keep_connections: bool = False,
    ) -> Optional[InstanceObject]:
        """Start the application."""
        assert await self.verify_demand(userid)
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        if await self.start_prepare(keep_connections):
            response, _ = await api.prox_vmstart(api.config_prox.node, self.id_proxmox)
            if response is not None and response.status == 200:
                if await self.start_finalize(userid, True, object_mode=object_mode):
                    return await self._return_connected_instance(connect)
        return None

    async def stop(self, instance: InstanceObject, force: bool) -> bool:
        """Stop and delete the instance."""
        # TODO: Handle pending tasks -> await taskman.stop_object_tasks(self.id)
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        if await self.stop_prepare(instance, force):
            await api.prox_vmstop(api.config_prox.node, instance.app.id_proxmox)
            return await self.stop_finalize(instance)
        return True

    async def vmtemplate_convert(self, disk: str) -> QwebResult:
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        args = await create_args_config(self.id_proxmox, disk=disk)
        response, data = await api.prox_vmtemplate_convert(**args)
        return await create_response_by_exitstatus(data, response, False)

    async def vmsnapshot_create(self, snapname: str, desc: str) -> QwebResult:
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        args = await create_args_config(self.id_proxmox, snapname=snapname, desc=desc)
        response, data = await api.prox_vmsnapshot_create(**args)
        return await create_response_by_exitstatus(data, response, False)

    async def vmsnapshot_list(self) -> QwebResult:
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        args = await create_args_config(self.id_proxmox)
        response, data = await api.prox_vmsnapshot_list(**args)
        return await create_response_by_data_attribute(data, response)

    async def vmsnapshot_rollback(self, snapname: str) -> QwebResult:
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        args = await create_args_config(self.id_proxmox, snapname=snapname)
        response, data = await api.prox_vmsnapshot_rollback(**args)
        return await create_response_by_exitstatus(data, response, False)

    async def vmconfig_get(self) -> QwebResult:
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        args = await create_args_config(self.id_proxmox)
        response, data = await api.prox_vmconfig_get(**args)
        return await create_response_by_data_attribute(data, response)

    async def vmconfig_set_pre_install(self, args: dict) -> QwebResult:
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        args = await create_args_pre_install(self.id_proxmox, args)
        response, data = await api.prox_vmconfig_set_pre_install(**args)
        return await create_response_by_exitstatus(data, response, False)

    async def vmconfig_set_post_install(self, args: dict) -> QwebResult:
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        args = await create_args_post_install(self.id_proxmox, args)
        response, data = await api.prox_vmconfig_set_post_install(**args)
        return await create_response_by_exitstatus(data, response, False)

    async def choose_template_root(self, ostype: str) -> str:
        """Choose isofile for specified operating system"""
        result = ""
        if ostype == "win10":
            result = "win10-daas.iso"
        elif ostype == "win11":
            result = "win11-daas.iso"
        elif ostype == "l26" or ostype == "l26vm":
            result = "debian12-daas.iso"
        return result
