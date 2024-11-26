import logging
import asyncio

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_2
from amqtt.session import ApplicationMessage
from readings import NFCReading, User,Quest

# from pipeline import PipeLine, Payload

class Subscriber:

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._queue = queue
        self._publish_topic = ""
        self._broker_address = ""
        with open('config.txt', 'r') as file:
            lines = file.readlines()  # Returns a list where each element is a line
            self._broker_address = lines[0].strip()
            self._publish_topic = lines[1].strip()



    async def process_input_string(self, input_string: str):
        lines = input_string.splitlines()

        for line in lines:
            line = line.strip()  # Remove leading/trailing spaces
            if line.startswith("QUEST"):
                quest = Quest(quest_id=line[5:])  # Extract everything after "QUEST"
            elif line.startswith("USER"):
                user = User(user_id=line[4:])  # Extract everything after "USER"
                nfc_reading = NFCReading(quest=quest, user=user)
                await (self._queue).put(nfc_reading)

    async def mqtt_connect_and_subscribe(self):
        # Create an MQTT client instance
        client = MQTTClient()

        # Set up the callback for incoming messages
        client.on_message = lambda client, topic, payload, qos, properties: asyncio.create_task(
            self.process_input_string(payload.decode())
        )

        # Connect to the broker (replace with your broker's address and port)
        await client.connect(self._broker_address)

        # Subscribe to a topic (replace 'test/topic' with your topic)
        await client.subscribe(self._publish_topic, qos=QOS_2)

        print("Subscribed to topic 'test/topic'")

        # Run the client to start listening for incoming messages
        await client.loop_forever()