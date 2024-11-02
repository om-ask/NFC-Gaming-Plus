import asyncio
import logging

from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_1

from reading_task import NFCReading

SERVER_ADDRESS = "mqtt://192.168.1.2:1883"
TOPIC = "nfc/read"

logger = logging.getLogger(__name__)


async def publish_forever(readings_queue: asyncio.Queue):
    while True:
        reading: NFCReading = await readings_queue.get()
        logger.info("Received reading on publish queue", NFCReading)

        # Connect to mqtt broker
        client = MQTTClient()

        # Connect to the MQTT broker using the specified IP address and port.
        await client.connect(SERVER_ADDRESS)

        # Publish message
        await client.publish(TOPIC, bytes(reading.generate_payload()), qos=QOS_1)

        # Disconnect from the MQTT broker.
        await client.disconnect()
