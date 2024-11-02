from asyncio import Queue


class Payload:

    def __init__(self, reader_id, user_id):
        self.reader_id = reader_id
        self.user_id = user_id

        self.processed = False
        self.points = 0

    def set_points(self, points):
        self.processed = True
        self.points = points


class PipeLine:
    def __init__(self):
        self._published_messages = Queue()
        self._processed_messages = Queue()

    async def add_reading(self, reading: Payload):
        await self._published_messages.put(reading)

    async def get_reading(self):
        return await self._published_messages.get()

    async def add_processed_message(self, reading: Payload):
        await self._processed_messages.put(reading)

    async def get_processed_message(self):
        return await self._processed_messages.get()
