import logging
import socket
import yaml
import asyncio
from amqtt.broker import Broker

from pipeline import PipeLine
from subscriber import subscribe_and_listen_forever
from points_logic import process_logic_forever
from api_posting import api_forwarding_forever

# Prepare the logger
logger = logging.getLogger(__name__)

# Load the broker server config
with open("broker_config.yaml", "r") as config_file:
    broker_config = yaml.safe_load(config_file)


# Main starting point
async def main():
    # Create and start broker server
    server = Broker(broker_config)
    await server.start()

    # Create Pipeline Stack
    pipeline = PipeLine()

    # Start listening and responding forever while forwarding to api after processing it:
    async with asyncio.TaskGroup() as task_group:
        subscriber_task = task_group.create_task(subscribe_and_listen_forever(pipeline))
        processing_task = task_group.create_task(process_logic_forever(pipeline))
        # api_forwarding_task = task_group.create_task(api_forwarding_forever(pipeline))


if __name__ == '__main__':
    # Start logger
    logging.basicConfig(level=logging.INFO)

    # Print ip
    # print("Opening broker at", socket.getaddrinfo(socket.gethostname()))

    # Run main
    asyncio.run(main())
