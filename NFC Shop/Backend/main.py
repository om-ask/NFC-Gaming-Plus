import asyncio
import logging
import argparse

from readings import NFCReading

# Import shop_server and reader
from reader import Reader
from shop_server import Shop_Server


# Main function
async def main(no_reader: bool) -> None:
    # Create queue stack
    readings_queue: asyncio.Queue[NFCReading] = asyncio.Queue()

    # Create shop server
    shop_server: Shop_Server = Shop_Server(readings_queue)

    # Check if we should connect to a real nfc reader or not
    if no_reader:
        logger.debug("No reader mode: Using random reader")
        from random_reader import RandomReader

        reader: RandomReader = RandomReader(readings_queue)

    else:
        # Create normal reader
        reader: Reader = Reader(readings_queue)

    # Create tasks
    async with asyncio.TaskGroup() as task_manager:

        # Start the reading task
        logger.info("Starting reader task")
        task_manager.create_task(reader.readings_task())

        # strat shop server
        logger.info("Starting shop server")
        task_manager.create_task(shop_server.run())

    logger.info("Finished tasks")


# Run program based on command line arguments
if __name__ == '__main__':
    # Configure logger
    logger = logging.getLogger("pi-reader-main")
    logging.basicConfig(level=logging.DEBUG)

    # Create a command line parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-nr", "--noreader", help="run on random readings without connecting to a reader",
                        action="store_true")

    # Parse command line arguments
    args = parser.parse_args()

    NO_READER = args.noreader

    # Run the main function in the asyncio event loop
    asyncio.run(main(NO_READER))
