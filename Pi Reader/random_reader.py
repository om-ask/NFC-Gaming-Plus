import asyncio
import logging
import random

from readings import NFCReading, Quest, User

ID_LENGTH = 10
ID_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

logger = logging.getLogger(__name__)


class RandomReader:

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._queue = queue

    @staticmethod
    def _generate_random_id(length: int):
        return ''.join(random.choices(ID_CHARS, k=length))

    async def readings_task(self) -> None:
        while True:
            # Wait for a random time
            await asyncio.sleep(random.randint(5, 30))

            # Create a random reading
            random_quest_id = self._generate_random_id(ID_LENGTH)
            random_user_id = self._generate_random_id(ID_LENGTH)

            random_reading = NFCReading(Quest(random_quest_id), User(random_user_id))

            # Put to queue
            logger.debug("Putting random reading to queue")
            await self._queue.put(random_reading)
