"""
This module serves as the entry point for running the ClientHub.
It initializes the ClientHub with the necessary configuration and runs it asynchronously.
"""

import os
import asyncio
from .qmsg.hub_instance import QHubInstance, QHubConfigInstance


async def run_client_hub():
    """
    Initialize and run the ClientHub. This function sets up the hub configuration,
    starts the hub, and manages its lifecycle.
    """
    rabbit_ip = "192.168.223.11"
    cfg_hub = QHubConfigInstance(
        rabbitmq_host=rabbit_ip,
        reconnect_time_client=5,
        reconnect_time_server=5,
        # force_name="lalala",
        # force_ip="192.168.223.11",
        log_topic="QHubInstance",
    )
    clienthub = QHubInstance(cfg_hub, setup_logging=True)
    await clienthub.start()
    try:
        await asyncio.sleep(1000)
    except KeyboardInterrupt:
        os._exit(0)

    await clienthub.stop()
    os._exit(0)


if __name__ == "__main__":
    asyncio.run(run_client_hub())
    os._exit(0)
