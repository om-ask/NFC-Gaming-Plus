import asyncio
import logging

from amqtt.client import MQTTClient, ConnectException
from readings import NFCReading
from amqtt.mqtt.constants import QOS_2

logger = logging.getLogger(__name__)


class Publisher:
    """
    An asynchronous class to forward any readings in the provided queue to a configured broker.

    The Publisher class takes an asynchronous queue that gets populated by NFCReading objects, publishing the readings
    to a mqtt broker.
    """
    CONFIG_FILE = "config.txt"
    PAYLOAD_FILE = "payload.txt"

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._queue = queue
        self._publish_topic = ""
        self._broker_address = ""
        self._OldPayload = ""

        with open(Publisher.PAYLOAD_FILE, "r") as file:
            self._OldPayload = file.read()

        with open(Publisher.CONFIG_FILE, 'r') as file:
            lines = file.readlines()  # Returns a list where each element is a line
            self._broker_address = lines[0].strip()
            self._publish_topic = lines[1].strip()
            logger.debug(f"Broker IP {self._broker_address}, and Topic {self._publish_topic}")

    async def publish(self, readings: list[NFCReading]) -> bool:
        """
        Publish the given readings to the broker address

        The sample format of the payload to be sent and received by the broker (tentative):
        QUESTg107af419hb41414
        USER14f8971da4984B5
        USER1414fa1441d555
        USER148arf9714faf9845
        QUESTg152181hkdf9814
        USER14f8971drFrt3145
        USER1414BdD2145e14
        USER148arf9714faf9845

        ... and so on

        :param readings: The readings to publish to the broker
        :return: True if successful
        """
        current_quest = ""
        payload = self._OldPayload

        for s in readings:
            if s.quest_id != current_quest:
                current_quest = s.quest_id
                payload += s.quest_string() + "\n"
            payload += s.user_string() + "\n"
        logger.debug(payload)
        battah = await self.publish_with_qos_2(self._broker_address, self._publish_topic, payload)
        return battah

    async def publish_forever(self) -> None:
        """
        Loops forever waiting for readings and publishing to the mqtt broker
        :return: None
        """
        while True:
            readings = []
            await asyncio.sleep(8)
            if self._queue.empty():
                logger.debug("No readings to publish")
                continue
            while not self._queue.empty():
                readings.append(await self._queue.get())
            await self.publish(readings)

    async def publish_with_qos_2(self, broker_url, topic, payload):
        mqtt_config = {
            "keep_alive": 20,
            "ping_delay": 1,
            "reconnect_retries": 5,
            "reconnect_max_interval": 3,
        }

        client = None

        try:
            # Initialize MQTTClient
            client = MQTTClient()

            # Connect to the broker
            await client.connect(broker_url)
            logger.debug(f"Connected to broker: {broker_url}")

            # Validate and encode the payload
            if not payload or not isinstance(payload, str):
                raise ValueError("Payload must be a non-empty string.")
            encoded_payload = payload.encode()

            # Publish the message
            await client.publish(topic, encoded_payload, qos=QOS_2)
            # f"Message published to topic"
            logger.info(f"Message published to topic {topic}")
            logger.debug(f"{encoded_payload} sent to {topic}")
            self._OldPayload = ""
            with open(Publisher.PAYLOAD_FILE, "w") as file:
                # Write the desired string to the file
                file.write("")
            return True

        except ConnectException as e:
            logger.error(f"Error connecting to Broker {e}")
            self._OldPayload = payload
            with open(Publisher.PAYLOAD_FILE, "w") as file:
                # Write the desired string to the file
                file.write(payload)
            return False

        except AttributeError as e:
            logger.error(f"Error {e}")
            self._OldPayload = payload
            with open("Payload.txt", "w") as file:
                # Write the desired string to the file
                file.write(payload)
            return False

        except Exception as e:
            logger.error(f"Error {e}")
            self._OldPayload = payload
            with open(Publisher.PAYLOAD_FILE, "w") as file:
                # Write the desired string to the file
                file.write(payload)
            return False

        finally:
            if client is not None:
                try:
                    await client.disconnect()
                    logger.debug(f"Disconnected From Broker")
                except Exception as e:
                    logger.error(f"Error during disconnection: {e}")
            else:
                logger.warning("Client was not initialized properly.")
