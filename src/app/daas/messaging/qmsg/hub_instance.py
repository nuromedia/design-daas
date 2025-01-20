"""
This module defines the ClientHub class, which manages the HeartbeatSender and RpcServer,
handling their lifecycle, including starting, stopping, and logging.
"""

import os
from dataclasses import dataclass
from datetime import datetime
import asyncio
import threading
import logging
from typing import Optional
from ProxyControl import ProxyControl
from sender.qmsg_heartbeat_sender import (
    HeartbeatSenderConfig,
    HeartbeatSender,
)
from receiver.qmsg_rpc_receiver import RpcReceiver, RpcReceiverConfig
from common.qmsg_model import RpcRequest, RpcResponse
from common.qmsg_tools import QMessageTools


@dataclass
class QHubConfigInstance:
    """
    Configuration dataclass for QHubClient.
    Holds the RabbitMQ connection details and operational parameters.
    """

    rabbitmq_host: str = "10.23.42.7"
    reconnect_time_client: int = 5
    reconnect_time_server: int = 5
    force_name: str = ""
    force_ip: str = ""
    log_topic: str = "daas.inst"


class QHubInstance:
    """
    The ClientHub class is responsible for managing the lifecycle of the HeartbeatSender and RpcServer.
    It handles initialization, starting, stopping, and logging for these components.
    """

    def __init__(self, config: QHubConfigInstance, setup_logging: bool = False) -> None:
        """
        Initialize the ClientHub with the provided RabbitMQ connection details.
        """
        logging.getLogger("pika").setLevel(logging.ERROR)
        self.config_hub = config
        self.cfg_client = HeartbeatSenderConfig(
            rabbitmq_host=self.config_hub.rabbitmq_host,
            reconnect_time=self.config_hub.reconnect_time_client,
            force_name=self.config_hub.force_name,
            force_ip=self.config_hub.force_ip,
            log_topic=self.config_hub.log_topic,
        )
        self.cfg_server = RpcReceiverConfig(
            rabbitmq_host=self.config_hub.rabbitmq_host,
            reconnect_time=self.config_hub.reconnect_time_server,
            force_name=self.config_hub.force_name,
            force_ip=self.config_hub.force_ip,
            log_topic=self.config_hub.log_topic,
        )
        self.proxy = ProxyControl()
        self.tools = QMessageTools()
        self.name = self.config_hub.force_name
        if self.name == "":
            self.name = self.tools.get_own_name()
        self.ip_address = self.config_hub.force_ip
        if self.ip_address == "":
            self.ip_address = self.tools.get_own_ip()
        if setup_logging is True:
            self.logger = self.setup_logger(self.config_hub.log_topic)
        else:
            self.logger = logging.getLogger(self.config_hub.log_topic)
        self.logger.info(f"Initialized as {self.name} with {self.ip_address}")
        self.heartbeat_sender = HeartbeatSender(self.cfg_client)
        self.rpc_server = RpcReceiver(self, self.cfg_server)
        self.task_heartbeat_sender: Optional[asyncio.Task] = None
        self.task_rpc_server: Optional[threading.Thread] = None

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

        if os.name == "posix":
            file_handler = logging.FileHandler("/root/daas/rpc.log")
        else:
            file_handler = logging.FileHandler("C:/Users/root/daas/rpc.log")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)
        logger.info("Loggerinitialized for %s", log_topic)
        return logger

    def execute_via_proxy(self, request: RpcRequest) -> tuple[int, str, str]:
        """called on rpc request"""
        self.logger.info(
            "Handling RpcRequest: %s %s",
            request.request_cmd,
            request.request_args,
        )
        rtype = request.request_type
        args = request.request_args
        if rtype == "app":
            return self.proxy.execute_app(request.request_cmd, args)
        if rtype == "cmd":
            return self.proxy.execute_cmd(request.request_cmd, args)
        if rtype == "action":
            return self.proxy.execute_action(request.request_cmd, args)
        if rtype == "resolution":
            return self.proxy.execute_resolution(request.request_cmd, args)
        if rtype == "ospackage":
            return self.proxy.execute_ospackage(request.request_cmd, args)
        if rtype == "filesystem":
            return self.proxy.execute_filesystem(request.request_cmd, args)

    def handle_request(self, request: RpcRequest) -> RpcResponse:
        """called on rpc request"""
        self.logger.info(
            "Handling RpcRequest: %s %s",
            request.request_cmd,
            request.request_args,
        )
        code, std_out, std_err = self.execute_via_proxy(request)
        response = RpcResponse(
            datetime.now().timestamp(),
            request,
            self.name,
            self.ip_address,
            {"code": code, "std_out": std_out, "std_err": std_err},
        )
        return response

    async def start_heartbeat_sender(self) -> None:
        """
        Start the HeartbeatSender as an asynchronous task.
        If the sender is already running, this function does nothing.
        """
        if self.task_heartbeat_sender is None or self.task_heartbeat_sender.done():
            await self.heartbeat_sender.start()
            self.task_heartbeat_sender = self.heartbeat_sender.task
            self.logger.info("HeartbeatSender task started.")

    async def start_rpc_server(self) -> None:
        """
        Start the RpcServer as an asynchronous task.
        If the server is already running, this function does nothing.

        :param process_request: A callable function that processes the RPC request.
        """
        if self.task_rpc_server is None:
            self.rpc_server.connect()
            self.task_rpc_server = self.rpc_server.run_in_thread()
            self.logger.info("RpcServer task started.")

    async def start(self) -> None:
        """
        Start the ClientHub, including the HeartbeatSender and RpcServer.
        """
        await self.start_heartbeat_sender()
        await self.start_rpc_server()

    async def stop(self) -> None:
        """
        Stop the ClientHub and its associated tasks.
        """
        if self.task_heartbeat_sender is not None:
            await self.heartbeat_sender.stop()
            self.logger.info("HeartbeatSender task stopped.")

        if self.task_rpc_server is not None:
            self.rpc_server.stop()
            self.logger.info("RpcServer task stopped.")
