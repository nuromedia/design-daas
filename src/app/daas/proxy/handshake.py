"""Implementation of the Guacamole handshake."""

from __future__ import annotations

from typing import Optional
from dataclasses import dataclass
from werkzeug.datastructures import MultiDict
from app.qweb.logging.logging import Loggable
from ..common.model import GuacamoleConnection, Instance
from .streams import GuacamoleSocket


@dataclass
class ClientConfiguration:
    """
    Configuration options set by the JS client.

    These options are transmitted as query parameters
    to the WebSocket upgrade request.
    """

    width: int
    height: int
    dpi: int
    colors: int
    keyboard: str
    audio_mimetypes: list[str]
    video_mimetypes: list[str]
    image_mimetypes: list[str]
    audio_input: str
    printing: str
    printer_name: str
    timezone: str
    autoretry: int
    force_lossless: str
    resize_method: str
    initial_program: str

    @classmethod
    def from_params(
        cls,
        params: MultiDict,
    ) -> ClientConfiguration:
        """
        Parse query parameters from the websocket request.

        This follows the parameter list in the Java source code
        in the [`TunnelRequest`](https://github.com/apache/guacamole-client/blob/940c7ad37aefc06cb42c764a1deb6abab86f8290/guacamole/src/main/java/org/apache/guacamole/tunnel/TunnelRequest.java#L32-L100)
        and in the JavaScript [`ManagedClient`](https://github.com/apache/guacamole-client/blob/940c7ad37aefc06cb42c764a1deb6abab86f8290/guacamole/src/main/frontend/src/app/client/types/ManagedClient.js#L276-L322).
        """
        return cls(
            width=params.get("GUAC_WIDTH", 1024, type=int),
            height=params.get("GUAC_HEIGHT", 768, type=int),
            dpi=params.get("GUAC_DPI", 96, type=int),
            colors=params.get("GUAC_COLORDEPTH", 32, type=int),
            keyboard=params.get("GUAC_KEYBOARD", "de-de-qwertz", type=str),
            audio_mimetypes=params.getlist("GUAC_AUDIO"),
            video_mimetypes=params.getlist("GUAC_VIDEO"),
            image_mimetypes=params.getlist("GUAC_IMAGE"),
            audio_input=params.get("GUAC_AUDIO_INPUT", "false"),
            printing=params.get("GUAC_ENABLE_PRINTING", "false"),
            printer_name=params.get("GUAC_PRINTER_NAME", "DESIGN-PRINTER"),
            timezone=params.get("GUAC_TIMEZONE", "UTC"),
            force_lossless=params.get("GUAC_LOSSLESS", "false", type=str),
            autoretry=params.get("GUAC_AUTORETRY", 1, type=int),
            resize_method=params.get("GUAC_RESIZEMETHOD", "reconnect", type=str),
            initial_program=params.get("GUAC_INITIAL_PROGRAM", "", type=str),
        )


async def perform_guacd_handshake(
    *,
    instance: Instance,
    socket: GuacamoleSocket,
    connection: GuacamoleConnection,
    client_conf: ClientConfiguration,
    log: Loggable,
) -> Optional[str]:
    """
    Perform the full handshake protocol.

    Upon success, returns the guacd connection ID.
    """
    # The server will select which of these args are needed.
    # The full list of available arguments is not documented,
    # but can be inferred from the Guacamole source code.
    #
    # For VNC connections:
    # https://github.com/apache/guacamole-server/blob/83ca7aa16b49830b5adb5a0ce60082b385163934/src/protocols/vnc/settings.c#L35-L97
    #
    # For RDP connections:
    # https://github.com/apache/guacamole-server/blob/1e9777abdaecd74551453cce0a6861a824d7267a/src/protocols/rdp/settings.c#L53-L147
    #
    # Similarly for Kubernetes, Telnet, SSH connections.
    #
    # Right now, only VNC is being tested.
    # Relevant arguments for RDP and so on will have to be added later.
    #
    # If an unknown argument is requested by the server, that isn't an error.
    # Instead, an empty string is written.
    available_args: dict[str, str] = {
        "hostname": connection.hostname,
        "port": str(connection.port),
        "username": connection.user,
        "password": connection.password,
        "ignore-cert": "true",
        "dpi": str(client_conf.dpi),
        "server-layout": client_conf.keyboard,
        "autoretry": str(client_conf.autoretry),
        "color-depth": str(client_conf.colors),
        "force-lossless": client_conf.force_lossless,
        "resize-method": client_conf.resize_method,
        "initial-program": client_conf.initial_program,
        "client-name": "daas-instance",
        "enable-audio": "true",
        "audio-servername": instance.host,
        "enable-audio-input": client_conf.audio_input,
        "enable-drive": "true",
        "create-drive-path": "true",
        "enable-printing": client_conf.printing,
        "printer-name": client_conf.printer_name,
    }

    await socket.send("select", connection.protocol)

    while True:
        match await socket.receive():
            case ["args", handshake_version, *handshake_args]:
                protocol_features = _check_protocol_version(
                    handshake_version,
                    log=log,
                )
                break
            case other:
                log._log_info("expected `args` message from server but got: {other}")

    # need the handshake negotiation feature
    if not protocol_features.supports_handshake_negotiation:
        log._log_error(f"guacd protocol version is too old: {handshake_version}")
        return None

    # send required arguments
    await socket.send(
        "size",
        str(client_conf.width),
        str(client_conf.height),
        str(client_conf.dpi),
    )
    await socket.send("audio", *client_conf.audio_mimetypes)
    await socket.send("video", *client_conf.video_mimetypes)
    await socket.send("image", *client_conf.image_mimetypes)
    await socket.send("timezone", client_conf.timezone)
    # await socket.send("dpi", str(client_conf.dpi))
    # await socket.send("color-depth", str(client_conf.colors))
    # await socket.send("server-layout", client_conf.keyboard)
    # await socket.send("autoretry", str(client_conf.autoretry))
    # await socket.send("force-lossless", str(client_conf.force_lossless))
    # await socket.send("resize-method", client_conf.resize_method)
    # await socket.send("initial-program", client_conf.initial_program)
    # user name, relevant for connection sharing scenarios.
    # Not going to do that in the demo, so just hardcode anything.
    if protocol_features.supports_name:
        await socket.send("name", "DESIGN-DaaS")

    # perform the connection.
    await socket.send(
        "connect",
        "VERSION_1_1_0",  # appear as v1.1.0 so that no "required" instructions happen
        *(available_args.get(arg, "") for arg in handshake_args),
    )

    # at this point, the server should respond with a "ready" instruction.
    match await socket.receive():
        case ["ready", connid]:
            log._log_info(f"Handshake successful {connid}")
            return connid
        case other:
            log._log_error(f"expected `ready` message from server but got: {other}")
            return None


@dataclass
class _GuacamoleProtocolFeatures:
    supports_name: bool = False
    supports_handshake_negotiation: bool = False
    supports_required: bool = False


def _check_protocol_version(
    handshake_version: str,
    *,
    log: Loggable,
) -> _GuacamoleProtocolFeatures:
    match handshake_version:
        case "VERSION_1_0_0":
            return _GuacamoleProtocolFeatures()
        case "VERSION_1_1_0":
            return _GuacamoleProtocolFeatures(supports_handshake_negotiation=True)
        case "VERSION_1_3_0":
            return _GuacamoleProtocolFeatures(
                supports_required=True,
                supports_handshake_negotiation=True,
            )
        case "VERSION_1_5_0":
            return _GuacamoleProtocolFeatures(
                supports_name=True,
                supports_required=True,
                supports_handshake_negotiation=True,
            )
        case other:
            log._log_info(
                f"guacd uses unsupported protocol version {other}, continuing as if 1.5.0",
            )
            return _GuacamoleProtocolFeatures(
                supports_name=True,
                supports_required=True,
                supports_handshake_negotiation=True,
            )
