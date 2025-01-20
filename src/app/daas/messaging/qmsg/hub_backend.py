"""
This module defines the QHubServer class, which manages the HeartbeatServer and RpcClient,
handling their lifecycle, including starting, stopping, and logging.
"""

import threading
from dataclasses import dataclass
import asyncio
import logging
from typing import Optional
from app.daas.messaging.qmsg.receiver.qmsg_heartbeat_receiver import (
    HeartbeatReceiver,
    HeartbeatReceiverConfig,
)
from app.daas.messaging.qmsg.common.qmsg_model import (
    HeartbeatMessage,
    RpcRequest,
    RpcResponse,
)
from app.daas.messaging.qmsg.sender.qmsg_rpc_sender import RpcSender, RpcSenderConfig
from app.daas.messaging.qmsg.common.qmsg_tools import QMessageTools
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class QHubConfigBackend:
    """
    Configuration dataclass for QHubServer.
    Holds the RabbitMQ connection details and operational parameters.
    """

    rabbitmq_host: str = "10.23.42.7"
    host_timeout: int = 5
    cleanup_time: int = 5
    reconnect_time_client: int = 5
    reconnect_time_server: int = 5
    wait_time_ms: int = 100
    wait_time_total_ms: int = 30000
    log_heartbeats: bool = True
    log_topic: str = "daas.adapter.qmsg"


class QHubBackend(Loggable):
    """
    The QHubServer class is responsible for managing the lifecycle of the HeartbeatServer and RpcClient.
    It handles initialization, starting, stopping, and logging for these servers.
    """

    def __init__(self, config: QHubConfigBackend, setup_logging: bool = False) -> None:
        """
        Initialize the QHubServer with the provided configuration.

        :param config: A HeartbeatServerConfig object containing server configuration details.
        """
        Loggable.__init__(self, LogTarget.QMSG)
        self.config_hub = config
        self.cfg_sender = RpcSenderConfig(
            rabbitmq_host=self.config_hub.rabbitmq_host,
            reconnect_time=self.config_hub.reconnect_time_client,
            wait_time_ms=self.config_hub.wait_time_ms,
            wait_time_total_ms=self.config_hub.wait_time_total_ms,
            log_topic=self.config_hub.log_topic,
        )
        self.cfg_receiver = HeartbeatReceiverConfig(
            rabbitmq_host=self.config_hub.rabbitmq_host,
            reconnect_time=self.config_hub.reconnect_time_server,
            cleanup_sleep_time=self.config_hub.cleanup_time,
            host_timeout=self.config_hub.host_timeout,
            log_topic=self.config_hub.log_topic,
        )

        self.tools = QMessageTools()
        self.name = self.tools.get_own_name()
        self.ip_address = self.tools.get_own_ip()
        if setup_logging is True:
            self.logger = self.setup_logger(self.config_hub.log_topic)
        else:
            self.logger = logging.getLogger(self.config_hub.log_topic)
        self.heartbeat_receiver = HeartbeatReceiver(self, self.cfg_receiver)
        self.task_heartbeat_listener: Optional[asyncio.Task] = None
        self.task_heartbeat_cleanup: Optional[asyncio.Task] = None
        self.tasks_rpc: list[tuple] = []

    def create_rpc_task(
        self, topic_name: str, msg: RpcRequest
    ) -> Optional[tuple[threading.Thread, RpcSender]]:
        """get RpcRequest for online client"""
        if self.heartbeat_receiver.is_online(topic_name):
            rpc_client = RpcSender(self.cfg_sender)
            thread = rpc_client.call_rpc_method(topic_name, msg)
            self.tasks_rpc.append((thread, rpc_client))
            return thread, rpc_client
        self._log_info(f"Host is not online: {topic_name}")
        return None

    def call_rpc(self, topic_name: str, msg: RpcRequest) -> Optional[RpcResponse]:
        """get RpcRequest for online client"""
        tasktuple = self.create_rpc_task(topic_name, msg)
        if tasktuple is not None:
            thread, rpc = tasktuple
            if thread is not None and rpc is not None:
                thread.join()
                return rpc.response
        return None

    def handle_heartbeat(self, msg: HeartbeatMessage):
        """called on client heartbeat"""
        if self.config_hub.log_heartbeats:
            self._log_info(f"Handling heartbeat for {msg.ip_address}")

    def handle_client_online(self, client_id: str):
        """called on client heartbeat"""
        self._log_info(f"Client online: {client_id}")

    def handle_client_offline(self, client_id: str):
        """called on client heartbeat"""
        self._log_info(f"Client offline: {client_id}")

    def setup_logger(self, log_topic: str) -> logging.Logger:
        """
        Set up the logger for the application.

        :param log_topic: The logging topic for the logger.
        :return: A configured logging.Logger object.
        """
        logger = logging.getLogger(log_topic)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def start_heartbeat_listener(self) -> None:
        """
        Start the HeartbeatServer listener as an asynchronous task.
        If the listener is already running, this function does nothing.
        """
        if self.task_heartbeat_listener is None or self.task_heartbeat_listener.done():
            await self.heartbeat_receiver.connect()
            self.task_heartbeat_listener = asyncio.create_task(
                self.heartbeat_receiver.start_listening()
            )
            self.task_heartbeat_cleanup = asyncio.create_task(
                self.heartbeat_receiver.start_cleanup_task()
            )
            self._log_info("HeartbeatServer task started.")

    async def start(self) -> None:
        """
        Start the QHubServer, including the HeartbeatServer listener and RpcServer.
        """
        self._log_info("Starting QHubServer")
        await self.start_heartbeat_listener()
        self._log_info("QHubServer started.")

    async def stop(self) -> None:
        """
        Stop the QHubServer and its associated tasks.
        """
        for _, rpc_client in self.tasks_rpc:
            rpc_client.waiting = False

        await self.heartbeat_receiver.disconnect()
        if self.task_heartbeat_cleanup is not None:
            self._log_info("Stopping Cleanup task.")
            self.task_heartbeat_cleanup.cancel()
            # asyncio.gather(self.task_heartbeat_cleanup, return_exceptions=True)
            # await self.task_heartbeat_cleanup
            # self.__log_info("Stopped Cleanup task.")
        if self.task_heartbeat_listener is not None:
            self._log_info("Stopping Listener task.")
            self.task_heartbeat_listener.cancel()
            # asyncio.gather(self.task_heartbeat_listener, return_exceptions=True)
            # await self.task_heartbeat_listener
            # self.__log_info("Stopped Listener task.")
