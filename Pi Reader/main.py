import asyncio
import logging
import argparse

from readings import NFCReading

# Import tasks
from publisher import Publisher
from reader import readings_task
from random_reader import random_readings_task


# Main function
async def main(no_reader: bool) -> None:
    # Create queue stack
    readings_queue: asyncio.Queue[NFCReading] = asyncio.Queue()

    # Create publisher
    publisher: Publisher = Publisher(readings_queue)

    async with asyncio.TaskGroup() as task_manager:
        # Create the publisher task
        logger.info("Starting publisher task")
        task_manager.create_task(publisher.publish_forever())

        # Create the reading task
        # Check if we should connect to a reader or not
        if no_reader:
            logger.debug("No reader mode: Starting random reader task")
            task_manager.create_task(random_readings_task(readings_queue))

        else:
            logger.info("Starting reader task")
            task_manager.create_task(readings_task(readings_queue))

    logger.info("Finished tasks")



# Run program based on command line arguments
if __name__ == '__main__':
    # Configure logger
    logger = logging.getLogger(__name__)

    # Create a command line parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-nr", "--noreader", help="run on random readings without connecting to a reader")

    # Parse command line arguments
    args = parser.parse_args()

    NO_READER = bool(args.noreader)

    # Run the main function in the asyncio event loop
    asyncio.run(main(NO_READER))
