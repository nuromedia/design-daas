"""Adapters for Guacamole protocol streams over various transports."""

import asyncio
import abc

# import time

from quart import Websocket

from .syntax import (
    IncrementalGuacamoleParser,
    IncrementalBinaryGuacamoleParser,
    format_message_b,
    format_message,
)


class GuacamoleSocket(abc.ABC):
    """A GuacamoleSocket can send() and receive() Guacamole messages."""

    async def get_path(self) -> str:
        """Retrieves path from the utilized websocket"""
        raise NotImplementedError()

    async def receive(self) -> tuple[str, ...]:
        """Receive the next Guacamole message over the socket."""
        raise NotImplementedError()

    async def send(self, opcode: str, *args: str):
        """Immediately send a Guacamole message over the socket."""
        raise NotImplementedError()


class GuacamoleSocketWs(GuacamoleSocket):
    """GuacamoleSocket adapter for quart.Websocket."""

    def __init__(self, websocket: Websocket) -> None:
        self.__ws = websocket
        self.__parser = IncrementalGuacamoleParser()

    async def get_path(self) -> str:
        return self.__ws.path

    async def receive(self) -> tuple[str, ...]:
        while True:
            if message := self.__parser.next_message():
                return message

            # may throw exception if connection is severed
            # t = time.time()
            # print(f"IN: {t}")
            raw: bytes | str = await self.__ws.receive()
            # print(f"GSWS: RECEIVE: {raw}")

            # The client should always send strings,
            # but handle bytes just in case.
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")

            if isinstance(raw, str):
                self.__parser.feed(raw)
            else:
                print("RECEIVED MALFORMED PACKET")

    async def send(self, opcode: str, *args: str) -> None:
        await self.__ws.send(format_message(opcode, *args))


class GuacamoleSocketStream(GuacamoleSocket):
    """GuacamoleSocket implementation for asyncio streams."""

    def __init__(
        self,
        *,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self.__reader = reader
        self.__writer = writer
        self.__parser = IncrementalBinaryGuacamoleParser()

    async def receive(self) -> tuple[str, ...]:
        running = 2
        while running > 0:
            if message := self.__parser.next_message():
                # print(f"Received message: {message}")
                return message

            # read any immediately available chunk of UP TO 1024 bytes
            raw = await self.__reader.read(1024)
            if not raw:
                running -= 1
            else:
                self.__parser.feed(raw)
        return ()

    async def send(self, opcode: str, *args: str) -> None:
        self.__writer.write(format_message_b(opcode, *args))
        await self.__writer.drain()  # proper backpressure
