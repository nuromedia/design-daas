"""Proxy Tasks"""

from dataclasses import asdict, dataclass
from datetime import timedelta
from enum import Enum
from typing import Optional
from quart import render_template, websocket
from app.daas.common.ctx import (
    create_response_url_start,
    get_request_object,
    get_request_object_optional,
)
from app.daas.common.enums import BackendName
from app.daas.objects.object_instance import InstanceObject
from app.daas.objects.object_container import ContainerObject
from app.daas.objects.object_machine import MachineObject
from app.daas.proxy.guacamole_proxy import (
    ResizeHandler,
    proxy_guacamole_ws,
)
from app.daas.proxy.jinja_params import (
    get_jinja_params_instance,
    get_jinja_params_viewer,
)
from app.daas.proxy.proxy_registry import ProxyRegistry
from app.daas.storage.filestore import Filestore
from app.qweb.common.common import TaskArgs
from app.qweb.common.qweb_tools import get_backend_component, get_database
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.processing.processor import QwebResult


class ProxyTask(Enum):
    """Proxy processor tasktype"""

    VIEWER_TEMPLATE = "VIEWER_TEMPLATE"
    VIEWER_CHECK = "VIEWER_CHECK"
    VIEWER_INFO = "VIEWER_INFO"
    VIEWER_PROXY_WS = "VIEWER_PROXY_WS"
    VIEWER_CONNECT = "VIEWER_CONNECT"
    VIEWER_DISCONNECT = "VIEWER_DISCONNECT"


@dataclass
class ViewerCheckInfo:
    """Info object for check_instance"""

    available: bool
    connection: bool
    booted: bool

    def tojson(self) -> dict:
        """Convert to json"""
        return asdict(self)


async def viewer_template(args: TaskArgs) -> str:
    """Get viewer template"""
    from app.daas.db.database import Database

    dbase = await get_database(Database)
    req = args.req.request_context.request_quart
    assert req is not None
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    assert entity is not None and entity.id_con is not None
    con = await dbase.get_guacamole_connection(entity.id_con)
    assert con is not None
    params_viewer = await get_jinja_params_viewer()
    params_inst = await get_jinja_params_instance(
        entity, con.viewer_token, req.referrer
    )
    return await render_template(
        "layout-viewer.html",
        params_host=params_inst.backend_url,
        params_inst=params_inst,
        params_viewer=params_viewer,
    )


async def viewer_connect(args: TaskArgs) -> QwebResult:
    inst = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    if isinstance(inst.app, MachineObject | ContainerObject):
        await inst.app.set_contype(reqargs["contype"])
        if await inst.connect(inst.app.viewer_contype) is not None:
            if inst is not None:
                return await create_response_url_start(True, inst.id)
            return QwebResult(400, {}, 1, "No instance")
        return QwebResult(400, {}, 2, "Not connected")
    return QwebResult(400, {}, 3, "Invalid object type")


async def viewer_disconnect(args: TaskArgs) -> QwebResult:
    inst = get_request_object(args.ctx, "entity", InstanceObject)
    if isinstance(inst.app, MachineObject | ContainerObject):
        if await inst.disconnect(True):
            return QwebResult(200, {}, response_url="-")
        return QwebResult(400, {}, 1, "Not disconnected")
    return QwebResult(400, {}, 2, "Invalid object type")


async def viewer_check(args: TaskArgs) -> dict:
    """Check viewer connection"""
    from app.daas.db.database import Database

    dbase = await get_database(Database)
    entity = get_request_object_optional(args.ctx, "entity", InstanceObject)
    if entity is not None and entity.id_con is not None:
        con = await dbase.get_guacamole_connection(entity.id_con)
        flag_available = True
        flag_booted = False
        flag_connection = False
        if con is not None:
            flag_connection = True
        if entity.booted_at > entity.created_at:
            flag_booted = True
        flag_booted = True
        info = ViewerCheckInfo(flag_available, flag_connection, flag_booted)
        return info.tojson()
    return ViewerCheckInfo(False, False, False).tojson()


async def viewer_info(args: TaskArgs) -> QwebResult:
    """Return viewer info for connection"""
    from app.daas.db.database import Database

    dbase = await get_database(Database)
    reqargs = args.req.request_context.request_args
    entity = get_request_object_optional(args.ctx, "entity", InstanceObject)
    if entity is not None and entity.id_con is not None:
        conn = await dbase.get_guacamole_connection(entity.id_con)
        reg = await get_backend_component(BackendName.PROXY, ProxyRegistry)
        store = await get_backend_component(BackendName.FILE, Filestore)

        reqargs["id"] = reqargs["id_instance"]

        stats_raw = reg.get_stats_instance(reqargs["id_instance"])
        if stats_raw is None:
            stats = {}
        else:
            stats = stats_raw.tojson()

        instance = await dbase.get_instance_by_id(reqargs["id_instance"])
        if instance is None:
            return QwebResult(400, {}, 1, "No instance")

        env = None
        appname = "none"
        envname = "none"
        if instance.env is not None:
            env = await dbase.get_environment_by_name(
                instance.app.id, instance.env.name
            )
        if env is not None and env.env_target != "" and "cmd" in env.env_target:
            envname = env.name
            appname = env.env_target["cmd"]

        if instance.id_con is not None and isinstance(
            instance.app, (ContainerObject, MachineObject)
        ):
            conn = await dbase.get_guacamole_connection(instance.id_con)
            if conn is None:
                msg = f"Connection not found={instance.id_con}"
                # __log_error(msg, 404)
                return QwebResult(404, {}, 3, msg)
            if conn.viewer_token != reqargs["token"]:
                msg = f"Token invalid={reqargs['token']}"
                # __log_error(msg, 403)
                return QwebResult(403, {}, 3, msg)
            pstools = instance.app.is_windows()

            if "resolutions" in reqargs and reqargs["resolutions"] is not None:
                cmp = instance.created_at
                if instance.app.is_windows:
                    cmp = instance.created_at + timedelta(seconds=60)
                if instance.booted_at > cmp:
                    adr = instance.host
                    ret = await instance.inst_vminvoke_resolution("list", "")
                    if ret.response_code != 200:
                        msg = f"Requesting resolutions failed for {adr}"
                        return QwebResult(
                            200,
                            {
                                "obj": instance.app.id,
                                "env": envname,
                                "app": appname,
                                "mode": instance.app.object_mode,
                                "stats": stats,
                                "mode_extended": instance.app.object_mode_extended,
                                "resolutions": "[]",
                            },
                        )
                    _, rout, _ = await store.read_inst_file_status(
                        instance.host, pstools, instance.app.os_username
                    )
                    return QwebResult(
                        200,
                        {
                            "obj": instance.app.id,
                            "env": envname,
                            "app": appname,
                            "mode": instance.app.object_mode,
                            "stats": stats,
                            "mode_extended": instance.app.object_mode_extended,
                            "resolutions": rout,
                        },
                    )
            return QwebResult(
                200,
                {
                    "obj": instance.app.id,
                    "env": envname,
                    "app": appname,
                    "mode": instance.app.object_mode,
                    "stats": stats,
                    "mode_extended": instance.app.object_mode_extended,
                    "resolutions": "[]",
                },
            )
    return QwebResult(404, {}, 4, "Unknown error")


class ProxmoxVncHandler(ResizeHandler, Loggable):
    """Resizehandler for Proxmox-VNC"""

    def __init__(self, instance: InstanceObject, adr: str, pstools: bool):
        Loggable.__init__(self, LogTarget.INST)
        self.instance = instance
        self.adr = adr
        self.pstools = pstools

    async def on_resize(self, *, width: float, height: float) -> None:
        """Resizehandler invoke instance cmd to resize internally as well"""
        res = f"{int(width)}x{int(height)}"
        self._log_info(f"ON_RESIZE: {res} -> '{self.instance.app.viewer_resize}'")
        if self.instance.app.viewer_resize in ("browser"):
            await self.instance.inst_vminvoke_resolution("set", res)
        else:
            self._log_info(f"Handler ommitted for {self.adr} ({res})", -1)


async def proxy_ws(args: TaskArgs):

    from app.daas.db.database import Database

    dbase = await get_database(Database)
    reqargs = args.req.request_context.request_args
    instance = get_request_object(args.ctx, "entity", InstanceObject)

    # api = await ctx.get_design_api()
    # if __check_token(token):
    #     __remove_token(token)
    # else:
    #     __print_info(f"WEBSOCKET OTP: Invalid Token: {token} {viewer_tokens}")
    #     return "Invalid viewer token", 403

    # __log_info(f"WebSocket request for {websocket.url}")
    # instance = await dbase.get_instance_by_id(id)
    # if instance is None:
    #     return "not found", 404
    # if await verify_entity_ownership(instance) is False:
    #     return respond_error(request, str({"id": id}), 403, "Invalid owner")
    if (
        instance is not None
        and instance.id_con is not None
        and isinstance(instance.app, (ContainerObject, MachineObject))
    ):
        connection_guac = await dbase.get_guacamole_connection(instance.id_con)
        if connection_guac is None:
            # __log_error(f"No Connection for instance={instance.id}", 404)
            return "not found", 404
        if reqargs["token"] != connection_guac.viewer_token:
            return "Invalid viewer token", 403

        pstools = False
        if isinstance(instance.app, MachineObject):
            if instance.app.os_type in ("win10", "win11"):
                pstools = True

        # maybe confirm a subprotocol
        subprotocol = None
        if "guacamole" in websocket.requested_subprotocols:
            subprotocol = "guacamole"
        await websocket.accept(subprotocol=subprotocol)

        # Forward to proxy
        resize_handler = ProxmoxVncHandler(
            instance,
            instance.host,
            pstools,
        )
        # reconnect_handler = ProxmoxReconnectHandler(
        #     api, logging.getLogger("daas.proxy")
        # )
        return await proxy_guacamole_ws(
            instance,
            websocket,
            connection_guac,
            resize_handler=resize_handler,
            # reconnect_handler=None,
        )

    raise TypeError(f"no HTTP proxy support for {type(instance.app)=}")
