import aiohttp

from pipeline import PipeLine, Payload


async def add_points_post(session: aiohttp.ClientSession, payload: Payload):
    # TODO
    # Construct post arguments

    print("POSTING")
    # session.post()


async def api_forwarding_forever(pipeline: PipeLine):
    async with aiohttp.ClientSession() as session:
        # Wait and get processed payload
        processed_payload = await pipeline.get_processed_message()

        # Forward result to server
        await add_points_post(session, processed_payload)
