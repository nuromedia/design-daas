import os
import aiohttp
from dataclasses import dataclass
from app.daas.adapter.adapter_http import HttpAdapterConfig
from app.daas.vm.proxmox.ProxmoxRestRequest import ProxmoxRestRequest, ProxmoxRestConfig
from app.daas.vm.proxmox.ProxmoxConfigStore import (
    ProxmoxConfigStore,
    ProxmoxConfigStoreConfig,
)
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class ProxmoxApiConfig:
    """
    Config for Proxmox
    """

    node: str
    hostIp: str
    prefixip: str
    main_folder: str
    storage_iso: str
    storage_img: str
    storage_ceph: str
    bridge_name_daas: str
    bridge_cidr_daas: str
    bridge_gw_daas: str
    bridge_adapter_daas: str
    bridge_name_inst: str
    bridge_cidr_inst: str
    bridge_adapter_inst: str
    bridge_name_ceph: str
    bridge_cidr_ceph: str
    bridge_adapter_ceph: str
    bridge_name_cluster: str
    bridge_cidr_cluster: str
    bridge_adapter_cluster: str
    prefixmac: str


class ApiProxmox(Loggable):
    """
    Api Component to interact with the proxmox backend service
    """

    def __init__(
        self,
        cfg_api: ProxmoxApiConfig,
        cfg_rest: ProxmoxRestConfig,
        cfg_http: HttpAdapterConfig,
    ):
        Loggable.__init__(self, LogTarget.VM)
        self.config_prox = cfg_api
        self.config_prox_http = cfg_http
        self.rest = ProxmoxRestRequest(cfg_rest, cfg_http)
        cfg_store = ProxmoxConfigStoreConfig(
            storage_iso=self.config_prox.storage_iso,
            storage_img=self.config_prox.storage_img,
            storage_ceph=self.config_prox.storage_ceph,
            bridge_name_daas=self.config_prox.bridge_name_inst,
            prefixmac=self.config_prox.prefixmac,
        )
        self.config_store = ProxmoxConfigStore(cfg_store)

    async def connection_test(self):
        """
        Tests connection of utilized backend-services
        """
        result = True

        res_prox, _ = await self.prox_connection_test()
        if res_prox is not None and res_prox.status != 200:
            self._log_error("Connection test failed: 'proxmox'")
            result = False
        else:
            self._log_info("Connection test successful: 'proxmox'")
        # res_node = self.node_connection_test()
        # if res_node != 0:
        #     logger.error("Connection test failed: 'node'")
        #     result = False
        # else:
        #     logger.info("Connection test successful: 'node'")
        return result

    async def configure_services(self):
        """
        Configures proxmox initially (Storage+Network)
        """

        ret_iso = await self.configure_storage_iso()
        ret_img = await self.configure_storage_img()

        ret_brg = await self.configure_network()

        if ret_iso == 0 and ret_img == 0 and ret_brg == 0:
            return 0
        return 1

    async def configure_storage_iso(self) -> int:
        """
        Configures proxmox iso storage
        """
        check_iso, _ = await self.prox_storage_status(
            self.config_prox.node, self.config_prox.storage_iso
        )
        self._log_info(f"Configure storage 'iso': {check_iso.status}")
        if check_iso is None:
            return 1
        if check_iso.status == 200:
            return 0
        self._log_info(f"Create storage 'iso': {check_iso.status}")
        ret_iso, _ = await self.prox_storage_create(
            self.config_prox.node,
            storage_name=self.config_prox.storage_iso,
            storage_type="dir",
            storage_path=f"/home/{self.config_prox.storage_iso}",
            storage_content="iso",
        )
        if ret_iso is not None and ret_iso.status == 200:
            return 0
        return 1

    async def configure_storage_img(self) -> int:
        """
        Configures proxmox image storage
        """
        check_iso, _ = await self.prox_storage_status(
            self.config_prox.node, self.config_prox.storage_img
        )
        self._log_info(f"Configure storage 'img': {check_iso.status}")
        if check_iso is None:
            return 1
        if check_iso.status == 200:
            return 0
        self._log_info(f"Create storage 'img': {check_iso.status}")
        ret_iso, _ = await self.prox_storage_create(
            self.config_prox.node,
            storage_name=self.config_prox.storage_img,
            storage_type="dir",
            storage_path=f"/home/{self.config_prox.storage_img}",
            storage_content="images",
        )
        if ret_iso is not None and ret_iso.status == 200:
            return 0
        return 1

    async def configure_network(self) -> int:
        """
        Configures proxmox network
        """
        br0 = None
        br1 = None
        br8 = None
        br9 = None
        check_br0, _ = await self.prox_network_status(self.config_prox.node, "vmbr0")
        if check_br0.status != 200:
            self._log_info(f"vmbr0 {self.config_prox.bridge_cidr_daas}")
            await self.prox_network_revert_vmbr0(self.config_prox.node)
            if self.config_prox.bridge_adapter_daas != "":
                self._log_debug("Unset adapter IP")
                adapter, adapter_data = await self.prox_network_set_adapter(
                    self.config_prox.node,
                    net_name=f"{self.config_prox.bridge_adapter_daas}",
                    net_type="eth",
                    net_cidr="0.0.0.0/32",
                    net_autostart=True,
                )
                self._log_debug(f"ADAPTER RESET: {adapter} -> {adapter_data}")
            br0, _ = await self.prox_network_create(
                self.config_prox.node,
                net_name=f"{self.config_prox.bridge_name_daas}",
                net_type="bridge",
                net_cidr=f"{self.config_prox.bridge_cidr_daas}",
                gateway=f"{self.config_prox.bridge_gw_daas}",
                net_autostart=True,
                bridge_ports=f"{self.config_prox.bridge_adapter_daas}",
            )
        else:
            br0 = True
        check_br1, _ = await self.prox_network_status(self.config_prox.node, "vmbr1")
        if check_br1.status != 200:
            self._log_info(f"vmbr1 {self.config_prox.bridge_cidr_inst}")
            br1, _ = await self.prox_network_create(
                self.config_prox.node,
                net_name=self.config_prox.bridge_name_inst,
                net_type="bridge",
                net_cidr=f"{self.config_prox.bridge_cidr_inst}",
                net_autostart=True,
            )
        else:
            br1 = True
        check_br8, _ = await self.prox_network_status(self.config_prox.node, "vmbr8")
        if check_br8.status != 200:
            self._log_info(f"vmbr8 {self.config_prox.bridge_cidr_ceph}")
            br8, _ = await self.prox_network_create(
                self.config_prox.node,
                net_name=f"{self.config_prox.bridge_name_ceph}",
                net_type="bridge",
                net_cidr=f"{self.config_prox.bridge_cidr_ceph}",
                net_autostart=True,
            )
        else:
            br8 = True
        check_br9, _ = await self.prox_network_status(self.config_prox.node, "vmbr9")
        if check_br9.status != 200:
            self._log_info(f"vmbr9 {self.config_prox.bridge_cidr_cluster}")
            br9, _ = await self.prox_network_create(
                self.config_prox.node,
                net_name=f"{self.config_prox.bridge_name_cluster}",
                net_type="bridge",
                net_cidr=f"{self.config_prox.bridge_cidr_cluster}",
                net_autostart=True,
            )
        else:
            br9 = True
        if br0 is None or br1 is None or br8 is None or br9 is None:
            self._log_error("One or more bridges were not created!")
            return 1
        self._log_info("Bridges ready")
        return 0

    async def connect(self):
        """Connects the component"""
        response, data = await self.prox_connection_test()
        if response.status != 200:
            print(f"Error: {data}")
            self.connected = False
        else:
            self.connected = True
        return self.connected

    async def disconnect(self) -> bool:
        """Disconnects the component"""
        self.docker = None
        self.connected = False
        return True

    async def prox_connection_test(self) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Test to check if the service is available
        """
        url = "nodes/"
        return await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )

    async def prox_vmstart(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Starts the specified vm via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/status/start"
        return await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data={}, files={}
        )

    async def prox_vmstop(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Stops the specified vm via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/status/stop"
        return await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data={}, files={}
        )

    async def prox_vmsuspend(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Suspends the vm and via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/status/suspend"
        return await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data={}, files={}
        )

    async def prox_vmresume(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Resumes the vm and via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/status/resume"
        return await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data={}, files={}
        )

    async def prox_vmrestart(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Restarts the specified vm via proxmox api
        """
        result, data = await self.prox_vmstop(vmnode, vmid)
        if result is not None and result.status == 200:
            result, data = await self.prox_vmstart(vmnode, vmid)
        return result, data

    async def prox_vmstartvnc(
        self, vmnode: str, vmid: int, password: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Starts vnc within the specified vm
        """
        result, data = await self.prox_vmmonitor(
            vmnode, vmid, f"set_password vnc {password} -d vnc2"
        )
        if result is not None and result.status == 200:
            result, data = await self.prox_vmmonitor(
                vmnode, vmid, "expire_password vnc never -d vnc2"
            )
        self._log_info(f"vnc configured for vm {vmid}")
        return result, data

    async def prox_vmmonitor(
        self, vmnode: str, vmid: int, monitor: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Runs the specified monitor command via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/monitor"
        return await self.rest.session_request_sync(
            "post", vmnode, url, {"command": monitor}, data={}, files={}
        )

    async def prox_vmstatus(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Returns status for the specified vm via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/status/current"
        return await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )

    async def prox_vmlist(self, vmnode: str) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Lists all vms via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/"
        return await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )

    async def prox_vmcreate(
        self,
        vmnode: str,
        vmid: int,
        name: str,
        ostype: str,
        cores: int,
        memsize: int,
        disksize: int,
        ceph_pool: bool,
        iso_installer: str,
        keyboard_layout: str,
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Creates a new vm via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/"
        obj = self.config_store.create_vmconf_installation(
            vmid=vmid,
            name=name,
            ostype=ostype,
            cores=cores,
            memsize=memsize,
            disksize=disksize,
            ceph_pool=ceph_pool,
            iso_installer=iso_installer,
            keyboard_layout=keyboard_layout,
        )

        return await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data=obj, files={}
        )

    async def prox_vmdelete(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Deletes a vm via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}"
        return await self.rest.session_request_async(
            "delete", url, params={}, data={}, files={}
        )

    async def prox_vmconfig_get(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Retrieves a vm config via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/config"
        return await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )

    async def prox_vmconfig_set(
        self, vmnode: str, vmid: int, cfg: dict
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Posts new vm config to proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/config"
        result, data = await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data=cfg, files={}
        )
        return result, data

    # pylint: disable=too-many-arguments
    async def prox_vmconfig_set_pre_install(
        self,
        vmnode: str,
        vmid: int,
        name: str,
        ostype: str,
        cores: int,
        memsize: int,
        disksize: int,
        ceph_pool: bool,
        iso_installer: str,
        keyboard_layout: str,
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Posts new vm config to proxmox api
        """
        cfg = self.config_store.create_vmconf_installation(
            vmid=vmid,
            name=name,
            ostype=ostype,
            cores=cores,
            memsize=memsize,
            disksize=disksize,
            ceph_pool=ceph_pool,
            iso_installer=iso_installer,
            keyboard_layout=keyboard_layout,
        )
        return await self.prox_vmconfig_set(vmnode, vmid, cfg)

    async def prox_vmconfig_set_post_install(
        self, vmnode: str, vmid: int, name: str, keyboard_layout: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Posts new vm config to proxmox api
        """
        cfg = self.config_store.create_vmconf_baseimage(vmid, name, keyboard_layout)
        return await self.prox_vmconfig_set(vmnode, vmid, cfg)

    async def prox_vmconfig_set_template(
        self, vmnode: str, vmid: int, name: str, keyboard_layout: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Posts new vm config to proxmox api
        """
        cfg = self.config_store.create_vmconf_template(vmid, name, keyboard_layout)
        return await self.prox_vmconfig_set(vmnode, vmid, cfg)

    async def prox_vmclone(
        self,
        vmnode: str,
        vmid: int,
        newid: int,
        snapname: str = "",
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Clones a vm via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/clone"
        data = {"newid": newid, "name": f"vm-{newid}"}
        if snapname != "":
            data["snapname"] = snapname

        return await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data=data, files={}
        )

    async def prox_vmsnapshot_list(
        self, vmnode: str, vmid: int
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Retrieves a list of all vm snapshots via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/snapshot"
        return await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )

    async def prox_vmsnapshot_create(
        self, vmnode: str, vmid: int, snapname: str, desc: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Creates a new vm snapshot via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/snapshot"
        result = await self.rest.session_request_sync(
            "post",
            vmnode,
            url,
            params={},
            data={"snapname": snapname, "description": desc, "vmstate": 1},
            files={},
        )
        return result

    async def prox_vmsnapshot_rollback(
        self, vmnode: str, vmid: int, snapname: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Restores a vm snapshot via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/snapshot/{snapname}/rollback"
        result = await self.rest.session_request_sync(
            "post",
            vmnode,
            url,
            params={},
            data={"snapname": snapname},
            files={},
        )
        return result

    async def prox_vmtemplate_convert(
        self, vmnode: str, vmid: int, disk: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Converts a base image into a template via proxmox api
        """
        url = f"nodes/{vmnode}/qemu/{vmid}/template"
        result = await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data={"disk": disk}, files={}
        )
        return result

    async def prox_storage_list(
        self, vmnode: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Lists info on all storages on the specified node
        """
        url = f"nodes/{vmnode}/storage/"
        result = await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )
        return result

    async def prox_storage_status(
        self,
        vmnode: str,
        name: str,
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Retrieves the status of a specified storage
        """
        url = f"nodes/{vmnode}/storage/{name}/status"
        result = await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )
        return result

    async def prox_storage_delete(
        self, storage_name: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Deletes a storage folder
        """
        return await self.rest.session_request_async(
            "delete", f"storage/{storage_name}", params={}, data={}, files={}
        )

    async def prox_storage_create(
        self,
        vmnode: str,
        *,
        storage_name: str,
        storage_type: str,
        storage_path: str,
        storage_content: str,
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Creates new storage folder on the specified node
        """
        obj = {
            "storage": storage_name,
            "type": storage_type,
            "path": storage_path,
            "content": storage_content,
        }
        result = await self.rest.session_request_sync(
            "post", vmnode, "storage", params={}, data=obj, files={}
        )
        return result

    async def prox_upload_iso(
        self,
        vmnode: str,
        filename: str,
        storage: str,
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Creates new storage folder on the specified node
        """

        if os.path.isfile(filename):
            name_only = os.path.basename(filename)
            with open(filename, "rb") as file_handle:
                result, data = await self.rest.session_request_sync(
                    "post",
                    vmnode,
                    f"nodes/{vmnode}/storage/{storage}/upload",
                    params={"content": "iso", "filename": name_only},
                    data={},
                    files={"filename": file_handle},
                )
                return result, data
        raise ValueError(f"Path not valid: {filename}")

    async def prox_network_revert(
        self, vmnode: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Reverts network configuration
        """
        url = f"nodes/{vmnode}/network/vmbr0"
        result = await self.rest.session_request_async(
            "delete", url, params={}, data={}, files={}
        )
        url = f"nodes/{vmnode}/network/vmbr1"
        result = await self.rest.session_request_async(
            "delete", url, params={}, data={}, files={}
        )
        url = f"nodes/{vmnode}/network/vmbr8"
        result = await self.rest.session_request_async(
            "delete", url, params={}, data={}, files={}
        )
        url = f"nodes/{vmnode}/network/vmbr9"
        result = await self.rest.session_request_async(
            "delete", url, params={}, data={}, files={}
        )
        return result

    async def prox_network_revert_vmbr0(
        self, vmnode: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Reverts network vmbr0 configuration
        """
        url = f"nodes/{vmnode}/network/vmbr0"
        result = await self.rest.session_request_async(
            "delete", url, params={}, data={}, files={}
        )
        return result

    async def prox_network_status(
        self, vmnode: str, iface: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Retrieves netwoprk status for specific interface
        """
        url = f"nodes/{vmnode}/network/{iface}"
        result = await self.rest.session_request_async(
            "get", url, params={}, data={}, files={}
        )
        return result

    async def prox_network_create(
        self,
        vmnode: str,
        *,
        net_name: str,
        net_type: str,
        net_cidr: str,
        net_autostart: bool,
        bridge_ports: str = "",
        gateway: str = "",
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Creates new network device specified node
        """
        obj = {
            "iface": net_name,
            "type": net_type,
            "cidr": net_cidr,
            "bridge_ports": bridge_ports,
            "autostart": net_autostart,
        }
        if gateway != "":
            obj["gateway"] = gateway

        url = f"nodes/{vmnode}/network"
        result = await self.rest.session_request_sync(
            "post", vmnode, url, params={}, data=obj, files={}
        )
        result = await self.rest.session_request_sync(
            "put", vmnode, url, params={}, data={}, files={}
        )
        return result

    async def prox_network_set_adapter(
        self,
        vmnode: str,
        *,
        net_name: str,
        net_type: str,
        net_cidr: str,
        net_autostart: bool,
        gateway: str = "",
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Creates new network device specified node
        """
        obj = {
            "iface": net_name,
            "type": net_type,
            "cidr": net_cidr,
            "autostart": net_autostart,
        }
        if gateway != "":
            obj["gateway"] = gateway

        url = f"nodes/{vmnode}/network/{net_name}"
        result = await self.rest.session_request_sync(
            "put", vmnode, url, params={}, data=obj, files={}
        )
        return result
