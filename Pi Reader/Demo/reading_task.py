import asyncio
import time

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

    def __str__(self):
        return self.generate_payload()


class HackContainer:

    def __init__(self):
        self.contains = None


async def read_forever(readings_queue: asyncio.Queue):
    # Open device
    reading = HackContainer()

    def on_connect(tag):
        # If contains records
        if tag.ndef is not None and len(tag.ndef.records) != 0:
            record = tag.ndef.records[0]
            # If contains valid record
            if isinstance(record, ndef.TextRecord):
                print(record)
                user_id = record.text

                # Push  reading to queue
                reading.contains = NFCReading(READER_ID, user_id)

            else:
                print("INVALID RECORD", record)
                return False

        else:
            return False

        return True

    rdwr_options = {
        'on-connect': on_connect,
    }

    with nfc.ContactlessFrontend("usb") as clf:

        while True:
            # Read Tag
            started = time.time()
            result = clf.connect(rdwr=rdwr_options, terminate=lambda: time.time() - started > 1)

            # If empty
            if result is None:
                print("None")
                continue

            # If error
            if not result:
                print("Error")
                break

            if reading.contains:
                print("reading", reading.contains)
                await readings_queue.put(reading.contains)
                reading.contains = None

            # Allow asyncio to switch context
            await asyncio.sleep(1)

            print("Waiting")

    print("Exit")
