import asyncio
import logging
import random

ID_LENGTH = 10
ID_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

logger = logging.getLogger(__name__)


class RandomReader:

    def __init__(self, queue: asyncio.Queue[str]):
        self._queue = queue

    @staticmethod
    def _generate_random_id(length: int):
        return ''.join(random.choices(ID_CHARS, k=length))

    async def readings_task(self) -> None:
        while True:
            # Wait for a random time
            await asyncio.sleep(random.randint(1, 2))

            # Create a random id
            random_user_id = self._generate_random_id(ID_LENGTH)

            # Put to queue
            logger.debug("Putting random user id to queue")
            await self._queue.put(random_user_id)
