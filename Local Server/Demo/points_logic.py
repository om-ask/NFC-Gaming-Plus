import logging

from pipeline import PipeLine, Payload

logger = logging.getLogger(__name__)


async def process_logic_forever(pipeline: PipeLine):
    while True:
        # Get reading
        published_payload: Payload = await pipeline.get_reading()
        logger.info("Received published payload")

        # TODO some custom quest logic
        published_payload.set_points(5)

        # Publish to processed queue
        await pipeline.add_processed_message(published_payload)
        logger.info("Put processed message")
