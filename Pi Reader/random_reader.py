import asyncio
import string
import random

from readings import NFCReading

ID_LENGTH = 10

# TODO Randomly wait for random times. Then create a random reading and add it to the queue
async def random_readings_task(queue: asyncio.Queue[NFCReading]) -> None:
    while True:
        # Wait for a random time
        await asyncio.sleep(random.randint(5, 30))

        # Create a random reading
        random_quest_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=ID_LENGTH))
        random_user_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=ID_LENGTH))

        random_reading = NFCReading("QUEST" + random_quest_id, "USER" + random_user_id)

        # Put to queue
        await queue.put(random_reading)
