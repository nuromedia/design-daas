"""Task to configure objects after being started"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from app.daas.common.enums import BackendName
from app.daas.common.model import DaasObject
from app.daas.node.nodecontrol import NodeController
from app.daas.objects.object_instance import InstanceObject
from app.daas.proxy.proxy_extensions import ProxyExtensions
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.plugins.platform.messaging.messaging_backend import MessagingBackend
from app.qweb.common.common import SystemTaskArgs
from app.qweb.common.qweb_tools import get_backend, get_backend_component, get_database
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.processing.processor import QwebResult


@dataclass
class PostbootConfig:
    args: SystemTaskArgs
    configure_connection: bool
    wait_for_reboot: bool
    wait_for_boot: bool


class PostbootTask(Loggable):
    """Task to configure objects after being started"""

    def __init__(self, cfg: PostbootConfig):
        Loggable.__init__(self, LogTarget.TASK)
        self.cfg = cfg
        self.use_qmsg = False

    async def prepare(self):
        qmsg = await get_backend(BackendName.MESSAGING, MessagingBackend)
        if qmsg is not None:
            if qmsg.cfg_main.enable_message_queue:
                self.use_qmsg = True

    async def run(self) -> QwebResult:
        from app.daas.db.database import Database

        args = self.cfg
        dbase = await get_database(Database)
        obj = await dbase.get_daas_object(args.args.id_object)
        inst = await dbase.get_instance_by_id(args.args.id_instance)
        assert obj is not None
        assert inst is not None

        configured = False
        if self.cfg.configure_connection:
            configured = await self.configure_connection(obj, inst)

        booted = False
        if self.cfg.wait_for_reboot:
            booted = await self.wait_for_reboot(inst)
        if self.cfg.wait_for_boot:
            booted = await self.wait_for_boot(inst)

        await self._add_printer(inst)

        if booted and configured:
            result = QwebResult(200, {})
        else:
            result = QwebResult(400, {}, 1, "Postboot task failed")
        self._log_info(f"Leaving postboot task (instance={inst.id})")
        self._log_info(f"Result was {result}")
        return result

    async def wait_for_boot(self, inst: InstanceObject) -> bool:
        online = await inst.check_online_state()
        while online is False:
            online = await inst.check_online_state()
            await asyncio.sleep(1)
            self._log_info("Loop wait postboot task")
        await self.update_boot_time(inst)
        self._log_info(f"Waited for boot (instance={inst.id})", 0)
        return online

    async def update_boot_time(self, inst: InstanceObject) -> bool:
        from app.daas.objects.object_container import ContainerObject
        from app.daas.objects.object_machine import MachineObject

        if inst.booted_at == inst.created_at:
            inst.booted_at = datetime.now()
            if isinstance(inst.app, MachineObject | ContainerObject):
                #     if inst.app.object_mode == "debug":
                #         inst.app.object_mode_extended = "done"
                await inst.app.update()
        return await inst.update()

    async def wait_for_reboot(self, inst: InstanceObject) -> bool:
        shutdown = await self.wait_for_shutdown(inst)
        code = 0 if shutdown is True else 1
        online = await self.wait_for_boot(inst)
        code = 0 if online else 1
        self._log_info(f"Waited for reboot (instance={inst.id})", code)
        return online

    async def wait_for_shutdown(self, inst: InstanceObject) -> bool:
        online = await inst.check_online_state()
        if online is False:
            self._log_info(f"Shutdown-Wait not needed (instance={inst.id})", True)
            return True

        while online is True:
            online = await inst.check_online_state()
            await asyncio.sleep(0)
        code = 0 if online is False else 1
        self._log_info(f"Waited for shutdown (instance={inst.id})", code)
        return online

    async def configure_connection(self, obj: DaasObject, inst: InstanceObject) -> bool:
        from app.daas.objects.object_machine import MachineObject

        vmapi = await get_backend_component(BackendName.VM, ApiProxmox)
        nodeapi = await get_backend_component(BackendName.NODE, NodeController)
        instid = self.cfg.args.id_instance
        objid = obj.id_proxmox
        node = vmapi.config_prox.node
        pw = obj.vnc_password
        adr = inst.host
        if isinstance(obj, MachineObject):
            vnc, _ = await vmapi.prox_vmstartvnc(node, objid, pw)
            if vnc is None or vnc.status != 200:
                self._log_error(f"Configure vnc failed ({instid})")
                return False
            dhcp, _, _ = await nodeapi.node_vmconfigure_dhcp(objid, adr)
            if dhcp != 0:
                self._log_error(f"Configure dhcp failed ({instid})")
                return False
            ip, _, _ = await nodeapi.node_vmconfigure_iptables(adr)
            if ip != 0:
                self._log_error(f"Configure iptables failed ({instid})")
                return False
        self._log_info(f"Connection configured (instance={instid})", 0)
        return True

    async def _add_printer(self, instance: InstanceObject):
        self._log_info(f"Adding printer for {instance.host}")
        # extensions = await get_backend_component(
        #     BackendName.EXTENSIONS, ProxyExtensions
        # )
        # iswin = instance.app.os_type in ("win10", "win11")
        # result = await extensions.add_printer_instance(
        #     instance.host, instance.app.id_owner, iswin
        # )
        return True
        # return result
