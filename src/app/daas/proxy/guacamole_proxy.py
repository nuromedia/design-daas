"""A proxy for the Guacamole protocol."""

from __future__ import annotations

import asyncio
from datetime import datetime
import subprocess
from dataclasses import dataclass
from datetime import timedelta
import functools
from typing import Optional, Protocol, TypeAlias
from collections.abc import Awaitable, Callable
from quart import Websocket
from websockets import WebSocketClientProtocol
from app.daas.common.enums import BackendName
from app.daas.common.model import GuacamoleConnection, Instance
from app.daas.proxy.streams import (
    GuacamoleSocketStream,
    GuacamoleSocketWs,
    GuacamoleSocket,
)
from app.daas.proxy.handshake import (
    ClientConfiguration,
    perform_guacd_handshake,
)
from app.qweb.common.qweb_tools import get_backend_component, get_database
from app.qweb.logging.logging import LogTarget, Loggable


socket_tuples: dict[str, SocketTuple] = {}
logger = Loggable(LogTarget.PROXY)
GUACAMOLE_ENCODING = "utf-8"
TIMEOUT_DELAY = 1.2
COLLECT_STATS = True
OPCODE_INTERNAL = ""
"""
Used by the Guacamole JavaScript client.

When sent by the client:

- ping request

When sent by the server:

- 1st message with connection ID
- ping response
"""


class ResizeHandler(Protocol):
    """A ResizeHandler may be invoked when the client sends a `size` message."""

    async def on_resize(self, *, width: float, height: float) -> None:
        """
        Adjust screen size to the client's width x height preferences.

        This method should return quickly, possibly before the resize is complete.
        """


class ReconnectHandler(Protocol):
    """A ReconnectHandler may be invoked when the client loses connection"""

    async def on_reconnect(self, *, id_instance: str, token: str) -> None:
        """
        Renables token
        """


class WebsocketStats:
    """Counts socket stats"""

    def __init__(self):
        self.opcodes_per_second = 0
        self.bytes_per_second = 0
        self.blobbytes_per_second = 0
        self.blobs_per_second = 0
        self.total_opcodes = 0
        self.total_bytes = 0
        self.total_blobs = 0
        self.size_blobs = 0
        self.total_opcodes_client = 0
        self.total_opcodes_guacd = 0
        self.total_bytes_client = 0
        self.total_bytes_guacd = 0
        self.counter_client: dict[str, int] = {}
        self.counter_guacd: dict[str, int] = {}
        self.created_at = datetime.now().timestamp()
        self.difftime: float = 0

    def add(self, other):
        self.opcodes_per_second += other.opcodes_per_second
        self.total_opcodes += other.total_opcodes
        self.total_bytes += other.total_bytes
        self.total_opcodes_client += other.total_opcodes_client
        self.total_opcodes_guacd += other.total_opcodes_guacd
        self.total_blobs += other.total_blobs
        self.size_blobs += other.size_blobs
        self.total_bytes_client += other.total_bytes_client
        self.total_bytes_guacd += other.total_bytes_guacd
        self.created_at = min(self.created_at, other.created_at)
        self.difftime = datetime.now().timestamp() - self.created_at

        for key, val in other.counter_client.items():
            if key not in self.counter_client:
                self.counter_client[key] = val
            else:
                self.counter_client[key] += val
        for key, val in other.counter_guacd.items():
            if key not in self.counter_guacd:
                self.counter_guacd[key] = val
            else:
                self.counter_guacd[key] += val
        if self.difftime >= 1:
            self.blobs_per_second = self.total_blobs / self.difftime
            self.opcodes_per_second = self.total_opcodes / self.difftime
            self.bytes_per_second = self.total_bytes / self.difftime
            self.blobbytes_per_second = self.size_blobs / self.difftime

    def add_opcode_guacd_to_client(self, opcode: str, args):
        """Appends opcode from guacd to client"""
        # print(f"G2C: {opcode} {len(args)}")
        size_bytes = 0
        for arg in args:
            size_bytes += len(arg)
        self.total_opcodes += 1
        self.total_opcodes_guacd += 1
        self.total_bytes += size_bytes
        self.total_bytes_guacd += size_bytes
        if opcode == "blob":
            pass
        if opcode not in self.counter_guacd:
            self.counter_guacd[opcode] = 1
        else:
            self.counter_guacd[opcode] += 1
        tsnow = datetime.now().timestamp()
        self.difftime = tsnow - self.created_at
        self.opcodes_per_second = self.total_opcodes / self.difftime
        self.bytes_per_second = self.total_bytes / self.difftime
        self.blobs_per_second = self.total_blobs / self.difftime
        self.blobbytes_per_second = self.size_blobs / self.difftime

    def add_opcode_client_to_guacd(self, opcode: str, args):
        """Appends opcode from client to guacd"""
        # print(f"C2G: {opcode} {len(args)}")
        size_bytes = 0
        for arg in args:
            size_bytes += len(arg)
        self.total_opcodes += 1
        self.total_opcodes_client += 1
        self.total_bytes += size_bytes
        self.total_bytes_client += size_bytes
        self.total_blobs += 1
        self.size_blobs += size_bytes
        if opcode != "blob":
            self.total_bytes += size_bytes
        self.total_bytes_client += size_bytes

        if opcode not in self.counter_client:
            self.counter_client[opcode] = 1
        else:
            self.counter_client[opcode] += 1
        tsnow = datetime.now().timestamp()
        self.difftime = tsnow - self.created_at
        self.opcodes_per_second = self.total_opcodes / self.difftime
        self.bytes_per_second = self.total_bytes / self.difftime
        self.blobs_per_second = self.total_blobs / self.difftime
        self.blobbytes_per_second = self.size_blobs / self.difftime

    def tostring(self) -> str:
        """Returns shorthand string"""
        return (
            f"{self.difftime:4.1f}s,"
            f"{self.total_opcodes:6} "
            f"({self.opcodes_per_second:5.1f} ops),"
            f"{self.total_blobs:6} "
            f"({self.blobs_per_second:5.1f} bps),"
            f"{self.total_bytes/1024/1024:6.1f} MB "
            f"({self.bytes_per_second/1024 /1024:4.1f}MB/s),"
        )

    def tojson(self) -> dict:
        """Returns shorthand string"""
        return {
            "opcodes_per_second": self.opcodes_per_second,
            "bytes_per_second": self.bytes_per_second,
            "blobbytes_per_second": self.blobbytes_per_second,
            "blobs_per_second": self.blobs_per_second,
            "total_opcodes": self.total_opcodes,
            "total_bytes": self.total_bytes,
            "total_blobs": self.total_blobs,
            "size_blobs": self.size_blobs,
            "total_opcodes_client": self.total_opcodes_client,
            "total_opcodes_guacd": self.total_opcodes_guacd,
            "total_bytes_client": self.total_bytes_client,
            "total_bytes_guacd": self.total_bytes_guacd,
            "counter_client": self.counter_client,
            "counter_guacd": self.counter_guacd,
            "created_at": self.created_at,
            "difftime": self.difftime,
        }


@dataclass
class SocketTuple:
    """
    Describes proxy tuple for a connection
    """

    id: str
    id_instance: str
    id_owner: int
    server_socket: GuacamoleSocketStream | WebSocketClientProtocol | subprocess.Popen
    client_socket: GuacamoleSocketWs | Websocket
    connection: GuacamoleConnection
    last_seen_guacd: datetime
    last_seen_client: datetime
    stats: WebsocketStats

    def tojson(self):
        """Converts object to json"""
        return {
            "id": self.id,
            "id_instance": self.id_instance,
            "last_seen_guacd": self.last_seen_guacd,
            "last_seen_client": self.last_seen_client,
            "stats": self.stats.tojson(),
        }


async def new_guacd_connection() -> GuacamoleSocketStream:
    """Create a new connection to guacd."""
    from app.daas.proxy.proxy_registry import ProxyRegistry

    reg = await get_backend_component(BackendName.PROXY, ProxyRegistry)
    connstring = reg.config.guacd
    host, port = connstring.split(":")  # no IPv6 support, lol
    guacd_reader, guacd_writer = await asyncio.open_connection(host, port)
    # print(f"NEW GUACD Socket: {connstring}")
    return GuacamoleSocketStream(reader=guacd_reader, writer=guacd_writer)


async def proxy_guacamole_ws(
    instance: Instance,
    client_ws: Websocket,
    connection: GuacamoleConnection,
    *,
    resize_handler: Optional[ResizeHandler],
    # reconnect_handler: Optional[ReconnectHandler],
):
    """Create a Guacamole tunnel from the client WebSocket to guacd."""
    from app.daas.proxy.proxy_registry import ProxyRegistry
    from app.daas.db.database import Database

    reg = await get_backend_component(BackendName.PROXY, ProxyRegistry)

    client_conf = ClientConfiguration.from_params(client_ws.args)
    # __log_info(f" PROXY:   0 -> Connecting instance {client_conf} with client conf")
    client_socket = GuacamoleSocketWs(client_ws)
    guacd_socket: GuacamoleSocketStream = await new_guacd_connection()
    # __log_info(f" PROXY:   0 -> Create guacd-socket: {guacd_socket}")

    connid = await perform_guacd_handshake(
        instance=instance,
        socket=guacd_socket,
        connection=connection,
        client_conf=client_conf,
        log=logger,
    )

    if not connid:
        return "connection failed", 500

    _log_info(f" PROXY:   0 -> Adding {connid}")
    info = SocketTuple(
        connid,
        instance.id,
        instance.app.id_owner,
        guacd_socket,
        client_socket,
        connection,
        datetime.now(),
        datetime.now(),
        WebsocketStats(),
    )
    reg.add_connection(info)
    socket_tuples[connid] = info

    # handshake with the client
    await client_socket.send(OPCODE_INTERNAL, connid)
    # __log_info(f" PROXY:   0 -> Create client-socket: {client_socket}")

    async def forward_client_to_guacd() -> None:
        """Handle messages from the client."""

        # select potential message handlers
        middlewares = [
            _handle_errors(client_socket=client_socket),
            _handle_ping(client_socket=client_socket),
            _handle_ignore_internal,
        ]

        if resize_handler:
            middlewares.append(_handle_size_message(resize_handler=resize_handler))

        handle_message = _assemble_middlewares(
            *middlewares,
            default=_forward_message(socket=guacd_socket),
        )

        while True:
            try:
                this_tuple = socket_tuples[connid]
                diff = abs(datetime.now() - this_tuple.last_seen_guacd)
                if diff > timedelta(seconds=TIMEOUT_DELAY):
                    _log_info(f"GUAC DIFF EXCEEDED: {diff}")
                    # raise asyncio.CancelledError()  # must re-raise
                opcode, *args = await client_socket.receive()
                await handle_message(opcode, tuple(args))
                if COLLECT_STATS is True:
                    info.stats.add_opcode_guacd_to_client(opcode, args)
                this_tuple.last_seen_client = datetime.now()
                if opcode == "error":
                    _log_info(f"Error raised on guacd loop -> {opcode} {args}")
            except asyncio.CancelledError:
                _log_info("Cancelled error on client_socket")
                await guacd_socket.send("disconnect", "Error received", "599")
                await guacd_socket.send("error", "Error received", "599")
                task_guacd.cancel("client has disconnected")
                task_client.cancel("client has disconnected")
                reg.disconnect_connection(connid)
                # if connid in socket_tuples:
                #     __log_info(f"Removing {connid}")
                #     socket_tuples.pop(connid)
                raise asyncio.CancelledError()  # must re-raise

    async def forward_guacd_to_client():
        """
        Handle messages from the server.

        In principle they could be forwarded without any parsing,
        but the client might expect to always receive full messages.
        This is in line with the Guacamole Java proxy.
        """
        while True:
            try:
                this_tuple = socket_tuples[connid]
                diff = abs(datetime.now() - this_tuple.last_seen_guacd)
                if diff > timedelta(seconds=TIMEOUT_DELAY):
                    _log_info(f"GUAC DIFF EXCEEDED: {diff}")
                    # raise asyncio.CancelledError()  # must re-raise
                opcode, *args = await guacd_socket.receive()
                if COLLECT_STATS is True:
                    info.stats.add_opcode_client_to_guacd(opcode, args)
                await client_socket.send(opcode, *args)
                this_tuple.last_seen_guacd = datetime.now()
                if opcode == "error":
                    _log_info(f"Error raised on guacd loop -> {opcode} {args}")

            except (asyncio.CancelledError, ValueError):
                _log_info("Cancelled error on guacd_socket")
                await client_socket.send("disconnect", "Error received", "599")
                await client_socket.send("error", "Error received", "599")
                task_guacd.cancel("server has disconnected")
                task_client.cancel("server has disconnected")
                reg.disconnect_connection(connid)
                # if connid in socket_tuples:
                #     __log_info(f"Removing {connid}")
                #     socket_tuples.pop(connid)
                #     reg.disconnect_connection(connid)
                # path_arr = (await client_socket.get_path()).split("/")
                # if reconnect_handler is not None and len(path_arr) == 4:
                #     await reconnect_handler.on_reconnect(
                #         id_instance=path_arr[2], token=path_arr[3]
                #     )
                # return
                # __log_info(f" PROXY: Exception on receive : {exc}")
                raise asyncio.CancelledError()  # must re-raise

            # forward messages to client

    if isinstance(guacd_socket, GuacamoleSocketStream):
        # global socket_tuples
        # global sockets_guacd

        dbase = await get_database(Database)

        task_client = asyncio.create_task(forward_client_to_guacd())
        task_guacd = asyncio.create_task(forward_guacd_to_client())
        # __log_queuesinfo(f" PROXY:  0 -> Create Tasks: {task_client} {task_guacd}")
        _log_info(f"Length sockelist: {len(socket_tuples)}")
        _log_info(f" PROXY:   0 -> Completed Guacamole connection connid={connid}")
        newinstance = await dbase.get_instance_by_id(instance.id)
        if newinstance is not None:
            newinstance.connected_at = datetime.now()
            await dbase.update_instance(newinstance)
        await asyncio.gather(task_client, task_guacd)


MessageHandler: TypeAlias = Callable[[str, tuple[str, ...]], Awaitable[None]]

Middleware: TypeAlias = Callable[
    [MessageHandler, str, tuple[str, ...]], Awaitable[None]
]


async def _assert_must_have_handler(opcode: str, args: tuple[str, ...]) -> None:
    raise AssertionError(f"message must be handled, but got: {opcode} {args}")


def _assemble_middlewares(
    *middlewares: Middleware,
    default: MessageHandler = _assert_must_have_handler,
) -> MessageHandler:
    """
    Chain multiple middlewares into a single message handler.

    Middlewares are invoked in order.
    Each middleware must either handle the message itself and return,
    or invoke the `next` MessageHandler.
    """

    combined: MessageHandler = default

    for middleware in reversed(middlewares):
        combined = functools.partial(middleware, combined)

    return combined


def _handle_errors(*, client_socket: GuacamoleSocket) -> Middleware:
    """If any later middlewares raise errors, log them and notify client."""

    async def inner_handler_catch_errors(
        next_handler: MessageHandler, opcode: str, args: tuple[str, ...]
    ) -> None:
        try:
            return await next_handler(opcode, args)
        except Exception:  # pylint: disable=broad-exception-caught
            _log_error(f" PROXY:  -1 -> Exception while handling {opcode} message")
        # guacamole status 512 = "server error"
        await client_socket.send("error", "could not handle message", "512")

    return inner_handler_catch_errors


def _handle_ping(*, client_socket: GuacamoleSocket) -> Middleware:
    async def inner_handler_ping(
        next_handler: MessageHandler, opcode: str, args: tuple[str, ...]
    ) -> None:
        """Respond to ping messages."""
        if opcode == OPCODE_INTERNAL and args and args[0] == "ping":
            return await client_socket.send(OPCODE_INTERNAL, *args)

        return await next_handler(opcode, args)

    return inner_handler_ping


async def _handle_ignore_internal(
    next_handler: MessageHandler, opcode: str, args: tuple[str, ...]
) -> None:
    """Ignore internal messages."""
    if opcode == OPCODE_INTERNAL:
        return

    return await next_handler(opcode, args)


def _handle_size_message(*, resize_handler: ResizeHandler) -> Middleware:
    """Parse `size` messages and pass them to the `resize_handler`."""

    async def inner_handle_size_message(
        next_handler: MessageHandler, opcode: str, args: tuple[str, ...]
    ) -> None:
        if opcode != "size":
            return await next_handler(opcode, args)

        width, height = args

        return await resize_handler.on_resize(
            width=float(width),
            height=float(height),
        )

    return inner_handle_size_message


def _forward_message(*, socket: GuacamoleSocket) -> MessageHandler:
    async def inner_forward_message(opcode: str, args: tuple[str, ...]) -> None:
        # try:
        return await socket.send(opcode, *args)
        # except Exception:
        #     pass

    return inner_forward_message


def _log_info(msg: str) -> None:
    logger._log_info(msg)


def _log_error(msg: str) -> None:
    logger._log_error(msg)
