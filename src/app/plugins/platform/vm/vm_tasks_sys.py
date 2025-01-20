"""VM Tasks"""

from enum import Enum
from nest_asyncio import asyncio
from app.daas.common.enums import BackendName
from app.daas.node.nodecontrol import NodeController
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.qweb.common.common import SystemTaskArgs
from app.qweb.common.qweb_tools import get_backend_component, get_database
from app.qweb.processing.processor import QwebResult


class VMSystemTask(Enum):
    """VM system tasktype"""

    VM_CONFIGURE_PROXMOX_VNC = "VM_CONFIGURE_PROXMOX_VNC"


async def vmconfigure_proxmox_vnc(args: SystemTaskArgs) -> QwebResult:
    """Configures proxmox vnc via monitor commands"""
    from app.daas.db.database import Database

    dbase = await get_database(Database)
    obj = await dbase.get_daas_object(args.id_object)
    inst = await dbase.get_instance_by_id(args.id_instance)
    vmapi = await get_backend_component(BackendName.VM, ApiProxmox)
    nodeapi = await get_backend_component(BackendName.NODE, NodeController)
    assert obj is not None
    assert inst is not None

    resp_vnc, _ = await vmapi.prox_vmstartvnc(
        vmapi.config_prox.node, obj.id_proxmox, obj.vnc_password
    )
    if resp_vnc is None or resp_vnc.status != 200:
        return QwebResult(400, {}, 1, "configure vnc failed")

    code_dhcp, out_dhcp, err_dhcp = await nodeapi.node_vmconfigure_dhcp(
        obj.id_proxmox, inst.host
    )
    if code_dhcp != 0:
        return QwebResult(400, {}, 2, f"{out_dhcp}{err_dhcp}")
    code_ip, out_ip, err_ip = await nodeapi.node_vmconfigure_iptables(inst.host)
    if code_ip != 0:
        return QwebResult(400, {}, 2, f"{out_ip}{err_ip}")

    while True:
        await asyncio.sleep(1)
    return QwebResult(200, {})
