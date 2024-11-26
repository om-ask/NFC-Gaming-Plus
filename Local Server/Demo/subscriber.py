import logging
import asyncio

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_2
from amqtt.session import ApplicationMessage
from readings import NFCReading, User,Quest

from pipeline import PipeLine, Payload

# Prepare the logger
logger = logging.getLogger(__name__)

async def process_input_string(input_string: str, queue: asyncio.Queue):
    lines = input_string.splitlines()

    for line in lines:
        line = line.strip()  # Remove leading/trailing spaces
        if line.startswith("QUEST"):
            quest = Quest(quest_id=line[5:])  # Extract everything after "QUEST"
        elif line.startswith("USER"):
            user = User(user_id=line[4:])  # Extract everything after "USER"
            nfc_reading = NFCReading(quest=quest, user=user)
            await queue.put(nfc_reading)

async def subscribe_and_listen_forever(pipeline: PipeLine):
    client = MQTTClient()

    await client.connect('mqtt://192.168.1.2:1883')
    await client.subscribe([
        ('nfc/read', QOS_2)])

    # Run forever
    try:
        while True:
            # Wait for the next message
            message: ApplicationMessage = await client.deliver_message()

            # Extract message payload
            packet = message.publish_packet
            print("MESSAGE RECEIVED", str(packet.payload.data, 'utf-8'))

            message_payload = str(packet.payload.data, 'utf-8').splitlines()

            # FORMAT OF MESSAGE PAYLOAD
            # FIRST LINE READER ID
            # SECOND LINE USER ID
            reader_id = message_payload[0]
            user_id = message_payload[1]

            # Format message payload to formal payload
            formal_payload = Payload(reader_id, user_id)

            # Add new payload to the pipeline
            await pipeline.add_reading(formal_payload)

    except ClientException as ce:
        logger.error("Client exception: %s" % ce)

    finally:
        # Unsubscribe and disconnect
        await client.unsubscribe(['nfc/read'])
        await client.disconnect()
