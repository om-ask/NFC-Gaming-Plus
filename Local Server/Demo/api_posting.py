import asyncio

import aiohttp

from pipeline import PipeLine, Payload

REMOTE_URL = "http://helloworld.test/"
API_PATH = "wp-json/my-api/v1/"
API_KEY = "BlahBlah"


async def add_attendee(session: aiohttp.ClientSession):
    post_args = {
        "first_name": "Om",
        "last_name": "Al",
        "api-key": API_KEY
    }
    response = await session.post(REMOTE_URL + API_PATH + "add-attendee", json=post_args)
    print("REPLY", await response.text())


async def add_points_post(session: aiohttp.ClientSession, payload: Payload):
    # TODO
    # Construct post arguments
    post_args = {
        "user_identifier": payload.user_id,
        "points": str(payload.points),  # TODO FIX API VALIDATION TO INT
        "path": payload.reader_id,
        "api-key": API_KEY
    }
    print("POSTING")
    response = await session.post(REMOTE_URL + API_PATH + "add-point", json=post_args)
    print("REPLY", await response.text())
    # session.post()


async def api_forwarding_forever(pipeline: PipeLine):
    async with aiohttp.ClientSession() as session:
        while True:
            # Wait and get processed payload
            processed_payload = await pipeline.get_processed_message()

            # Forward result to server
            await add_points_post(session, processed_payload)


async def main():
    async with aiohttp.ClientSession() as session:
        await add_attendee(session)


if __name__ == '__main__':
    asyncio.run(main())
