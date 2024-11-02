import asyncio
import ndef
import nfc

from functools import partial


# TODO ENVIRONMENT VARIABLE FOR READER
READER_ID = "A"


class NFCReading:

    def __init__(self, reader_id, user_id):
        self.reader_id = reader_id
        self.user_id = user_id

    def generate_payload(self):
        return (f"{self.reader_id}\n"
                f"{self.user_id}")

    def __str__(self):
        return self.generate_payload()


class ReturnContainer:
    def __init__(self):
        self.item = None


def on_connect(return_result: ReturnContainer, tag):
    # If contains records
    if tag.ndef is not None and len(tag.ndef.records) != 0:
        record = tag.ndef.records[0]
        # If contains valid record
        if isinstance(record, ndef.TextRecord):
            print(record)
            user_id = record.text

            # Write to return container
            return_result.item = NFCReading(READER_ID, user_id)

        else:
            print("INVALID RECORD", record)
            return False

    else:
        return False

    return True


async def read_forever(readings_queue: asyncio.Queue):

    # Open device
    with nfc.ContactlessFrontend("usb") as clf:

        while True:
            returned_reading = ReturnContainer()
            # Read Tag
            rdwr_options = {
                'on-connect': partial(on_connect, returned_reading),
            }
            result = await asyncio.to_thread(clf.connect(rdwr=rdwr_options))

            # If empty
            if result is None:
                print("None")
                continue

            # If error
            if not result:
                print("Error")
                break

            if returned_reading.item:
                await readings_queue.put(returned_reading.item)

            print("Waiting")

    print("Exit")
