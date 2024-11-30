import logging
from database import PointsRepo
from pointsManager import PointsManager
from pipeline import PipeLine, Payload

logger = logging.getLogger(__name__)

async def process_logic_forever(pipeline: PipeLine):
    logger.info("Starting process logic")
    # Connect to database
    logger.info("Connecting to database")
    pointsRepo = PointsRepo("database.db")
    await pointsRepo.connect()
    pointsManager = PointsManager(pointsRepo)
    while True:
        try:
        # Get reading
            published_payload: Payload = await pipeline.get_reading()
            logger.info("Received published payload")

            # TODO some custom quest logic
            # published_payload.set_points(5)
            user_id = published_payload.user_id.strip()
            quest_id = published_payload.quest_id.strip()
            logger.info("user_id: %s, reader_id: %s", user_id, quest_id)
            points = await pointsManager.recordVisit(user_id, quest_id)
            
            if points is not None:
                published_payload.set_points(points)
                await pipeline.add_processed_message(published_payload)
            # Publish to processed queue
            
            logger.info("Put processed message")
        except Exception as e:
            logger.error("Error processing message: ", str(e))
