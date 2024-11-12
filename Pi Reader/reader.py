import asyncio

from readings import NFCReading

class Reader:

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._queue = queue

    # TODO Read from reader and push to queue
    async def readings_task(self) -> None:
        while True:
            await asyncio.sleep(0)