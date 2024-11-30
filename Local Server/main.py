import logging
import asyncio
import socket

from amqtt.broker import Broker

from pipeline import PipeLine
from subscriber import Subscriber
from points_logic import process_logic_forever
from api_processor import api_forwarding_forever


# Prepare the logger
logger = logging.getLogger(__name__)

# Load config file
with open("config.txt", "r") as file:
    TOPIC = file.readline()

# MQTT Port
PORT = 1883

# Get ip address of device
HOST_NAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOST_NAME)


# Main starting point
async def main():
    # Create Pipeline Stack
    pipeline = PipeLine()

    # Create Subscriber
    logger.info(f"Creating subscriber to topic {TOPIC}")
    subscriber = Subscriber(TOPIC, IP_ADDRESS, pipeline)

    # Start listening and responding forever while forwarding to api after processing it:
    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(subscriber.mqtt_connect_and_subscribe())
        task_group.create_task(process_logic_forever(pipeline))
        task_group.create_task(api_forwarding_forever(pipeline))


if __name__ == '__main__':
    # Start logger
    formatter = "[%(asctime)s] %(name)s %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)

    # Configure amqtt logger
    amqtt_logger = logging.getLogger("amqtt")
    # amqtt_logger.setLevel(logging.WARNING)

    # Configure transitions.core logger
    transitions_core_logger = logging.getLogger("transitions.core")
    transitions_core_logger.setLevel(logging.WARNING)

    # Run main
    asyncio.run(main())
