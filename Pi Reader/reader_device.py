import logging
import time
import nfc

# Create a logger for this module
logger = logging.getLogger(__name__)


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

        self._clf = nfc.ContactlessFrontend()

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

    def read_tag(self, check=lambda tag: True) -> nfc.tag.Tag:
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

    def normal_beep(self, repeat=1):
        for i in range(repeat):
            self._clf.device.turn_on_led_and_buzzer()
            time.sleep(0.1)
            self._clf.device.turn_off_led_and_buzzer()

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
