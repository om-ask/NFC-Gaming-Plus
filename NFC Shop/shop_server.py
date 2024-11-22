import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from hypercorn.asyncio import serve
from hypercorn.config import Config


from readings import NFCReading

class Shop_Server:
    def __init__(self, queue: asyncio.Queue[NFCReading]):
        """Initialize the Flask app and set up routes."""
        self._queue = queue
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        """Define the API endpoints."""
        @self.app.get('/read_nfc')
        async def read_nfc():
            readings = []
            while not self._queue.empty():
                readings.append(await self._queue.get())
            return readings

    async def run(self):
        config = Config()
        config.bind = ["0.0.0.0:5000"]
        await serve(self.app, config)