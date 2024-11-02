import logging
import asyncio

from reading_task import read_forever
from publish import publish_forever

logger = logging.getLogger(__name__)


async def main():
    buffer = asyncio.Queue()

    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(read_forever(buffer))
        print("Task 1")
        task_group.create_task(publish_forever(buffer))


# Main entry point of the script.
if __name__ == '__main__':  # Corrected __name_
    # Set up logging configuration.
    logging.basicConfig(level=logging.INFO)

    # Run the test_coro function until complete.
    asyncio.run(main())
