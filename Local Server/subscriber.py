import logging
import asyncio

from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_2
from amqtt.session import ApplicationMessage

from pipeline import Payload, PipeLine

logger = logging.getLogger(__name__)


class Subscriber:

    def __init__(self, publish_topic, broker_ip_address, pipeline: PipeLine):
        self._pipeline = pipeline
        self._publish_topic = publish_topic
        self._broker_address = f"mqtt://{broker_ip_address}"

    async def process_input_string(self, input_string: str):
        lines = input_string.splitlines()
        quest_id = "NONE"
        for line in lines:
            line = line.strip()  # Remove leading/trailing spaces
            if line.startswith("QUEST"):
                quest_id = line[5:]  # Extract everything after "QUEST"
            elif line.startswith("USER"):
                user_id = line[4:]  # Extract everything after "USER"
                payload = Payload(quest_id, user_id)
                await self._pipeline.add_reading(payload)

    async def mqtt_connect_and_subscribe(self):
        # Create an MQTT client instance
        client = MQTTClient()

        # Connect to the broker (replace with your broker's address and port)
        await client.connect(self._broker_address)
        logger.info(f"Connected to {self._broker_address}")

        # Subscribe to a topic (replace 'test/topic' with your topic)
        await client.subscribe([(self._publish_topic, QOS_2)])
        logger.debug(f"Subscribed to topic {self._publish_topic}")

        # Start listening for incoming messages
        while True:
            # TODO Add error handling
            message: ApplicationMessage = await client.deliver_message()

            payload = str(message.publish_packet.payload.data, 'utf-8')
            _ = asyncio.create_task(self.process_input_string(payload))
