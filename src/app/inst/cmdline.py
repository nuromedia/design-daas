"""
Commandline tool to invoke ApiDesign calls
"""
# pylint: disable=relative-beyond-top-level
import pprint
import os
import time
import tomllib

import click

from ..web.daas_web.backend.ApiDesign import ApiDesign
from ..web.daas_web.common.config import DaasConfiguration
from ..web.daas_web.tests.validation import validate_dataclass


DEFAULT_CONFIG_LOCATION = "/home/design-daas/backend/web/design-config.toml"


def load_conf(
    conf: DaasConfiguration | str | dict | None = None,
) -> DaasConfiguration:
    """
    Loads a new config
    """
    if conf is None:
        conf = os.environ.get("DESIGN_CONFIG", DEFAULT_CONFIG_LOCATION)

    if isinstance(conf, str):
        try:
            with open(conf, mode="rb") as file:
                conf = tomllib.load(file)
        except FileNotFoundError:
            print(f"could not open file {conf}")
            raise

    if isinstance(conf, dict):
        conf = validate_dataclass(
            DaasConfiguration,
            conf,
            env=os.environ,
            coerce_dataclass=True,
            warn_unknown=True,
        )

    assert isinstance(conf, DaasConfiguration)
    return conf


api = ApiDesign(load_conf(DEFAULT_CONFIG_LOCATION))


@click.group
def design():
    """
    APIDesign Commandline tool
    """


@design.command
def configure_services():
    """
    Configure services
    """
    return api.configure_services()


@design.command
def configure_network():
    """
    Configure network
    """
    return api.configure_network()


@design.command
def connection_test():
    """
    Test connection to all backend services
    """
    response = api.connection_test()
    if response:
        return 0
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("timeout", nargs=1, type=int)
def connection_test_instance_icmp(vmid: int, timeout: int):
    """
    Test connection to all backend services
    """
    # pylint: disable=unused-variable
    # pyright: ignore [reportUnusedVariable]
    code, std_out, std_err = api.inst_connection_test_icmp(vmid, timeout)
    if code:
        return 0
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("timeout", nargs=1, type=int)
def connection_test_instance_ssh(vmid: int, timeout: int):
    """
    Test connection to all backend services
    """
    # pylint: disable=unused-variable
    # pyright: ignore [reportUnusedVariable]
    code, std_out, std_err = api.inst_connection_test_ssh(vmid, timeout)
    if code:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmstart(vmnode: str, vmid: int):
    """
    Starts a vm via proxmox api
    """
    response = api.prox_vmstart(vmnode, vmid)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmstop(vmnode: str, vmid: int):
    """
    Stops the specified vm via proxmox api
    """
    response = api.prox_vmstop(vmnode, vmid)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmsuspend(vmnode: str, vmid: int):
    """
    Suspends the specified vm via proxmox api
    """
    response = api.prox_vmsuspend(vmnode, vmid)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmresume(vmnode: str, vmid: int):
    """
    Resumes the specified vm via proxmox api
    """
    response = api.prox_vmresume(vmnode, vmid)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmrestart(vmnode: str, vmid: int):
    """
    Restarts the specified vm via proxmox api
    """
    response = api.prox_vmrestart(vmnode, vmid)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("password", nargs=1)
def prox_vmstartvnc(vmnode: str, vmid: int, password: str):
    """
    Starts vnc within the specified vm
    """
    response = api.prox_vmstartvnc(vmnode, vmid, password)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("monitor", nargs=1)
def prox_vmmonitor(vmnode: str, vmid: int, monitor: str):
    """
    Runs the specified monitor command via proxmox api
    """
    response = api.prox_vmmonitor(vmnode, vmid, monitor)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmstatus(vmnode: str, vmid: int):
    """
    Prints status info via proxmox api
    """
    response = api.prox_vmstatus(vmnode, vmid)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
def prox_vmlist(vmnode: str):
    """
    Lists all vms via proxmox api
    """
    response = api.prox_vmlist(vmnode)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
def prox_storage_list(vmnode: str):
    """
    Lists all storage via proxmox api
    """
    response = api.prox_storage_list(vmnode)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
def prox_storage_status(vmnode: str, name: str):
    """
    Returns the status of a specified storage via proxmox api
    """
    response = api.prox_storage_status(vmnode, name)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("storage_name", nargs=1, type=str)
@click.argument("storage_type", nargs=1, type=str)
@click.argument("storage_path", nargs=1, type=str)
@click.argument("storage_content", nargs=1, type=str)
def prox_storage_create(
    vmnode: str,
    storage_name: str,
    storage_type: str,
    storage_path: str,
    storage_content: str,
):
    """
    Creates storage folder via proxmox api
    """
    response = api.prox_storage_create(
        vmnode,
        storage_name=storage_name,
        storage_type=storage_type,
        storage_path=storage_path,
        storage_content=storage_content,
    )
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("storage_name", nargs=1, type=str)
def prox_storage_delete(
    storage_name: str,
):
    """
    Deletes storage folder via proxmox api
    """
    response = api.prox_storage_delete(storage_name)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("ostype", nargs=1, type=str)
@click.argument("cores", nargs=1, type=int)
@click.argument("memsize", nargs=1, type=int)
@click.argument("disksize", nargs=1, type=int)
@click.argument("kb", nargs=1, type=str)
@click.argument("cdinst", nargs=1, type=str)
# pylint: disable=too-many-arguments
def prox_vmcreate(
    vmnode: str,
    vmid: int,
    ostype: str,
    cores: int,
    memsize: int,
    disksize: int,
    cdinst: str,
    keyboard: str,
) -> int:
    """
    Prepares vm config for installation via proxmox api
    """
    response = api.prox_vmcreate(
        vmnode,
        vmid,
        name=f"TODO{vmid}",
        ostype=ostype,
        cores=cores,
        memsize=memsize,
        disksize=disksize,
        iso_installer=cdinst,
        keyboard_layout=keyboard,
    )
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmdelete(vmnode: str, vmid: int):
    """
    Deletes a vm via proxmox api
    """
    response = api.prox_vmdelete(vmnode, vmid)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("keyboard", nargs=1, type=str)
def prox_vmconfig_set_post_install(vmnode: str, vmid: int, keyboard: str):
    """
    Configure vm for baseimage usage
    """
    response = api.prox_vmconfig_set_post_install(
        vmnode, vmid, f"basevm-{vmid}", keyboard
    )
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmconfig_get(vmnode: str, vmid: int):
    """
    Prints status info via proxmox api
    """
    response = api.prox_vmconfig_get(vmnode, vmid)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def prox_vmsnapshot_list(vmnode: str, vmid: int):
    """
    Retrieves a list of all vm snapshots via proxmox api
    """
    response = api.prox_vmsnapshot_list(vmnode, vmid)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("snapname", nargs=1)
@click.argument("desc", nargs=1)
def prox_vmsnapshot_create(vmnode: str, vmid: int, snapname: str, desc: str):
    """
    Creates a new vm snapshot via proxmox api
    """
    response = api.prox_vmsnapshot_create(vmnode, vmid, snapname, desc)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("snapname", nargs=1)
def prox_vmsnapshot_rollback(vmnode: str, vmid: int, snapname: str):
    """
    Restores a vm snapshot via proxmox api
    """
    response = api.prox_vmsnapshot_rollback(vmnode, vmid, snapname)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("disk", nargs=1)
def prox_vmtemplate_convert(vmnode: str, vmid: int, disk: str):
    """
    Restores a vm snapshot via proxmox api
    """
    response = api.prox_vmtemplate_convert(vmnode, vmid, disk)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("newid", nargs=1, type=int)
@click.argument("snapname", nargs=1)
def prox_vmclone(vmnode: str, vmid: int, newid: int, snapname: str):
    """
    Clones a vm via proxmox api
    """
    response = api.prox_vmclone(vmnode, vmid, newid, snapname)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("net_name", nargs=1, type=str)
@click.argument("net_type", nargs=1, type=str)
@click.argument("net_cidr", nargs=1, type=str)
@click.argument("net_autostart", nargs=1, type=bool)
def prox_network_create(
    vmnode: str,
    net_name: str,
    net_type: str,
    net_cidr: str,
    net_autostart: bool,
):
    """
    Creates a new network device
    """
    response = api.prox_network_create(
        vmnode,
        net_name=net_name,
        net_type=net_type,
        net_cidr=net_cidr,
        net_autostart=net_autostart,
    )
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("iface", nargs=1, type=str)
def prox_network_status(vmnode: str, iface: str):
    """
    Retrieves status for a specific network device
    """
    response = api.prox_network_status(vmnode, iface)
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
def prox_network_revert(vmnode: str):
    """
    Clones a vm via proxmox api
    """
    response = api.prox_network_revert(vmnode)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("filename", nargs=1, type=str)
@click.argument("storage", nargs=1, type=str)
def prox_upload_iso(
    vmnode: str,
    filename: str,
    storage: str,
):
    """
    uploads iso image to proxmox backend
    """
    response = api.prox_upload_iso(vmnode, filename, storage)
    if response is not None and response.status_code == 200:
        return 0
    if response is not None:
        print("REASON: " + str(response.reason))
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
def node_vmconfigure_dhcp(vmid: int):
    """
    Configures dhcp the vmid
    """
    ret = api.node_vmconfigure_dhcp(vmid=vmid)
    if ret is not None and ret[0] != 0:
        print(f"{ret[1]}{ret[2]}")
        return ret[0]
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
def node_vmconfigure_iptables(vmid: int):
    """
    Configures dhcp the vmid
    """
    ret = api.node_vmconfigure_iptables(vmid=vmid)
    if ret is not None and ret[0] != 0:
        print(f"{ret[1]}{ret[2]}")
        return ret[0]
    return 1


@design.command
def guac_conlist():
    """
    Lists all configured guacamole connections
    """
    response = api.gc_conlist()
    if response is not None and response.status_code == 200:
        pretty = pprint.PrettyPrinter(width=20)
        pretty.pprint(response.json())
        return 0
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("proto", nargs=1)
@click.argument("username", nargs=1)
@click.argument("password", nargs=1)
def guac_conadd(vmid: int, proto: str, username: str, password: str):
    """
    Adds a new guacamole connection
    """
    response = api.gc_conadd(vmid, proto, username, password)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("proto", nargs=1)
def guac_congetid(vmid: int, proto: str):
    """
    Gets guacamole connection-id by vmid
    """
    response = api.gc_congetid(vmid, proto)
    if response is not None and response > 0:
        print(str(response))
        return 0
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("proto", nargs=1)
def guac_condel(vmid: int, proto: str):
    """
    Deletes a connection
    """
    response = api.gc_condel(vmid, proto)
    if response is not None and response.status_code == 200:
        return 0
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("proto", nargs=1)
def guac_conurl(vmid: int, proto: str):
    """
    Prints a url for a specified guacamole connection
    """
    response = api.gc_conurl(vmid, proto)
    if response != "":
        print(f"URL: {response}")
        return 0
    return 1


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("cmd", nargs=1)
@click.argument("args", nargs=1)
def inst_vminvoke_action(vmid: int, cmd: str, args: str):
    """
    Invoke an action via client api (ssh+python)
    """
    ret, std_out, std_err = api.inst_vminvoke_action(vmid, cmd, args)
    print(f"{std_out}{std_err}")
    return ret


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("cmd", nargs=1)
@click.argument("args", nargs=1)
def inst_vminvoke_cmd(vmid: int, cmd: str, args: str):
    """
    Invoke a command line via client api (ssh+python)
    """
    ret, std_out, std_err = api.inst_vminvoke_cmd(vmid, cmd, args)
    print(f"{std_out}{std_err}")
    return ret


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("cmd", nargs=1)
@click.argument("args", nargs=1)
def inst_vminvoke_ssh(vmid: int, cmd: str, args: str):
    """
    Invoke a command line (ssh only)
    """
    ret, std_out, std_err = api.inst_vminvoke_ssh(vmid, cmd, args)
    print(f"{std_out}{std_err}")
    return ret


@design.command
@click.argument("vmid", nargs=1, type=int)
def inst_vmstatus(vmid: int):
    """
    Invoke a status action via client api (ssh+python)
    """
    ret, std_out, std_err = api.inst_vmstatus(vmid)
    print(f"{std_out}{std_err}")
    return ret


@design.command
@click.argument("vmid", nargs=1, type=int)
def inst_vmversion(vmid: int):
    """
    Invoke a version action via client api (ssh+python)
    """
    ret, std_out, std_err = api.inst_vmversion(vmid)
    print(f"{std_out}{std_err}")
    return ret


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("ostype", nargs=1, type=str)
@click.argument("cores", nargs=1)
@click.argument("memsize", nargs=1)
@click.argument("disksize", nargs=1)
@click.argument("cdrom", nargs=1)
# pylint: disable=too-many-arguments
def use_create_baseimage(
    vmnode: str,
    vmid: int,
    ostype: str,
    cores: int,
    memsize: int,
    disksize: int,
    cdrom: str,
):
    """
    Creates new baseimage
    """
    api.prox_vmcreate(
        vmnode,
        vmid,
        name=f"basevm-{vmid}",
        ostype=ostype,
        cores=cores,
        memsize=memsize,
        disksize=disksize,
        iso_installer=cdrom,
        keyboard_layout="de",
    )
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def use_finalize_baseimage(vmnode: str, vmid: int):
    """
    Finalizes baseimage
    """
    basename = f"basevm-{vmid}"
    api.prox_vmstop(vmnode, vmid)
    api.prox_vmconfig_set_post_install(vmnode, vmid, basename, "de")
    api.prox_vmtemplate_convert(vmnode, vmid, "virtio0")


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("newid", nargs=1, type=int)
def use_create_environment(vmnode: str, vmid: int, newid: int):
    """
    Creates new environment
    """
    api.prox_vmclone(vmnode, vmid, newid, "")
    api.prox_vmconfig_set_post_install(vmnode, newid, f"env-{newid}", "de")
    api.node_vmconfigure_dhcp(newid)
    api.node_vmconfigure_iptables(newid)


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def use_finalize_environment(vmnode: str, vmid: int):
    """
    Finalizes environment
    """
    api.prox_vmstop(vmnode, vmid)
    api.prox_vmsnapshot_create(vmnode, vmid, "env", "")


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
def use_create_deployment(vmnode: str, vmid: int):
    """
    Creates new deployment
    """
    api.prox_vmsnapshot_rollback(vmnode, vmid, "env")
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("deployname", nargs=1)
@click.argument("desc", nargs=1)
def use_finalize_deployment(
    vmnode: str, vmid: int, deployname: str, desc: str
):
    """
    Finalizes deployment
    """
    api.prox_vmsnapshot_create(vmnode, vmid, deployname, desc)
    api.prox_vmstop(vmnode, vmid)


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("deployname", nargs=1)
def use_create_appinstance(vmnode: str, vmid: int, deployname: str):
    """
    Runs app within deployment
    """
    api.prox_vmsnapshot_rollback(vmnode, vmid, deployname)
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("proto", nargs=1, type=str)
@click.argument("password", nargs=1, type=str)
def use_run_and_connect(vmnode: str, vmid: int, proto: str, password: str):
    """
    Runs vm and creates connector
    """
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)
    api.prox_vmstart(vmnode, vmid)
    api.prox_vmstartvnc(vmnode, vmid, password)
    api.gc_conupdate(vmid, proto, password, password)
    url = api.gc_conurl(vmid, proto)
    print(f"{vmid} -> {url}")


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("deployname", nargs=1)
@click.argument("proto", nargs=1, type=str)
@click.argument("password", nargs=1, type=str)
def use_run_and_connect_deployment(
    vmnode: str, vmid: int, deployname: str, proto: str, password: str
):
    """
    Runs vm and creates connector
    """
    api.prox_vmsnapshot_rollback(vmnode, vmid, deployname)
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)
    api.prox_vmstart(vmnode, vmid)
    api.prox_vmstartvnc(vmnode, vmid, password)
    api.gc_conupdate(vmid, proto, password, password)
    url = api.gc_conurl(vmid, proto)
    print(f"{vmid} -> {url}")


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("platform", nargs=1, type=str)
def testcase_baseimage_full(vmnode: str, vmid: int, platform: str):
    """
    Test create and finalize of baseimage
    """
    password = "user1234"
    basename = f"basevm-{vmid}"

    if platform == "win10":
        ostype = "win10"
        isofile = "win10-daas.iso"
    elif platform == "win11":
        ostype = "win11"
        isofile = "win11-daas.iso"
    elif platform == "debian12":
        ostype = "l26"
        isofile = "debian12-daas.iso"
    else:
        return

    proto = "vnc"
    api.prox_vmcreate(
        vmnode,
        vmid,
        name=basename,
        ostype=ostype,
        cores=4,
        memsize=4096,
        disksize=64,
        iso_installer=isofile,
        keyboard_layout="de",
    )
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)
    api.prox_vmstart(vmnode, vmid)
    api.prox_vmstartvnc(vmnode, vmid, password)
    api.gc_conupdate(vmid, proto, password, password)
    url = api.gc_conurl(vmid, proto)
    print(f"{vmid} -> {url}")
    api.inst_connection_test_ssh(vmid, 10000)
    api.inst_vminvoke_ssh(vmid, "shutdown /f /r /t 1", "")
    time.sleep(20)
    api.inst_connection_test_ssh(vmid, 1000)
    time.sleep(10)
    api.inst_vminvoke_ssh(vmid, "shutdown /f /s /t 1", "")
    time.sleep(15)
    api.prox_vmconfig_set_post_install(vmnode, vmid, basename, "de")
    api.prox_vmtemplate_convert(vmnode, vmid, "virtio0")


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("newid", nargs=1, type=int)
def testcase_environment_full(vmnode: str, vmid: int, newid: int):
    """
    Test create and finalize of environment
    """
    proto = "vnc"
    password = "user1234"
    api.prox_vmclone(vmnode, vmid, newid, "")
    api.prox_vmconfig_set_post_install(vmnode, newid, f"env-{newid}", "de")
    api.node_vmconfigure_dhcp(newid)
    api.node_vmconfigure_iptables(newid)
    api.prox_vmstart(vmnode, newid)
    api.prox_vmstartvnc(vmnode, newid, password)
    api.gc_conupdate(newid, proto, password, password)
    url = api.gc_conurl(newid, proto)
    print(f"{newid} -> {url}")
    api.inst_connection_test_ssh(newid, 10000)
    time.sleep(15)
    api.inst_vminvoke_ssh(newid, "shutdown /f /s /t 1", "")
    time.sleep(20)
    api.prox_vmsnapshot_create(vmnode, newid, "env", "")


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("deployname", nargs=1, type=str)
def testcase_deployment_full(vmnode: str, vmid: int, deployname: str):
    """
    Test create and finalize of deployment
    """
    proto = "vnc"
    password = "user1234"
    api.prox_vmsnapshot_rollback(vmnode, vmid, "env")
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)
    api.prox_vmstart(vmnode, vmid)
    api.prox_vmstartvnc(vmnode, vmid, password)
    api.gc_conupdate(vmid, proto, password, password)
    url = api.gc_conurl(vmid, proto)
    print(f"{vmid} -> {url}")
    api.inst_connection_test_ssh(vmid, 10000)
    time.sleep(15)
    api.prox_vmsnapshot_create(
        vmnode, vmid, deployname, f"custom{deployname} description"
    )
    api.prox_vmstop(vmnode, vmid)


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("deployname", nargs=1, type=str)
def testcase_appinstance_full(vmnode: str, vmid: int, deployname: str):
    """
    Test create and finalize of appinstance
    """
    proto = "vnc"
    password = "user1234"
    api.prox_vmsnapshot_rollback(vmnode, vmid, deployname)
    api.node_vmconfigure_dhcp(vmid)
    api.node_vmconfigure_iptables(vmid)
    api.prox_vmstartvnc(vmnode, vmid, password)
    api.gc_conupdate(vmid, proto, password, password)
    url = api.gc_conurl(vmid, proto)
    print(f"{vmid} -> {url}")
    api.inst_connection_test_ssh(vmid, 10000)
    api.inst_vminvoke_cmd(
        vmid,
        '\\"C:\\Program Files\\Microsoft Office\\root\\Office16\\winword.exe\\"',
        "",
    )


@design.command
@click.argument("vmid", nargs=1, type=int)
@click.argument("program", nargs=1, type=str)
def testcase_exec(vmid: int, program: str):
    """
    Test create and finalize of appinstance
    """
    proto = "vnc"
    password = "user1234"
    api.inst_vminvoke_cmd(vmid, f"\\\"{program}\\\"", "")


@design.command
@click.argument("vmnode", nargs=1, type=str)
@click.argument("vmid", nargs=1, type=int)
@click.argument("newid", nargs=1, type=int)
@click.argument("deployname", nargs=1, type=str)
@click.argument("program", nargs=1, type=str)
def testcase_all_snapshot(
    vmnode: str, vmid: int, newid: int, deployname: str, program: str
):
    """
    Test create and finalize of appinstance
    """
    proto = "vnc"
    password = "user1234"
    api.prox_vmstop(vmnode, newid)
    time.sleep(1)
    api.prox_vmdelete(vmnode, newid)
    time.sleep(1)
    api.prox_vmclone(vmnode, vmid, newid, "")
    api.prox_vmconfig_set_post_install(vmnode, newid, f"env-{newid}", "de")
    api.node_vmconfigure_dhcp(newid)
    api.node_vmconfigure_iptables(newid)
    api.prox_vmsnapshot_create(vmnode, newid, "env", "")
    api.prox_vmsnapshot_rollback(vmnode, newid, "env")
    api.node_vmconfigure_dhcp(newid)
    api.node_vmconfigure_iptables(newid)
    api.prox_vmstart(vmnode, newid)
    api.inst_connection_test_ssh(newid, 10000)
    if program == "":
        program = "C:/Program Files/Microsoft Office/root/Office16/Excel.exe"
    api.inst_vminvoke_cmd(newid, f"\\\"{program}\\\"", "")
    time.sleep(1)
    api.prox_vmsnapshot_create(
        vmnode, newid, deployname, f"custom {deployname} description"
    )
    api.prox_vmstop(vmnode, newid)
    api.prox_vmsnapshot_rollback(vmnode, newid, deployname)
    api.node_vmconfigure_dhcp(newid)
    api.node_vmconfigure_iptables(newid)
    api.prox_vmstartvnc(vmnode, newid, password)
    api.gc_conupdate(newid, proto, password, password)
    url = api.gc_conurl(newid, proto)
    print(f"{newid} -> {url}")


if __name__ == "__main__":
    # Pylint doesn't understand click.
    # pylint: disable=unexpected-keyword-arg
    retval = design(standalone_mode=False)
    if retval is not None:
        os._exit(retval)
