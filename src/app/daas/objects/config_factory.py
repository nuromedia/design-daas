"""
Helepr component to do tedious object initialization
"""

import secrets
from app.daas.common.ctx import remove_args
from app.daas.common.enums import BackendName
from app.daas.common.model import GuacamoleConnection
from app.daas.proxy.proxy_registry import ProxyRegistry
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.qweb.common.qweb_tools import get_backend_component, get_database

DEFAULT_INSTANCE_RESOLUTION = "1280x800"


async def create_args_config(id_proxmox: int, **kwargs) -> dict:
    api = await get_backend_component(BackendName.VM, ApiProxmox)
    args = kwargs
    args["vmnode"] = api.config_prox.node
    args["vmid"] = id_proxmox
    return args


async def create_args_pre_install(id_proxmox: int, args: dict) -> dict:
    api = await get_backend_component(BackendName.VM, ApiProxmox)
    args["vmnode"] = api.config_prox.node
    args["vmid"] = id_proxmox
    args["ostype"] = args["os_type"]
    args["ceph_pool"] = False
    if "ceph_pool" in args:
        args["ceph_pool"] = True
    return await remove_args(args, ["id", "os_type", "timestamp", "counter"])


async def create_args_post_install(id_proxmox: int, args: dict) -> dict:
    api = await get_backend_component(BackendName.VM, ApiProxmox)
    args["vmnode"] = api.config_prox.node
    args["vmid"] = id_proxmox
    return await remove_args(args, ["id", "timestamp", "counter"])


async def get_empty_connection(**kwargs) -> GuacamoleConnection:
    """
    Creates a new GuacamoleConnection by given parameters
    """
    connection_args = await __get_empty_connection_dict(**kwargs)
    return GuacamoleConnection(**connection_args)


async def get_empty_object_dict(
    object_type: str,
    userid: int,
    *,
    cores: str,
    memsize: str,
    disksize: str,
    id: str = "",
    ceph_public: str = "",
    ceph_shared: str = "",
    ceph_user: str = "",
    object_mode: str = "",
    viewer_contype: str = "sysvnc",
    viewer_resolution: str = DEFAULT_INSTANCE_RESOLUTION,
    viewer_resize: str = "none",
    viewer_scale: str = "none",
    **kwargs,
) -> dict:
    """Creates empty base object"""

    if object_type == "vm":
        if viewer_contype not in ("sysvnc", "instvnc", "rdp"):
            viewer_contype = "sysvnc"
    if object_type == "container":
        if viewer_contype not in ("instvnc",):
            viewer_contype = "instvnc"

    if viewer_scale not in ("none", "up", "down", "both"):
        viewer_scale = "none"

    if viewer_resize not in ("none", "browser"):
        viewer_resize = "none"

    if viewer_resolution is None or viewer_resolution == "":
        viewer_resolution = DEFAULT_INSTANCE_RESOLUTION

    if object_mode == "":
        object_mode = "untouched"

    arguments: dict = {
        "id": id,
        "id_user": "",
        "id_owner": userid,
        "id_proxmox": -1,
        "id_docker": "",
        "object_storage": "daas-img",
        "object_type": object_type,
        "object_mode": object_mode,
        "object_mode_extended": "none",
        "object_state": "baseimage-create",
        "object_tasks": [],
        "object_apps": [],
        "object_target": {},
        "ceph_public": (ceph_public == "on"),
        "ceph_shared": (ceph_shared == "on"),
        "ceph_user": (ceph_user == "on"),
        "viewer_contype": viewer_contype,
        "viewer_resolution": viewer_resolution,
        "viewer_resize": viewer_resize,
        "viewer_scale": viewer_scale,
        "os_wine": False,
        "os_type": "none",
        "os_username": "root",
        "os_password": "root",
        "os_installer": "",
        "hw_cpus": int(cores),
        "hw_memory": int(memsize),  # * 1024**2,
        "hw_disksize": int(disksize),  # * 1024**3,
        "vnc_port_system": -1,
        "vnc_port_instance": 5900,
        "vnc_username": "user1234",
        "vnc_password": "user1234",
        "extra_args": "",
    }
    return arguments


async def __get_empty_connection_dict(
    id_instance: str,
    contype: str,
    hostname: str,
) -> dict:
    from app.daas.db.database import Database

    proxy = await get_backend_component(BackendName.PROXY, ProxyRegistry)
    dbase = await get_database(Database)
    instance = await dbase.get_instance_by_id(id_instance)
    if instance is None:
        return {}

    # Choose params
    user = ""
    password = ""
    port = -1
    adr = ""
    instance_ip = hostname
    protocol = "vnc"
    if contype == "sysvnc":
        vmapi = await get_backend_component(BackendName.VM, ApiProxmox)
        user = instance.app.vnc_username
        password = instance.app.vnc_password
        protocol = "vnc"
        port = instance.app.vnc_port_system
        adr = f"{vmapi.config_prox.hostIp}"
    elif contype == "rdp":
        user = instance.app.os_username
        password = instance.app.os_password
        protocol = "rdp"
        port = 3389
        adr = instance_ip
    elif contype == "instvnc":
        user = instance.app.vnc_username
        password = instance.app.vnc_password
        protocol = "vnc"
        port = instance.app.vnc_port_instance
        adr = instance_ip

    # Create dict
    randid = secrets.token_urlsafe(16)
    token_con = secrets.token_urlsafe(proxy.config.token_length)
    url = await generate_connection_url(id_instance)
    arguments = {
        "id": randid,
        "user": user,
        "password": password,
        "protocol": protocol,
        "hostname": adr,
        "port": port,
        "viewer_url": url,
        "viewer_token": token_con,
    }
    return arguments


async def generate_connection_url(id_instance: str):
    """Generates Endpoint URL for viewer clients"""

    proxy = await get_backend_component(BackendName.PROXY, ProxyRegistry)
    full_url = (
        f"{proxy.config.viewer_protocol}://"
        + f"{proxy.config.viewer_host}:{proxy.config.viewer_port}"
        + f"/viewer/template/{id_instance}"
    )
    return full_url


#
#
# async def create_object_dict_from_app(app: Application) -> dict:
#     # Create args
#     args = {}
#     args["ceph_pool"] = ""
#     args["ceph_public"] = ""
#     args["ceph_shared"] = ""
#     args["ceph_user"] = ""
#     args["keyboard_layout"] = "de"
#     args["viewer_resolution"] = "1280x800"
#     args["viewer_resize"] = "both"
#     args["viewer_scale"] = "both"
#     args["viewer_contype"] = "sysvnc"
#     args["os_type"] = app.os_type
#     return args
#
#
# async def get_empty_object_dict(
#     object_type: str,
#     cores: str,
#     memsize: str,
#     disksize: str,
#     *,
#     id: str = "",
#     ceph_public: str = "",
#     ceph_shared: str = "",
#     ceph_user: str = "",
#     object_mode: str = "",
#     viewer_contype: str = "sysvnc",
#     viewer_resolution: str = DEFAULT_INSTANCE_RESOLUTION,
#     viewer_resize: str = "none",
#     viewer_scale: str = "none",
# ) -> dict:
#     """Creates empty base object"""
#
#     ctx = get_context()
#     userid = await get_userid(ctx)
#
#     # default_cpus = 4
#     # default_mem = 4 * 1024**3
#     # default_size = 8 * 1024**3
#     if object_type == "vm":
#         # default_size = 64 * 1024**3
#         if viewer_contype not in ("sysvnc", "instvnc", "rdp"):
#             viewer_contype = "sysvnc"
#     if object_type == "container":
#         # default_cpus = 2
#         # default_mem = 2 * 1024**3
#         if viewer_contype not in ("instvnc",):
#             viewer_contype = "instvnc"
#     if viewer_scale not in ("none", "up", "down", "both"):
#         viewer_scale = "none"
#     if viewer_resize not in ("none", "browser"):
#         viewer_resize = "none"
#     if viewer_resolution is None or viewer_resolution == "":
#         viewer_resolution = DEFAULT_INSTANCE_RESOLUTION
#     if object_mode == "":
#         object_mode = "untouched"
#
#     arguments: dict = {
#         "id": id,
#         "id_user": "",
#         "id_owner": userid,
#         "id_proxmox": -1,
#         "id_docker": "",
#         "object_storage": "daas-img",
#         "object_type": object_type,
#         "object_mode": object_mode,
#         "object_mode_extended": "none",
#         "object_state": "baseimage-create",
#         "object_tasks": [],
#         "object_apps": [],
#         "object_target": {},
#         "ceph_public": (ceph_public == "on"),
#         "ceph_shared": (ceph_shared == "on"),
#         "ceph_user": (ceph_user == "on"),
#         "viewer_contype": viewer_contype,
#         "viewer_resolution": viewer_resolution,
#         "viewer_resize": viewer_resize,
#         "viewer_scale": viewer_scale,
#         "os_wine": False,
#         "os_type": "none",
#         "os_username": "root",
#         "os_password": "root",
#         "os_installer": "",
#         "hw_cpus": int(cores),
#         "hw_memory": int(memsize) * 1024**2,
#         "hw_disksize": int(disksize) * 1024**3,
#         "vnc_port_system": -1,
#         "vnc_port_instance": 5900,
#         "vnc_username": "user1234",
#         "vnc_password": "user1234",
#         "extra_args": "",
#     }
#     return arguments
#
#
# async def generate_connection_url(id_instance: str):
#     """Generates Endpoint URL for viewer clients"""
#
#     ctx = get_context()
#     cfg = ctx.config
#     full_url = (
#         f"{cfg.viewer.viewer_protocol}://"
#         + f"{cfg.viewer.viewer_host}:{cfg.viewer.viewer_port}"
#         + f"/viewer/{id_instance}"
#     )
#     return full_url
#
#
# async def get_empty_connection(**kwargs) -> GuacamoleConnection:
#     """
#     Creates a new GuacamoleConnection by given parameters
#     """
#     connection_args = await __get_empty_connection_dict(**kwargs)
#     return GuacamoleConnection(**connection_args)
#
#
# async def __get_empty_connection_dict(
#     id_instance: str,
#     contype: str,
#     hostname: str,
# ) -> dict:
#
#     # Prepare
#     ctx = get_context()
#     api = await ctx.get_design_api()
#     dbase = await ctx.get_database()
#     cfg = api.config
#     instance = await dbase.get_instance_by_id(id_instance)
#     if instance is None:
#         return {}
#
#     # Choose params
#     user = ""
#     password = ""
#     port = -1
#     adr = ""
#     instance_ip = hostname
#     protocol = "vnc"
#     if contype == "sysvnc":
#         user = instance.app.vnc_username
#         password = instance.app.vnc_password
#         protocol = "vnc"
#         port = instance.app.vnc_port_system
#         adr = f"{cfg.prox_api.hostIp}"
#     elif contype == "rdp":
#         user = instance.app.os_username
#         password = instance.app.os_password
#         protocol = "rdp"
#         port = 3389
#         adr = instance_ip
#     elif contype == "instvnc":
#         user = instance.app.vnc_username
#         password = instance.app.vnc_password
#         protocol = "vnc"
#         port = instance.app.vnc_port_instance
#         adr = instance_ip
#
#     # Create dict
#     ctx = get_context()
#     randid = secrets.token_urlsafe(16)
#     token_con = secrets.token_urlsafe(ctx.config.viewer.token_length)
#     url = await generate_connection_url(instance.id)
#     arguments = {
#         "id": randid,
#         "user": user,
#         "password": password,
#         "protocol": protocol,
#         "hostname": adr,
#         "port": port,
#         "viewer_url": url,
#         "viewer_token": token_con,
#     }
#     return arguments
