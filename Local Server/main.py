import logging
import asyncio
import socket

from amqtt.broker import Broker

from pipeline import PipeLine
from subscriber import Subscriber

# Prepare the logger TODO remove redundant loggers
logger = logging.getLogger(__name__)

# Load config file
with open("config.txt", "r") as file:
    TOPIC = file.readline()

# MQTT Port
PORT = 1883

# Get ip address of device
HOST_NAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOST_NAME)

# Configurations
BROKER_CONFIG = {
    "listeners": {
        "default": {
            "max-connections": 100,
            "type": "tcp"
        },
        "tcp1": {
            "bind": f"{IP_ADDRESS}:{PORT}"
        }
    },
    "auth": {
        "allow-anonymous": True  # TODO Authentication?
    },
    "topic-check": {
        "enabled": True,
        "acl": {
            "nfc-reader": [TOPIC],
            "anonymous": [TOPIC]
        }
    }
}


# Main starting point
async def main():
    # Create and start broker server
    server = Broker(BROKER_CONFIG)
    logger.info(f"Starting broker. IP address is : {IP_ADDRESS}:{PORT}")
    await server.start()

    # Create Pipeline Stack
    pipeline = PipeLine()

    # Create Subscriber
    logger.info(f"Creating subscriber to topic {TOPIC}")
    subscriber = Subscriber(TOPIC, IP_ADDRESS, pipeline)

    # Start listening and responding forever while forwarding to api after processing it:
    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(subscriber.mqtt_connect_and_subscribe())
        # processing_task = task_group.create_task(process_logic_forever(pipeline))
        # api_forwarding_task = task_group.create_task(api_forwarding_forever(pipeline))


if __name__ == '__main__':
    # Start logger
    logging.basicConfig(level=logging.INFO)

    # Run main
    asyncio.run(main())
