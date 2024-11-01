import nfc
import ndef
import logging

logger = logging.getLogger(__name__)


def on_connect(tag):
    print("Tag Connected")
    if tag.ndef is not None:
        for record in tag.ndef.records:
            print(record)

        print("CLEARING AND ADDING RECORD")
        try:
            # Write a new record
            tag.ndef.records = [ndef.UriRecord("https://portal.kfupm.edu.sa/")]

        except nfc.tag.TagCommandError as e:
            print("Error", e)

    return True


rdwr_options = {
    # 'targets': ['212F', '424F'],
    'on-connect': on_connect,
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with nfc.ContactlessFrontend("usb") as clf:
        while True:
            result = clf.connect(rdwr=rdwr_options)
            if not result:
                print("Error")
                break
            print("Waiting")

    print("Exit")
