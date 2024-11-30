import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from hypercorn.asyncio import serve
from hypercorn.config import Config
from pydantic import BaseModel

class PurchaseNFCRequest(BaseModel):
    email: str
    points: str

async def fetch_points(id: str):
    url = "https://gaming.kfupm.org/wp-json/my-api/v1/get-attendee"  # Replace with your API URL
    # headers = {"Authorization": "Bearer YOUR_API_KEY"}  # Replace with your API key if needed
    params = {"email": id}  # Replace with your query parameters

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()  # Parse JSON response
                print(f"Fetched data: {data}")
                return data["attendee"]["points"]
            else:
                print(f"Failed to fetch data: {response.status}, {await response.text()}")

async def add_points(email: str, points: int):
    url = "https://gaming.kfupm.org/wp-json/my-api/v1/add-point"
    payload = {"user_identifier": email, "points": points}  # Replace with your payload

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"Successfully added points: {data}")
                return data
            else:
                error_text = await response.text()
                print(f"Failed to add points: {response.status}, {error_text}")
                raise HTTPException(status_code=response.status, detail=error_text)

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
            """Read NFC tag and fetch points.
              Returns the last reading and points or an empty string if no reading."""
            last_reading = ""
            while not self._queue.empty():
                last_reading = await self._queue.get()
            if last_reading:
                points = await fetch_points(last_reading)
                return {"id": last_reading, "points": points}
            else:
                return {"id": "", "points": 0}

        @self.app.post("/purchase_nfc")
        async def purchase_nfc(request: PurchaseNFCRequest):
            try:
                print(f"Adding points for {request}...")
                # Assuming add_points is an async function
                response = await add_points(request.email, request.points)
                return {"message": "Points added successfully", "details": response}
            except HTTPException as e:
                raise e

    async def run(self):
        config = Config()
        config.bind = ["localhost:5000"]
        await serve(self.app, config)
