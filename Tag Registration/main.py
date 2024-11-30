import time

import requests
from nfc_writer import NFCReaderWriterDevice
import os
import emailAPI

api_key = os.getenv("API_KEY")

website_url = "https://gaming.kfupm.org/wp-json"
endpoint = "my-api/v1/register-ticket"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def main():
    nfc_device = NFCReaderWriterDevice()
    with nfc_device as activated_device:
        while True:
            print("SCAN TICKET")
            print()

            # Wait for scan
            ticket = input()

            if not ticket:
                print()
                print("Could not scan ticket")
                continue

            try:
                data = {"ticket_id": ticket}
                response = requests.post(url=f"{website_url}/{endpoint}", json=data, headers=headers)
                print(response.json())
                email = response.json()["email"]
                user_id = response.json()["hash"]

            except requests.RequestException as e:
                print()
                print("Could not connect to server due to \n" + e)
                continue

            except KeyError:
                print()
                print("Could not retrieve email. Please try again")
                continue

            account_profile_page = f"https://gaming.kfupm.org/profile?userID={user_id}"

            success_write = activated_device.write_tag("USER" + email)
            if success_write:
                print()
                print("Successfully written email")

            else:
                print()
                print("Could not write. Please try again")
                continue

            params = {
                "to": email,
                "sender": "Contact@gaming.kfupm.org",
                "subject": "Your account",
                "msg_html": f"<h1>Your account email!</h1><br />{account_profile_page}.",
                "signature": True  # use my account signature
            }
            emailAPI.send_email(params)


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            raise

        except OSError:
            print()
            print("Reconnect Device")
            time.sleep(5)

        except Exception as e:
            print(f"error {e}")
            continue
