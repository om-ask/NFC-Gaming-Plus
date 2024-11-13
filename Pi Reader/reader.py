import asyncio
import ndef
import nfc

from readings import NFCReading


class NFCReaderDevice:
    def __init__(self):
        self._clf = nfc.ContactlessFrontend()

    def open(self):
        self._clf.open("usb")

    def close(self):
        self._clf.close()

    def find_tag(self) -> nfc.tag.Tag | None:
        target_tag: nfc = self._clf.sense('106A', '106B', '212F')
        if target_tag is None:
            return

        tag = nfc.tag.activate(self._clf, target_tag)
        if tag is None:
            return

        return tag

    def read_tag(self) -> nfc.tag.Tag:
        """
        Blocking
        """
        while True:
            tag = self.find_tag()
            if tag:
                return tag

    def beep(self):
        self._clf.device.turn_on_led_and_buzzer()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Reader:

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._device = NFCReaderDevice()

        self._queue = queue

        self._current_quest = ""
        self._previous_quest = ""

    def set_new_quest(self, quest: str) -> None:
        self._previous_quest = self._current_quest
        self._current_quest = quest

    def switch_quest_back(self) -> None:
        self.set_new_quest(self._previous_quest)

    async def handle_tag(self, tag: nfc.tag.Tag) -> bool:
        if not tag.ndef or not tag.ndef.records:
            return False
        # TODO Check if it a quest or user card, and then act accordingly



    async def readings_task(self) -> None:
        with self._device as activated_device:
            while True:
                tag = await asyncio.to_thread(activated_device.read_tag)
                success = self.handle_tag(tag)
                if success:
                    activated_device.beep()
