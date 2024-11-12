import asyncio

from readings import NFCReading


class Publisher:
    """
    An asynchronous class to forward any readings in the provided queue to a configured broker.

    The Publisher class takes an asynchronous queue that gets populated by NFCReading objects, publishing the readings
    to a mqtt broker.
    """

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._queue = queue

        # TODO Read ip address and topic specified in config.txt
        self._publish_topic = ""
        self._broker_address = ""


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
            await asyncio.sleep(0)
            await self.publish([])


