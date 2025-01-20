"""
This module defines the HeartbeatSender class, which sends periodic heartbeat signals
to indicate that the client is online.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
import json
import time
import asyncio
import logging
import pika
from typing import Optional

from common.qmsg_model import HeartbeatMessage
from common.qmsg_tools import QMessageTools


@dataclass
class HeartbeatSenderConfig:
    """
    Configuration dataclass for HeartbeatServer.
    Holds the RabbitMQ connection details and operational parameters.
    """

    rabbitmq_host: str = "localhost"
    exchange_name: str = "heartbeat"
    routing_key: str = "instance.heartbeat"
    heartbeat_timeout: int = 1
    reconnect_time: int = 5
    force_name: str = ""
    force_ip: str = ""
    log_topic: str = "HeartbeatServer"


class HeartbeatSender:
    """
    The HeartbeatSender class sends periodic heartbeat messages to a RabbitMQ topic to
    indicate that the client is online.
    """

    def __init__(self, config: HeartbeatSenderConfig) -> None:
        """
        Initialize the HeartbeatSender with the provided RabbitMQ connection details.
        """
        if config is None:
            raise ValueError("Config cannot be None")

        self.config: HeartbeatSenderConfig = config
        self.tools = QMessageTools()
        self.name = self.config.force_name
        if self.name == "":
            self.name = self.tools.get_own_name()
        self.ip_address = self.config.force_ip
        if self.ip_address == "":
            self.ip_address = self.tools.get_own_ip()
        # self.ip_address = "192.168.223.11"
        self.logger = logging.getLogger(self.config.log_topic)
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.task: Optional[asyncio.Task] = None

    def connect(self) -> None:
        """
        Establish a connection to RabbitMQ. If the connection fails, retry after a delay.
        """
        while True:
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
                        self.__log_info(
                            f"Connected to RabbitMQ at {self.config.rabbitmq_host}",
                        )
                        break
            except pika.exceptions.AMQPConnectionError as exe:
                self.__log_error(
                    f"Connection failed, retrying in {self.config.reconnect_time} seconds... Error: {exe}",
                )
                time.sleep(self.config.reconnect_time)

    def send_heartbeat(self) -> None:
        """
        Send a heartbeat message to the RabbitMQ exchange. This method is called periodically.
        """
        while True:
            if self.connection is not None:
                self.connection.close()
            self.connect()
            try:
                if self.channel is not None:
                    message = HeartbeatMessage(
                        datetime.now().timestamp(), self.name, self.ip_address
                    )
                    self.__log_info(f"Send heartbeat: {message}")
                    self.channel.basic_publish(
                        exchange=self.config.exchange_name,
                        routing_key=self.config.routing_key,
                        body=json.dumps(asdict(message)),
                    )
            except pika.exceptions.AMQPConnectionError as exe:
                self.__log_error(
                    f"Failed to send heartbeat, reconnecting... Error: {exe}"
                )
            if self.connection is not None:
                self.connection.close()
                self.connection = None
            time.sleep(self.config.heartbeat_timeout)

    async def start(self) -> None:
        """
        Start the HeartbeatSender as an asynchronous task.
        """
        if self.task is None or self.task.done():
            self.connect()
            self.task = asyncio.create_task(asyncio.to_thread(self.send_heartbeat))
            self.__log_info("HeartbeatSender task started.")

    async def stop(self) -> None:
        """
        Stop the HeartbeatSender and its associated task.
        """
        if self.task is not None:
            self.task.cancel()
            await self.task
            self.__log_info("HeartbeatSender task stopped.")

    def __log_info(self, msg: str):
        # self.logger.info(f"HRT: {msg}")
        pass

    def __log_error(self, msg: str):
        # self.logger.error(f"HRT: {msg}")
        pass
