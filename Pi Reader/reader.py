import asyncio

from readings import NFCReading


# TODO Read from reader and push to queue
async def readings_task(queue: asyncio.Queue[NFCReading]) -> None:
    while True:
        await asyncio.sleep(0)