import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hypercorn.asyncio import serve
from hypercorn.config import Config
import aiohttp


async def fetch_points():
    url = "http://www.randomnumberapi.com/api/v1.0/random"  # Replace with your API URL
    headers = {"Authorization": "Bearer YOUR_API_KEY"}  # Replace with your API key if needed
    params = {"min": "100", "max": "1000", "count": "1"} # Replace with your query parameters

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()  # Parse JSON response
                return data
            else:
                print(f"Failed to fetch data: {response.status}, {await response.text()}")

class Shop_Server:
    def __init__(self, queue: asyncio.Queue[str]):
        """Initialize the Flask app and set up routes."""
        self._queue = queue
        self.app = FastAPI()
        self.setup_cors()
        self.setup_routes()

    def setup_cors(self):
        """Set up CORS middleware for the FastAPI app."""
        # Add CORSMiddleware to the FastAPI app
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Define the API endpoints."""
        @self.app.get('/read_nfc')
        async def read_nfc():
            last_reading = ""
            while not self._queue.empty():
                last_reading = await self._queue.get()
            
            points = await fetch_points()

            return points[0]

    async def run(self):
        config = Config()
        config.bind = ["0.0.0.0:5000"]
        await serve(self.app, config)

