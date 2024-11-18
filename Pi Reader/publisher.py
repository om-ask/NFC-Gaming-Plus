import asyncio

from amqtt.client import MQTTClient, ConnectException
from readings import NFCReading
from amqtt.mqtt.constants import QOS_2


class Publisher:
    """
    An asynchronous class to forward any readings in the provided queue to a configured broker.

    The Publisher class takes an asynchronous queue that gets populated by NFCReading objects, publishing the readings
    to a mqtt broker.
    """

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._queue = queue
        self._publish_topic = ""
        self._broker_address = ""
        # TODO Read ip address and topic specified in config.txt Done
        with open('config.txt', 'r') as file:
            lines = file.readlines()  # Returns a list where each element is a line
            self._broker_address = lines[0].strip()
            self._publish_topic = lines[1].strip()


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
        await asyncio.sleep(0)
        return False

    # TODO Publish every 30 seconds
    # TODO Handle cases where publishing fails due to connection errors
    async def publish_forever(self) -> None:
        """
        Loops forever waiting for readings and publishing to the mqtt broker
        :return: None
        """
        while True:
            await asyncio.sleep(0.5)
            await self.publish([])

    async def publish_with_qos_2(self,broker_url, topic, payload):
        mqtt_config = {
            "keep_alive": 60,  # Time in seconds for keep-alive pings
            "ping_delay": 1,  # Delay before sending a ping after the keep-alive time
            "reconnect_retries": 10,  # Maximum reconnection attempts
            "reconnect_max_interval": 5,  # Maximum interval between retries (seconds)
        }

        client = MQTTClient(config=mqtt_config)

        try:
            # Connect to the broker
            await client.connect(broker_url)
            print(f"Connected to broker: {broker_url}")

            # Publish the message
            await client.publish(topic, payload.encode(), qos=QOS_2)
            print(f"Message published to topic '{topic}' with QoS 2.")

        except ConnectException as e:
            print(f"Failed to connect to the broker: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await client.disconnect()
            print("Disconnected from broker.")


readings_queue: asyncio.Queue[NFCReading] = asyncio.Queue()
x = Publisher = Publisher(readings_queue)
print(x._broker_address, x._publish_topic)