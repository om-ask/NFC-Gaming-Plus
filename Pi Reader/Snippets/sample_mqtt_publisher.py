import logging
import asyncio

from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

# Create a logger object for logging messages.
logger = logging.getLogger(__name__)  # Corrected __name_


async def test_coro():
    # Create an instance of the MQTT client.
    C = MQTTClient()

    # Connect to the MQTT broker using the specified IP address and port.
    await C.connect('mqtt://test.mosquitto.org:1883')
    print("Connected", flush=True)

    # Wait for all publish tasks to complete.
    await C.publish('nfc/read', b'QUESTplace3\nUSERomar-ask@outlook.com', qos=QOS_2)
    print("Messages published", flush=True)

    # Log a message indicating that the messages have been published.
    logger.info("messages published")

    # Disconnect from the MQTT broker.
    await C.disconnect()


# Main entry point of the script.
if __name__ == '__main__':  # Corrected __name_
    # Set up logging configuration.
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)

    # Run the test_coro function until complete.
    asyncio.get_event_loop().run_until_complete(test_coro())
