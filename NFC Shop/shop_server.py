import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from hypercorn.asyncio import serve
from hypercorn.config import Config

class Shop_Server:
    def __init__(self, queue: asyncio.Queue[str]):
        """Initialize the Flask app and set up routes."""
        self._queue = queue
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        """Define the API endpoints."""
        @self.app.get('/read_nfc')
        async def read_nfc():
            last_reading = ""
            while not self._queue.empty():
                last_reading = await self._queue.get()
            


            return last_reading

    async def run(self):
        config = Config()
        config.bind = ["0.0.0.0:5000"]
        await serve(self.app, config)