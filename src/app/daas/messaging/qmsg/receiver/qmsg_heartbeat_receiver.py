"""
This module defines the HeartbeatServer class, which handles sending and receiving
heartbeat signals to/from RabbitMQ. It also includes the HeartbeatServerConfig dataclass
for server configuration.
"""

import json
import asyncio
import time
from typing import Optional
from dataclasses import dataclass
import pika
from pika.adapters.blocking_connection import BlockingChannel
import pika.exceptions
import pika.channel
import pika.spec
from app.daas.messaging.qmsg.common.qmsg_model import HeartbeatMessage
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class HeartbeatReceiverConfig:
    """
    Configuration dataclass for HeartbeatServer.
    Holds the RabbitMQ connection details and operational parameters.
    """

    rabbitmq_host: str = "localhost"
    exchange_name: str = "heartbeat"
    routing_key: str = "instance.heartbeat"
    cleanup_sleep_time: int = 5
    host_timeout: int = 5
    reconnect_time: int = 5
    log_topic: str = "HeartbeatServer"


class HeartbeatReceiver(Loggable):
    """
    The HeartbeatServer class manages the connection to RabbitMQ and handles the
    sending and receiving of heartbeat signals.
    """

    def __init__(self, owner, config: HeartbeatReceiverConfig) -> None:
        """
        Initialize the HeartbeatServer with the provided configuration.
        """
        Loggable.__init__(self, LogTarget.QMSG)
        if owner is None:
            raise ValueError("Owner cannot be None")

        self.owner = owner
        self.listening = False
        self.reconnecting = True
        self.config: HeartbeatReceiverConfig = config
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None
        self.hosts: dict[str, float] = {}

    async def connect(self) -> None:
        """
        Establish a connection to RabbitMQ. If the connection fails, retry after a delay.
        """
        while self.reconnecting is True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.config.rabbitmq_host)
                )
                if self.connection is not None:
                    self.channel = self.connection.channel()
                    if self.channel is not None:
                        self.channel.exchange_declare(
                            exchange=self.config.exchange_name,
                            exchange_type="topic",
                        )
                        self._log_info(
                            f"Connected to RabbitMQ at {self.config.rabbitmq_host}"
                        )
                        break
            except pika.exceptions.AMQPConnectionError as e:
                self._log_info(
                    (
                        "Connection failed, retrying in "
                        f"{self.config.reconnect_time} seconds... Error: {e}"
                    )
                )
                await asyncio.sleep(self.config.reconnect_time)

    async def disconnect(self) -> None:
        """
        Establish a connection to RabbitMQ. If the connection fails, retry after a delay.
        """
        self.reconnecting = False
        if self.connection:
            try:
                self.connection.close()
            except pika.exceptions.StreamLostError as exe:
                self._log_error(f"StreamLostError: {exe}")
            except pika.exceptions.ChannelWrongStateError as exe:
                self._log_error(f"ChannelError: {exe}")

    def reset_heartbeat(self, ip_addr: str):
        """Resets heartbeat for a given host"""
        if ip_addr in self.hosts:
            del self.hosts[ip_addr]

    def on_heartbeat(
        self,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """
        Handle a received heartbeat message by updating the list of active hosts.
        """
        if channel is not None and method is not None and properties is not None:
            raw_dict = json.loads(body.decode())
            msg = HeartbeatMessage(**raw_dict)
            if msg.ip_address not in self.hosts:
                self.owner.handle_client_online(msg.ip_address)
            self.hosts[msg.ip_address] = time.time()
            self.owner.handle_heartbeat(msg)

    async def start_listening(self) -> None:
        """
        Start listening for heartbeat messages from RabbitMQ.
        """
        if self.channel is not None:
            result = self.channel.queue_declare(queue="", exclusive=True)
            queue_name = result.method.queue
            self.channel.queue_bind(
                exchange=self.config.exchange_name,
                queue=queue_name,
                routing_key=self.config.routing_key,
            )
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.on_heartbeat,
                auto_ack=True,
            )
            self._log_info("Waiting for heartbeat messages...")
            self.listening = True
            loop = asyncio.get_event_loop()
            try:
                task = loop.run_in_executor(None, self.channel.start_consuming)
                await task
            except asyncio.CancelledError:
                self._log_info("HeartbeatReceiver-listener cancelled")

    async def start_cleanup_task(self) -> None:
        """
        Start a periodic task to clean up inactive hosts.
        """
        try:
            while self.reconnecting:
                await asyncio.sleep(0)
                current_time = time.time()
                inactive_hosts = [
                    host
                    for host, last_seen in self.hosts.items()
                    if current_time - last_seen > self.config.host_timeout
                ]
                for host in inactive_hosts:
                    self._log_info(f"Removing inactive host: {host}")
                    del self.hosts[host]
                    self.owner.handle_client_offline(host)
                await asyncio.sleep(self.config.cleanup_sleep_time)
        except asyncio.CancelledError:
            self._log_info("HeartbeatReceiver-cleanup cancelled")

    def is_online(self, ip_address: str) -> bool:
        """Checks if host is online"""

        current_time = time.time()
        if ip_address in self.hosts:
            last_seen = self.hosts[ip_address]
            diff = current_time - last_seen
            if diff < self.config.host_timeout:
                return True

        return False

    async def get_available_hosts(self) -> list:
        """
        Get a list of currently active hosts.

        :return: A list of active host IDs.
        """
        return list(self.hosts.keys())
