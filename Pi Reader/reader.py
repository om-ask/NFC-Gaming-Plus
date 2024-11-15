import asyncio
import logging
import time
import ndef
import nfc

from readings import NFCReading, TagType, Quest, User

# TODO Document this code and test
logger = logging.getLogger(__name__)


# TODO Handle Exceptions
class NFCReaderDevice:

    TARGETS = [nfc.clf.RemoteTarget(t) for t in ('106A', '106B', '212F')]

    def __init__(self):
        logger.info("Initializing NFC reader device")
        self._clf = nfc.ContactlessFrontend("usb")
        # Config beep and led
        self.buzzer_and_led_on("blink_red_to_green", 100, 2, "short")
        self.buzzer_and_led_on("clear", 100, 1, "none")
        logger.info("Finished initializing NFC reader device")

    def close(self):
        self._clf.close()

    def find_tag(self) -> nfc.tag.Tag | None:
        target_tag: nfc = self._clf.sense(*self.TARGETS, iterations=5, interval=0.5)
        if target_tag is None:
            return
        logger.debug("Target found")
        if target_tag.sel_res and target_tag.sel_res[0] & 0x40:
            logger.debug("invalid bytes 1")
            return
        elif target_tag.sensf_res and target_tag.sensf_res[1:3] == b"\x01\xFE":
            logger.debug("invalid bytes 2")
            return

        tag = nfc.tag.activate(self._clf, target_tag)
        if tag is None:
            logger.debug("Could not activate")
            return

        logger.debug("Returning tag")
        return tag

    def read_tag(self, check=lambda tag:True) -> nfc.tag.Tag:
        """
        Blocking
        """
        while True:
            tag = self.find_tag()
            if tag and check(tag):
                logger.info("Beeping for valid tag")
                self.buzzer_and_led_on("blink_green", 100, 1, "short")
                return tag

    def buzzer_and_led_on(self, color_command, cycle_duration_in_ms, repeat, beep_type) -> bool:
        """
        Function was taken from https://github.com/nfcpy/nfcpy/issues/245

        Usage examples:
        buzzer_and_led_on("blink_orange", 1000, 1, "short")
        This will set the color to orange and beep once for 1 second and then go back to what it was set to previously.
        (orange is just green and red led's both on)

        buzzer_and_led_on("clear", 0, 1, "none")
        This clears the buzzer of any previous settings

        buzzer_and_led_on("blink_green", 200, 2, "short")
        This will blink green twice and beep twice for 200 milliseconds and then return to the previous color

        :param color_command:
        :param cycle_duration_in_ms:
        :param repeat:
        :param beep_type:
        :return: success boolean
        """
        match color_command:
            case "clear":
                led_color_hex = "0C"
            case "keep_red":
                led_color_hex = "09"
            case "keep_green":
                led_color_hex = "0A"
            case "keep_orange":
                led_color_hex = "0F"
            case "blink_red":
                led_color_hex = "12"
            case "blink_green":
                led_color_hex = "28"
            case "blink_orange":
                led_color_hex = "F0"
            case "blink_red_to_green":
                led_color_hex = "D8"
            case "blink_green_to_red":
                led_color_hex = "E4"
            case "blink_red_to_green_keep_red":
                led_color_hex = "D9"
            case "blink_red_to_green_keep_green":
                led_color_hex = "DA"
            case "blink_red_to_green_keep_orange":
                led_color_hex = "DB"
            case "blink_green_to_red_keep_red":
                led_color_hex = "E5"
            case "blink_green_to_red_keep_green":
                led_color_hex = "E6"
            case "blink_green_to_red_keep_orange":
                led_color_hex = "E7"

            case _:
                return False

        duration_in_tenths_of_second = int(min(cycle_duration_in_ms / 100, 255))
        timeout_in_seconds = (duration_in_tenths_of_second * repeat * 2 + 3) / 10.0

        repeat_hex = f'{repeat:0{2}x}'

        beep_hex_map = {
            "none": "00",
            "short": "01",
            "long": "03"
        }

        beep_hex = beep_hex_map.get(beep_type)
        if beep_hex is None:
            raise ValueError("Invalid beep count")

        # 4th block chooses color of LED
        # 7th block chooses T1 duration
        # 8th block chooses T2 duration
        # 9th block chooses repetition
        # 10th block chooses when buzzer operates (01 = on T1, 02 = on T2, 03 = on T1 and T2)

        hexvalue = "FF 00 40 {led_control} 04 {timing:0>2X} {timing:0>2X} {repeat:0>1} {beep:0>1}".format(
            led_control=led_color_hex, timing=duration_in_tenths_of_second, repeat=repeat_hex, beep=beep_hex
        )

        # hexvalue = "FF 00 40 {} 04 {} {} {} {}"
        # hexvalue = hexvalue.format(led_color_hex, "{timing:02X}", "{timing:02X}", "{repeat:01}", "{beep:01}")
        # hexvalue = hexvalue.format(led_color_hex, duration_in_tenths_of_second, "{timing:02X}", "{repeat:01}", "{beep:01}")
        # hexvalue = hexvalue.format(led_color_hex, duration_in_tenths_of_second, duration_in_tenths_of_second, "{repeat:01}", "{beep:01}")
        # hexvalue = hexvalue.format(led_color_hex, duration_in_tenths_of_second, duration_in_tenths_of_second, repeat_hex, "{beep:01}")
        # hexvalue = hexvalue.format(led_color_hex, duration_in_tenths_of_second, duration_in_tenths_of_second, repeat_hex, beep_hex)

        try:
            self._clf.device.chipset.ccid_xfr_block(bytearray.fromhex(hexvalue), timeout=timeout_in_seconds)
            time.sleep(timeout_in_seconds)
            return True
        except:
            logger.error("Failed to set led and buzzer with command: " + hexvalue)
            raise

    def __enter__(self):
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
            logger.info("Special Quest Enabled")
            self._special_quest_flag = True

        logger.info("Setting new quest")

        self._previous_quest = self._current_quest
        self._current_quest = quest
        return True

    def switch_quest_back(self) -> bool:
        if self._previous_quest is None:
            return False

        logger.info("Switching to previous quest")
        return self.set_new_quest(self._previous_quest)

    def handle_quest_card(self, tag_text: str, one_time: bool) -> bool:
        return self.set_new_quest(Quest.quest_from_card(tag_text, one_time))

    async def handle_user_tag(self, tag_text: str) -> bool:
        if not self._current_quest:
            logger.info("No current quest")
            return False
        user: User = User.user_from_tag(tag_text)

        user_recorded: bool = self._current_quest.record_user(user)
        if not user_recorded:
            logger.info("User already logged in quest")
            return False

        # Create reading and push to queue
        reading: NFCReading = NFCReading(self._current_quest, user)
        logger.debug("Adding reading to queue")
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
                logger.info("Handling tag" + str(tag))

                await self.handle_tag(tag)


# TODO make the check inside reader to check for current quest and if the user is recorded or not
def tag_check(tag: nfc.tag.Tag) -> bool:
    if not tag.ndef:
        logger.debug("No ndef")
        return False

    if not len(tag.ndef.records) == 1:
        logger.debug("Records list length is not 1")
        return False

    record: ndef.TextRecord = tag.ndef.records[0]
    if not isinstance(record, ndef.TextRecord):
        logger.debug("Record is not a TextRecord")
        return False

    tag_type = TagType.tag_type(record.text)
    if tag_type == TagType.INVALID:
        logger.debug("Invalid tag type")
        return False

    return True

