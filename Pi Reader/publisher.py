import asyncio

from readings import NFCReading


class Publisher:

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._queue = queue

        # TODO Read ip address and topic specified in config.txt
        self._publish_topic = ""
        self._broker_address = ""


    async def publish(self, readings: list[NFCReading]) -> bool:
        """
        Publish the given readings to the broker address

        The format of the payload to be sent:
        QUEST_ID
        USER1_ID
        USER2_ID
        USER3_ID

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


