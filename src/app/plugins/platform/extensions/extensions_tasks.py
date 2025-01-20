"""Extension Tasks"""

import websockets
from enum import Enum
from quart import websocket
from app.daas.common.enums import BackendName
from app.daas.proxy.proxy_extensions import ProxyExtensions
from app.qweb.common.common import TaskArgs
from app.qweb.common.qweb_tools import get_backend_component, get_database
from app.qweb.processing.processor import QwebResult


class ExtensionsTask(Enum):
    """Extensions processor tasktype"""

    EXTENSIONS_WSS_PRINTER = "EXTENSIONS_WSS_PRINTER"
    EXTENSIONS_WSS_AUDIO = "EXTENSIONS_WSS_AUDIO"


async def printer_ws(args: TaskArgs):
    """Forward all printer traffic to docker service"""
    from app.daas.db.database import Database

    dbase = await get_database(Database)
    extensions = await get_backend_component(BackendName.EXTENSIONS, ProxyExtensions)
    reqargs = args.req.request_context.request_args
    token = reqargs["token"]
    con = await dbase.get_guacamole_connection_by_token(token)
    if con is None:
        return QwebResult(400, {}, 1, "No connection")
    inst = await dbase.get_instance_by_conid(con.id)
    if inst is None:
        return QwebResult(400, {}, 2, "No instance")

    userid = int(inst.app.id_owner)
    added = await extensions.add_printer_service(inst, userid)
    if added:
        url_printer = await extensions.get_url_service_printer()
        url_query = (
            f"{url_printer}?"
            f"token={token}&"
            f"id={extensions.config.prefix_printer_user}{inst.app.id_owner}"
        )
        async with websockets.connect(url_query) as service_ws:
            client_ws = websocket
            await extensions.proxy_printer_sockets(
                f"printer_ws_{inst.id}", inst, con, client_ws, service_ws
            )
            return QwebResult(200, {}, 0, "Connection closed")
    return QwebResult(400, {}, 3, "Printer not added")


async def audio_ws(args: TaskArgs):
    """Forward all audio traffic to docker service"""
    from app.daas.db.database import Database

    dbase = await get_database(Database)
    extensions = await get_backend_component(BackendName.EXTENSIONS, ProxyExtensions)
    reqargs = args.req.request_context.request_args
    token = reqargs["token"]

    con = await dbase.get_guacamole_connection_by_token(token)
    if con is None:
        return QwebResult(400, {}, 1, "No connection")
    inst = await dbase.get_instance_by_conid(con.id)
    if inst is None:
        return QwebResult(400, {}, 2, "No instance")

    client_ws = websocket
    await client_ws.accept()
    audio_proc = await extensions.create_audio_socket(inst)
    await extensions.proxy_audio_socket(
        f"audio_ws_{inst.id}", inst, con, client_ws, audio_proc
    )
    return QwebResult(200, {}, 0, "Connection closed")
