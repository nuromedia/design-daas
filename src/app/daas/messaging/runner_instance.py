"""
This module serves as the entry point for running the ClientHub.
It initializes the ClientHub with the necessary configuration and runs it asynchronously.
"""


async def run_client_hub():
    """
    Initialize and run the ClientHub. This function sets up the hub configuration,
    starts the hub, and manages its lifecycle.
    """
    rabbit_ip = "172.17.0.1"
    cfg_hub = QHubConfigInstance(
        rabbitmq_host=rabbit_ip,
        reconnect_time_client=5,
        reconnect_time_server=5,
        # force_name="ForcedName",
        # force_ip="192.168.223.112",
        log_topic="daas.inst",
    )
    clienthub = QHubInstance(cfg_hub, setup_logging=True)
    await clienthub.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        os._exit(0)

    await clienthub.stop()
    os._exit(0)


if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "env")))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "qmsg")))
    print(sys.path)
    import asyncio
    from hub_instance import QHubInstance, QHubConfigInstance

    asyncio.run(run_client_hub())
    os._exit(0)
