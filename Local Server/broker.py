import logging
import asyncio
import socket

from amqtt.broker import Broker

from pipeline import PipeLine
from subscriber import Subscriber
from points_logic import process_logic_forever

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
    while True:
        await asyncio.sleep(0)
   
    # Start listening and responding forever while forwarding to api after processing it:
    # async with asyncio.TaskGroup() as task_group:
    #     # task_group.create_task(subscriber.mqtt_connect_and_subscribe())
    #     processing_task = task_group.create_task(process_logic_forever(pipeline))
    #     # api_forwarding_task = task_group.create_task(api_forwarding_forever(pipeline))


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
