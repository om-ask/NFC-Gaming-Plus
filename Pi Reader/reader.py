import asyncio
import logging
import time
import ndef
import nfc

from readings import NFCReading, TagType, Quest, User

# Create a logger for this module
logger = logging.getLogger(__name__)
# TODO Log

class NFCReaderDevice:
    """
    Class that represents the actual NFC reader device hardware

    Provides methods for reading tags, buzzing and turning on leds.

    All methods are blocking, including initialization
    """

    # Target tag types for detecting in find_tag
    TARGETS = [nfc.clf.RemoteTarget(t) for t in ('106A', '106B', '212F')]

    def __init__(self):
        logger.info("Initializing NFC reader device")

        # Open device
        self._clf = nfc.ContactlessFrontend("usb")

        # Beep and configure led
        self.buzzer_and_led_on("blink_red_to_green", 100, 2, "short")
        self.buzzer_and_led_on("clear", 100, 1, "none")
        logger.info("Finished initializing NFC reader device")

    def open(self) -> None:
        """
        Open/Reopen device
        :return: None
        """
        # Open device
        self._clf.open("usb")


    def close(self) -> None:
        """
        Close the device
        :return: None
        """
        # Close device
        self._clf.close()

    def find_tag(self) -> nfc.tag.Tag | None:
        """
        Attempts to detect a nfc tag in the vicinity of the reader.

        Blocks for a couple of seconds

        :return: A Tag object if successfully sensed and activated, None otherwise
        """
        # Attempt detection
        target_tag: nfc = self._clf.sense(*self.TARGETS, iterations=5, interval=0.5)
        if target_tag is None:
            # No tag was found
            return

        # A possible tag was found
        logger.debug("Target tag found")

        # Validate tag
        if target_tag.sel_res and target_tag.sel_res[0] & 0x40:
            logger.debug("Target has invalid bytes 1")
            return
        elif target_tag.sensf_res and target_tag.sensf_res[1:3] == b"\x01\xFE":
            logger.debug("Target has invalid bytes 2")
            return

        # Attempt to activate target tag
        tag = nfc.tag.activate(self._clf, target_tag)
        if tag is None:
            # Tag could not be activated
            logger.debug("Could not activate tag")
            return

        # Tag was successfully activated; return it
        logger.debug("Tag successfully activated and returned")
        return tag

    def read_tag(self, check=lambda tag:True) -> nfc.tag.Tag:
        """
        Method that blocks until a valid tag is found and read by the reader device.
        If a check is optionally provided, the tag will be validated by the check function.

        The check function accepts one argument only which is the Tag object and
        should return a boolean indicating validity.

        :return: A valid tag that passes the check (if provided)
        """
        while True:
            tag = self.find_tag()
            if tag and check(tag):
                logger.debug("Valid tag read and returned")
                return tag

    def buzzer_and_led_on(self, color_command, cycle_duration_in_ms, repeat, beep_type) -> None:
        """
        Function was taken from https://github.com/nfcpy/nfcpy/issues/245

        Control device buzzer and led

        Usage examples:
        buzzer_and_led_on("blink_orange", 1000, 1, "short")
        This will set the color to orange and beep once for 1 second and then go back to what it was set to previously.
        (orange is just green and red led's both on)

        buzzer_and_led_on("clear", 0, 1, "none")
        This clears the buzzer of any previous settings

        buzzer_and_led_on("blink_green", 200, 2, "short")
        This will blink green twice and beep twice for 200 milliseconds and then return to the previous color

        :param color_command: A string. See function match table for possible commands
        :param cycle_duration_in_ms: The length of one beep/led switch cycle
        :param repeat: Number of cycles
        :param beep_type: A string representing the type of beep. "short", "none" or "long"
        :return: None
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
                raise ValueError("Invalid color command")

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

        try:
            self._clf.device.chipset.ccid_xfr_block(bytearray.fromhex(hexvalue), timeout=timeout_in_seconds)
            time.sleep(timeout_in_seconds)
        except:
            logger.error("Failed to set led and buzzer with command: " + hexvalue)
            raise

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# TODO Handle exceptions (device disconnected, etc)
# TODO Test this code extensively
# NOTE: Possible edge case may occur when the same special quest is read multiple time in a row
class Reader:
    """
    Asynchronous class that performs custom tag reading logic using a NFCReaderDevice and pushes the results to a queue

    Handles quests and one time quests
    """

    # Custom buzzer and led blinking configurations for different situations
    QUEST_SET = "blink_green", 200, 1, "short"
    QUEST_ALREADY_SET = "blink_orange", 200, 1, "none"

    SPECIAL_QUEST_SET = "blink_green", 100, 2, "short"
    SPECIAL_QUEST_ALREADY_SET = "blink_orange", 100, 2, "none"

    USER_RECORDED = "blink_green", 100, 1, "short"
    USER_ALREADY_RECORD = "blink_orange", 100, 1, "none"

    NO_QUEST_CONFIGURED = "blink_red", 200, 1, "short"

    def __init__(self, queue: asyncio.Queue[NFCReading]):
        # Create the reader device and open it
        self._device = NFCReaderDevice()

        # Save queue reference
        self._queue = queue

        # Create the quest instance variables
        self._current_quest: Quest | None = None
        self._previous_quest: Quest | None = None

        self._special_quest_flag: bool = False

    def set_new_quest(self, quest: Quest) -> bool:
        """
        Sets the given quest as the current quest, handling special quests
        
        :param quest: The Quest object to set
        :return: True if quest was set, False if the same quest is already set
        """
        if quest == self._current_quest:
            # Quest is already current
            return False

        if quest.one_time:
            # Enable special quest flag if the quest is one-time
            logger.info("Special Quest Enabled")
            self._special_quest_flag = True

        logger.info("Setting new quest")
        
        # Set the new quest to current while setting previous quest to old current 
        self._previous_quest = self._current_quest
        self._current_quest = quest
        return True

    def switch_quest_back(self) -> bool:
        """
        Switch current and previous quests
        
        :return: True if quests were switched, False if no previous or current quest is set 
        """
        if self._previous_quest is None or self._current_quest is None:
            # No current or previous quest to switch between
            return False

        logger.info("Switching to previous quest")
        return self.set_new_quest(self._previous_quest)

    def handle_quest_card(self, tag_text: str, one_time: bool) -> bool:
        """
        Transform the given tag text into a Quest object and update the current quest

        :param tag_text: The text in the tag's record
        :param one_time: True if the quest is special, False otherwise
        :return: True if the current quest was updated successfully, False otherwise (quest is already set)
        """
        return self.set_new_quest(Quest.quest_from_card(tag_text, one_time))

    async def handle_user_tag(self, tag_text: str) -> bool:
        """
        Create a User from the given text and record it into the current quest, then compose an NFCReading to push
        to the queue

        :param tag_text: The text is the tag's record
        :return: True if the user was recorded successfully, False otherwise
        """
        # Create the user from the tag text
        user: User = User.user_from_tag(tag_text)

        # Record the user into the current quest and check if the user is already recorded
        user_just_recorded: bool = self._current_quest.record_user(user)
        if not user_just_recorded:
            # User already recorded previously
            logger.info("User already recorded in quest")
            return False

        # Create reading and push to queue
        reading: NFCReading = NFCReading(self._current_quest, user)
        logger.debug("Adding reading to queue")
        await self._queue.put(reading)

        # If the current quest was one time only, switch to the previous quest and update the special quest flag
        if self._special_quest_flag:
            self._special_quest_flag = False
            self.switch_quest_back()

        return True

    async def handle_tag(self, tag: nfc.tag.Tag) -> bool:
        """
        Given a valid Tag object, extract the text, identify the TagType, and then handle the tag according to the tag
        type
        :param tag: The valid Tag object to handle
        :return: True if tag was meaningfully handled, False otherwise (such as repeated tag readings)
        """
        # Extract the text record from the tag
        record: ndef.TextRecord = tag.ndef.records[0]

        # Determine tag type from the record text and handle the tag according to its type while beeping
        tag_type = TagType.tag_type(record.text)
        match tag_type:
            case TagType.QUEST:
                # Handle it as a quest card
                if self.handle_quest_card(record.text, False):
                    # Beep for success
                    await self.beep(*self.QUEST_SET)
                    return True

                else:
                    # Quest is already set, but beep to notify this
                    await self.beep(*self.QUEST_ALREADY_SET)
                    return False

            case TagType.ONE_TIME_QUEST:
                # Handle it as a special quest card (one time)
                if self.handle_quest_card(record.text, True):
                    # Beep for success
                    await self.beep(*self.SPECIAL_QUEST_SET)
                    return True

                else:
                    # Special quest is already set, but beep to notify this
                    await self.beep(*self.SPECIAL_QUEST_ALREADY_SET)
                    return False

            case TagType.USER:
                if not self._current_quest:
                    # No quest to record the user
                    logger.warning("No current quest configured. User discarded")
                    # Beep to notify this
                    await self.beep(*self.NO_QUEST_CONFIGURED)
                    return False

                # Handle it as a user tag
                if await self.handle_user_tag(record.text):
                    # Beep for success
                    await self.beep(*self.USER_RECORDED)
                    return True

                else:
                    # User already did quest, but beep to notify this
                    await self.beep(*self.USER_ALREADY_RECORD)
                    return False

        # Return False if tag type is invalid (THIS SHOULD NOT LOGICALLY HAPPEN)
        return False

    async def readings_task(self) -> None:
        """
        An asynchronous task that runs forever, reading nfc tags and acting accordingly such as putting new readings to
        the queue or switching quests when reading quest cards.
        :return: None
        """
        with self._device as activated_device:
            while True:
                tag = await asyncio.to_thread(activated_device.read_tag, tag_check)
                logger.info("Handling tag" + str(tag))

                await self.handle_tag(tag)

    async def beep(self, color_command, cycle_duration_in_ms, repeat, beep_type) -> None:
        """
        Function was taken from https://github.com/nfcpy/nfcpy/issues/245

        Wraps NFCReaderDevice's buzz method but makes it asynchronous

        Control device buzzer and led

        Usage examples:
        buzzer_and_led_on("blink_orange", 1000, 1, "short")
        This will set the color to orange and beep once for 1 second and then go back to what it was set to previously.
        (orange is just green and red led's both on)

        buzzer_and_led_on("clear", 0, 1, "none")
        This clears the buzzer of any previous settings

        buzzer_and_led_on("blink_green", 200, 2, "short")
        This will blink green twice and beep twice for 200 milliseconds and then return to the previous color

        :param color_command: A string. See function match table for possible commands
        :param cycle_duration_in_ms: The length of one beep/led switch cycle
        :param repeat: Number of cycles
        :param beep_type: A string representing the type of beep. "short", "none" or "long"
        :return: None
        """
        try:
            await asyncio.to_thread(self._device.buzzer_and_led_on, color_command,
                                    cycle_duration_in_ms, repeat, beep_type)

        except IOError as io_error:
            logger.warning("Device beeping failed due to: " + str(io_error))

        # TODO Possible handle other unforeseen errors?


def tag_check(tag: nfc.tag.Tag) -> bool:
    """
    A check that checks if the given Tag is valid for usage in the Reader class
    :param tag: The Tag instance to be checked
    :return: True if valid, False otherwise
    """
    # Check if tag has ndef records
    if not tag.ndef:
        logger.debug("No ndef")
        return False

    # Check if only one record exists in tag
    if not len(tag.ndef.records) == 1:
        logger.debug("Records list length is not 1")
        return False

    # Check if record is of a valid type
    record: ndef.TextRecord = tag.ndef.records[0]
    if not isinstance(record, ndef.TextRecord):
        logger.warning("Record is not a TextRecord")
        return False

    # Check if the text in the record resolves into a valid TagType
    tag_type = TagType.tag_type(record.text)
    if tag_type == TagType.INVALID:
        return False

    return True
