from datetime import datetime
import os
import asyncio
from qmsg.hub_backend import QHubBackend, QHubConfigBackend
from qmsg.common.qmsg_model import RpcRequest


async def run_qhub_server():
    """
    Initialize and run the QHubServer. This function sets up the server configuration,
    starts the server, and periodically logs the available hosts.
    """
    receiver_ip = "192.168.223.116"
    sender_ip = "192.168.223.112"
    sender_name = "sendloop"
    rabbit_ip = "172.17.0.1"  # "192.168.223.112"
    test_cmd = "calc.exe"
    test_args = [""]
    config_hub = QHubConfigBackend(
        rabbitmq_host=rabbit_ip,
        cleanup_time=5,
        host_timeout=5,
        reconnect_time_client=5,
        reconnect_time_server=5,
        log_topic="daas.proxy",
    )
    qhub_server = QHubBackend(config_hub, setup_logging=True)

    # Start the QHubServer components
    await qhub_server.start()
    try:
        while True:
            await asyncio.sleep(5)
            qhub_server.create_rpc_task(
                receiver_ip,
                RpcRequest(
                    datetime.now().timestamp(),
                    sender_name,
                    sender_ip,
                    "cmd",
                    test_cmd,
                    test_args,
                ),
            )
    except KeyboardInterrupt:
        os._exit(0)
    await qhub_server.stop()
    os._exit(0)


if __name__ == "__main__":
    asyncio.run(run_qhub_server())
