"""Definitions for qmsg data exchange"""

from dataclasses import dataclass


@dataclass
class HeartbeatMessage:
    """Model for rpc messages"""

    timestamp: float
    name: str
    ip_address: str


@dataclass
class RpcRequest:
    """Model for rpc messages"""

    timestamp: float
    sender_name: str
    sender_ip: str
    request_type: str
    request_cmd: str
    request_args: list


@dataclass
class RpcResponse:
    """Model for rpc messages"""

    timestamp: float
    request: RpcRequest
    processor_name: str
    processor_ip: str
    processor_result: dict
