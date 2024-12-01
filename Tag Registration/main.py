import time

import requests
import usb1

from registration_api import RegistrationEndpointAPI
from nfc_writer import NFCReaderWriterDevice
from emailAPI import RepeatEmailer

# Config Constants
EMAILER_ADDRESS = "Contact@gaming.kfupm.org"
EMAILER_SUBJECT = "NFC Points Profile"

EMAIL_HTML_TEMPLATE = "<h1>Enter this link to view your points!</h1><br />%s."


def register_process(api: RegistrationEndpointAPI, writer: NFCReaderWriterDevice, emailer: RepeatEmailer):
    while True:
        print("-" * 30)
        print("SCAN TICKET")
        print()

        # Wait for scan
        ticket = input()

        if not ticket:
            print()
            print("Could not scan ticket")
            continue

        try:
            email, user_id = api.register_ticket(ticket)

        except requests.RequestException as e:
            print()
            print(f"Could not connect to server due to \n{e}")
            continue

        except KeyError:
            print()
            print("Could not retrieve email. Please try again")
            continue

        print()
        print("Visitor's Email is: " + email)

        print()
        print("Use NFC")

        # Write to tag
        success_write = writer.write_tag("USER" + email)
        if success_write:
            print()
            print(f"Successfully written {email} to tag!")

        else:
            print()
            print("Could not write. Please try again")
            continue

        # Generate account profile page
        account_profile_page = f"https://gaming.kfupm.org/profile?userID={user_id}"

        # Sending email
        print()
        print("Sending profile email")
        # TODO handle exceptions here
        emailer.send_repeat_email(email, account_profile_page)

        print()
        print("REGISTERED!")

        time.sleep(1)


# Outer loop for writer and critical exceptions
def main():
    endpoint_api = RegistrationEndpointAPI()
    nfc_device = NFCReaderWriterDevice()
    repeat_emailer = RepeatEmailer(EMAILER_ADDRESS, EMAILER_SUBJECT, EMAIL_HTML_TEMPLATE)
    while True:
        try:
            with nfc_device:
                # Beep 2 times
                nfc_device.normal_beep(2)

                # Start registering
                register_process(endpoint_api, nfc_device, repeat_emailer)

        except KeyboardInterrupt:
            print("Exiting Program")
            print("-" * 30)
            break

        except (OSError, AttributeError):
            print()
            print("-" * 30)
            print("Please Reconnect Reader Device")
            print()
            time.sleep(1)
            print("Retrying in 5 seconds")

            print()
            for i in range(1, 6):
                print(i)
                time.sleep(1)
            continue

        except usb1.USBError:
            print()
            print("-" * 30)
            print("Please Reconnect NFC to same usb port or restart program!")
            time.sleep(1)
            print("Retrying in 5 seconds")

            print()
            for i in range(1, 6):
                print(i)
                time.sleep(1)
            continue

        except Exception as e:
            print()
            print(f"Unexpected error: {e} \nof type {type(e)}")
            print()
            print("-" * 30)
            print("Retrying")
            continue


# Main
if __name__ == '__main__':
    main()
