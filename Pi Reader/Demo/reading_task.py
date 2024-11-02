import asyncio

import ndef
import nfc

# TODO ENVIRONMENT VARIABLE FOR READER
READER_ID = "A"


class NFCReading:

    def __init__(self, reader_id, user_id):
        self.reader_id = reader_id
        self.user_id = user_id

    def generate_payload(self):
        return (f"{self.reader_id}\n"
                f"{self.user_id}")


async def read_forever(readings_queue: asyncio.Queue):
    # Open device
    with nfc.ContactlessFrontend("usb") as clf:
        while True:
            # Read Tag
            result_tag = clf.connect()

            # If empty
            if result_tag is None:
                print("None")
                continue

            # If error
            if not result_tag:
                print("Error")
                break

            # If contains records
            if result_tag.ndef is not None and len(result_tag.ndef.records) != 0:
                record = result_tag.ndef.records[0]
                # If contains valid record
                if isinstance(record, ndef.TextRecord):
                    print(record)
                    user_id = record.text

                    # Push  reading to queue
                    reading = NFCReading(READER_ID, user_id)
                    await readings_queue.put(reading)

                else:
                    print("INVALID RECORD", record)

            print("Waiting")

    print("Exit")
