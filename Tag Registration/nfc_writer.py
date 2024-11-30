import time
import logging
import nfc
import ndef

# Create a logger for this module
logger = logging.getLogger(__name__)


class NFCReaderWriterDevice:
    """
    Class that represents the actual NFC reader device hardware

    Provides methods for reading/writing tags, buzzing and turning on leds.

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

    def write_tag(self, text: str) -> bool:
        """
        Write text to first tag that is detected
        :param text:
        :return: success boolean
        """
        self.normal_beep()
        try:
            while True:
                tag = self.find_tag()
                if tag:
                    logger.debug("Valid tag found")
                    if tag.ndef is not None:
                        print("WRITING " + text)
                        try:
                            # Write a new record
                            tag.ndef.records = [ndef.TextRecord(text)]

                            self.normal_beep()
                            return True

                        except nfc.tag.TagCommandError as e:
                            print("Retry", e)

        except KeyboardInterrupt:
            return False

    def normal_beep(self, repeat=1):
        for i in range(repeat):
            self._clf.device.turn_on_led_and_buzzer()
            time.sleep(0.1)
            self._clf.device.turn_off_led_and_buzzer()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

