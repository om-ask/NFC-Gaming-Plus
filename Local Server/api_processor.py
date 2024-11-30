import asyncio
import logging

from pipeline import Payload, PipeLine
from APIPoster import APIPoster
import os
api_key = os.getenv("API_KEY")

logger = logging.getLogger(__name__)


async def api_forwarding_forever(pipeline: PipeLine):
    logger.info("Starting api process logic")
    api_poster = APIPoster("https://gaming.kfupm.org/wp-json", api_key)

    while True:
        try:
            # Get reading
            processed_payload: Payload = await pipeline.get_reading()

            result = await api_poster.addPoints(processed_payload.user_id, processed_payload.points, processed_payload.quest_id)

            if not result:
                await pipeline.add_processed_message(processed_payload)

        except Exception as e:
            logger.error("Error processing message: ", str(e))


async def test_api():
    for i in range(3):
        api_poster = APIPoster("https://gaming.kfupm.org/wp-json", api_key)
        result = await api_poster.addPoints("Mohammed@g.g", 10000, f"QUEST{i}")

        print(result)


if __name__ == '__main__':
    print(api_key)
    asyncio.run(test_api())