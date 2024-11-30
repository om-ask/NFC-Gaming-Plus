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

            await api_poster.addPoints(processed_payload.user_id, processed_payload.points, processed_payload.quest_id)

        except Exception as e:
            logger.error("Error processing message: ", str(e))
