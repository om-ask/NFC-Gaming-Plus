import asyncio
import ndef
import nfc

from readings import NFCReading, TagType, Quest, User

# TODO Document this code and test


# TODO Handle Exceptions
class NFCReaderDevice:

    TARGETS = [nfc.clf.RemoteTarget(t) for t in ('106A', '106B', '212F')]

    def __init__(self):
        self._clf = nfc.ContactlessFrontend()

    def open(self):
        self._clf.open("usb")

    def close(self):
        self._clf.close()

    def find_tag(self) -> nfc.tag.Tag | None:
        target_tag: nfc = self._clf.sense(self.TARGETS)
        if target_tag is None:
            return

        tag = nfc.tag.activate(self._clf, target_tag)
        if tag is None:
            return

        return tag

    def read_tag(self, check=lambda tag:True) -> nfc.tag.Tag:
        """
        Blocking
        """
        while True:
            tag = self.find_tag()
            if tag and check(tag):
                self.beep()
                return tag

    def beep(self):
        self._clf.device.turn_on_led_and_buzzer()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# TODO Handle exceptions
class Reader:

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        self._device = NFCReaderDevice()

        self._queue = queue

        self._current_quest: Quest | None = None
        self._previous_quest: Quest | None = None

        self._special_quest_flag: bool = False

    def set_new_quest(self, quest: Quest) -> bool:
        if quest == self._current_quest:
            return False

        if quest.one_time:
            self._special_quest_flag = True

        self._previous_quest = self._current_quest
        self._current_quest = quest
        return True

    def switch_quest_back(self) -> bool:
        return self.set_new_quest(self._previous_quest)

    def handle_quest_card(self, tag_text: str, one_time: bool) -> bool:
        return self.set_new_quest(Quest.quest_from_card(tag_text, one_time))

    async def handle_user_tag(self, tag_text: str) -> bool:
        user: User = User.user_from_tag(tag_text)

        user_recorded: bool = self._current_quest.record_user(user)
        if user_recorded:
            return False

        # Create reading and push to queue
        reading: NFCReading = NFCReading(self._current_quest, user)
        await self._queue.put(reading)

        if self._special_quest_flag:
            self._special_quest_flag = False
            self.switch_quest_back()

        return True

    async def handle_tag(self, tag: nfc.tag.Tag) -> bool:
        record: ndef.TextRecord = tag.ndef.records[0]
        tag_type = TagType.tag_type(record.text)
        match tag_type:
            case TagType.QUEST:
                return self.handle_quest_card(record.text, False)

            case TagType.ONE_TIME_QUEST:
                return self.handle_quest_card(record.text, True)

            case TagType.USER:
                return await self.handle_user_tag(record.text)

            case _:
                return False

    async def readings_task(self) -> None:
        with self._device as activated_device:
            while True:
                tag = await asyncio.to_thread(activated_device.read_tag, tag_check)

                await self.handle_tag(tag)


def tag_check(tag: nfc.tag.Tag) -> bool:
    if not tag.ndef:
        return False

    if not len(tag.ndef.records) == 1:
        return False

    record: ndef.TextRecord = tag.ndef.records[0]
    if not isinstance(record, ndef.TextRecord):
        return False

    tag_type = TagType.tag_type(record.text)
    if tag_type == TagType.INVALID:
        return False

    return True

