import asyncio
import logging
import ndef
import nfc

from readings import NFCReading, TagType, Quest, User
from reader_device import NFCReaderDevice

# Create a logger for this module
logger = logging.getLogger(__name__)


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

        try:
            with open("CQuest.txt", "r") as file:
                current_quest_id = file.read().strip()  # Read and remove any leading/trailing whitespace
                logger.debug(("Current Quest:" + current_quest_id))
                self._current_quest = Quest(current_quest_id[5:])

        except FileNotFoundError:
            logger.error("Error, CQuest.txt not found")

        except OSError as e:
            logger.error("Error with opening CQuest.txt file")

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

        else:
            with open("CQuest.txt", "w") as file:
                file.write(quest.message())

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
        flag = True
        # Create the user from the tag text
        user: User = User.user_from_tag(tag_text)

        # Record the user into the current quest and check if the user is already recorded
        user_just_recorded: bool = self._current_quest.record_user(user)
        if not user_just_recorded:
            # User already recorded previously
            logger.info("User already recorded in quest")
            flag = False

        # Create reading and push to queue
        reading: NFCReading = NFCReading(self._current_quest, user)
        logger.debug("Adding reading to queue")
        await self._queue.put(reading)

        # If the current quest was one time only, switch to the previous quest and update the special quest flag
        if self._special_quest_flag:
            self._special_quest_flag = False
            self.switch_quest_back()

        return flag

    async def handle_tag(self, tag: nfc.tag.Tag) -> bool:
        """
        Given a valid Tag object, extract the text, identify the TagType, and then handle the tag according to the tag
        type
        :param tag: The valid Tag object to handle
        :return: True if tag was meaningfully handled, False otherwise (such as repeated tag readings)
        """
        # Extract the text record from the tag
        try:
            record: ndef.TextRecord = tag.ndef.records[0]
            text = record.text

        except Exception as e:
            logger.error(e)
            return False

        # Determine tag type from the record text and handle the tag according to its type while beeping
        tag_type = TagType.tag_type(text)
        match tag_type:
            case TagType.QUEST:
                # Handle it as a quest card
                if self.handle_quest_card(record.text, False):
                    # Beep for success
                    # await self.beep(*self.QUEST_SET)
                    await self.normal_beep(2)
                    return True

                else:
                    # Quest is already set, but beep to notify this
                    # await self.beep(*self.QUEST_ALREADY_SET)
                    return False

            case TagType.ONE_TIME_QUEST:
                # Handle it as a special quest card (one time)
                if self.handle_quest_card(record.text, True):
                    # Beep for success
                    # await self.beep(*self.SPECIAL_QUEST_SET)
                    await self.normal_beep(2)
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
                    # await self.beep(*self.NO_QUEST_CONFIGURED)
                    await self.normal_beep(3)
                    return False

                # Handle it as a user tag
                if await self.handle_user_tag(record.text):
                    # Beep for success
                    # await self.beep(*self.USER_RECORDED)
                    await self.normal_beep(1)
                    return True

                else:
                    # User already did quest, but beep to notify this
                    # await self.beep(*self.USER_ALREADY_RECORD)
                    await self.normal_beep(3)
                    return False

        # Return False if tag type is invalid (THIS SHOULD NOT LOGICALLY HAPPEN)
        return False

    async def readings_task(self) -> None:
        """
        An asynchronous task that runs forever, reading nfc tags and acting accordingly such as putting new readings to
        the queue or switching quests when reading quest cards.
        :return: None
        """
        while True:
            try:
                with self._device as activated_device:
                    # Beep 2 times for activated device
                    await self.normal_beep(2)
                    while True:
                        tag = await asyncio.to_thread(activated_device.read_tag, tag_check)

                        logger.info("Handling tag" + str(tag))
                        await self.handle_tag(tag)

            except OSError as e:
                logger.error(f"{e} Waiting for 5 seconds")
                await asyncio.sleep(5)
                continue

            except KeyboardInterrupt:
                raise

            except Exception as e:
                logger.error(f"{e} Waiting for 5 seconds")
                await asyncio.sleep(5)
                continue

    async def normal_beep(self, repeat) -> None:
        try:
            await asyncio.to_thread(self._device.normal_beep, repeat)

        except IOError as io_error:
            logger.warning("Device beeping failed due to: " + str(io_error))

        except Exception as e:
            logger.error(f"UNHANDLED ERROR in beeping {e}")
            raise

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

        except Exception as e:
            logger.error(f"UNHANDLED ERROR in beeping {e}")
            raise

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
