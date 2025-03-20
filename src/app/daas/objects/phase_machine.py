"""Baseclass for a virtualized object using Guacamole."""

from dataclasses import dataclass
from app.daas.common.enums import BackendName
from app.daas.common.model import DaasObject
from app.daas.objects.base_machine import MachineBase
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.qweb.common.qweb_tools import get_backend_component, get_database

DEFAULT_KEYBOARD_LAYOUT = "de"


@dataclass(kw_only=True)
class MachinePhase(MachineBase):
    """Configuration for a virtualized object using Guacamole."""

    async def create(self, args: dict) -> tuple[int, str, str]:
        if await self._phase_new_check_args(args):
            if await self._phase_new_consume_args(args):
                if await self._phase_new_check_limit():
                    if await self._phase_new_init(args):
                        return 0, "", ""
                    return 1, "", "Error during object preparation"
                return 3, "", "Insufficient ressource limits"
            return 4, "", "Error on argument consumption"
        return 5, "", "Required arguments missing"

    async def clone(self, oldid: str, args: dict) -> tuple[int, str, str]:
        if await self._phase_clone_check_args(args):
            old = await self._get_db_object(oldid)
            if old is not None:
                if await self._phase_clone_consume_args(old, args):
                    if await self._check_resource_limit():
                        if await self._phase_clone_init(old, args):
                            return 0, "", ""
                        return 1, "", "Error during object preparation"
                    return 2, "", "Insufficient ressource limits"
                return 3, "", "Error on argument consumption"
            return 4, "", "No object to cllone from"
        return 5, "", "Required arguments missing"

    async def _phase_new_consume_args(self, args: dict) -> bool:
        self.id = args["id"]
        self.hw_cpus = int(args["cores"])
        self.hw_memory = int(args["memsize"])  # * 1024**2
        self.hw_disksize = int(args["disksize"])  # * 1024**3
        self.id_proxmox = await self._suggested_vmid_by_db()
        self._log_info(f"Suggested VMID: {self.id_proxmox}")
        if (self.id_proxmox >= 100 <= 254) is False:
            self._log_info(f"Suggested proxmox id is out of range: {self.id_proxmox}")
            return False
        self.vnc_port_system = 5900 + self.id_proxmox
        self.id_user = args["name"]
        self.os_type = args["os_type"]
        self.os_installer = await self.choose_template_root(self.os_type)
        if self.os_installer == "":
            self._log_info("No os_installer")
            return False
        return True

    async def _phase_clone_consume_args(self, old: DaasObject, args: dict) -> bool:
        self.inherit_object_properties(old)
        self.object_state = "baseimage-create"
        self.id = args["newid"]
        self.id_user = args["name"]
        self.id_owner = args["id_owner"]
        self.os_type = old.os_type
        self.id_docker = ""
        self.id_proxmox = await self._suggested_vmid_by_db()
        self._log_info(f"Suggested VMID: {self.id_proxmox}")
        if (self.id_proxmox >= 100 <= 254) is False:
            self._log_info(f"Suggested proxmox id is out of range: {self.id_proxmox}")
            return False
        self.vnc_port_system = 5900 + self.id_proxmox
        self.hw_cpus = old.hw_cpus
        self.hw_memory = old.hw_memory
        self.hw_disksize = old.hw_disksize
        self.os_installer = old.os_installer
        return True

    async def _suggested_vmid_by_db(self):
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        return await dbase.suggest_vmid()

    async def _phase_new_init(self, args: dict, keep_connections: bool = False) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if await self.start_prepare(keep_connections) is False:
            self._log_error("start_prepare was not successful")
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        self._log_warn(f"DISKSIZE_ARGS: {args} {self.hw_disksize}")
        # Workaround: User gives disksize in gb but automated task gives size in bytes
        # Check if size > 0 and size/1024**3 == 0
        # If that is the case. size was given in gb and must be converted.
        # Reason: later functions expect bytes
        if self.hw_disksize > 0 and int(self.hw_disksize / 1024**3) == 0:
            self.hw_disksize = self.hw_disksize * 1024**3

        resp, _ = await api.prox_vmcreate(
            api.config_prox.node,
            self.id_proxmox,
            self.id_user,
            self.os_type,
            self.hw_cpus,
            int(self.hw_memory),
            int(self.hw_disksize / 1024**3),
            self.has_ceph_filesystems(),
            self.os_installer,
            args["kb"],
        )
        if resp is not None and resp.status == 200:
            return await dbase.create_daas_object(self)
        self._log_error("create vm object was not successful")
        return False

    async def _phase_clone_init(
        self, obj: DaasObject, args: dict, keep_connections: bool = False
    ) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if await self.start_prepare(keep_connections) is False:
            self._log_error("start_prepare was not successful")
        api = await get_backend_component(BackendName.VM, ApiProxmox)
        snapname = ""
        if "snapname" in args:
            snapname = args["snapname"]
        self._log_info(f"Cloning from {obj.id_proxmox} to {self.id_proxmox}")
        resp, _ = await api.prox_vmclone(
            api.config_prox.node, obj.id_proxmox, self.id_proxmox, snapname=snapname
        )
        if resp is not None and resp.status == 200:
            keyboard_layout = DEFAULT_KEYBOARD_LAYOUT
            if "kb" in args:
                keyboard_layout = args["kb"]
            response_conf, _ = await api.prox_vmconfig_set_post_install(
                api.config_prox.node,
                self.id_proxmox,
                name=self.id_user,
                keyboard_layout=keyboard_layout,
            )
            if response_conf is not None and response_conf.status == 200:
                return await dbase.create_daas_object(self)
        self._log_error("create vm object was not successful")
        return False

    async def _phase_new_check_limit(self) -> bool:
        return True

    async def _phase_clone_check_args(self, args: dict) -> bool:
        required = ["id", "newid", "name"]
        for k in required:
            if k in args is False:
                self._log_error(f"Required argument missing: {k}", 1)
                return False
        return await self._phase_new_check_id(args)

    async def _phase_new_check_args(self, args: dict) -> bool:
        required = [
            "id",
            "id_owner",
            "name",
            "cores",
            "memsize",
            "disksize",
            "kb",
            "os_type",
        ]
        for k in required:
            if k in args is False:
                self._log_error(f"Required argument missing: {k}", 1)
                return False
        return await self._phase_new_check_id(args)

    async def _phase_new_check_id(self, args: dict) -> bool:
        if "id" in args and args["id"] == "":
            self._log_error(f"Invalid argument: id='{args['id']}'", 2)
            return False
        return True
