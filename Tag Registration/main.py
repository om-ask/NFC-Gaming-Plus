import time

import requests
from nfc_writer import NFCReaderWriterDevice
import os
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

            # TODO Send request to api
            try:
                data = {"ticket_id": ticket}
                response = requests.post(url=f"{website_url}/{endpoint}", json=data, headers=headers)
                email = response.json()["email"]

            except requests.RequestException as e:
                print()
                print("Could not connect to server due to \n" + e)
                continue

            except KeyError:
                print()
                print("Could not retrieve email. Please try again")
                continue

            print(email)
            # continue

            # email = "omar-ask@outlook.com"

            success_write = activated_device.write_tag("USER"+email)
            if success_write:
                print()
                print("Successfully written email")

            else:
                print()
                print("Could not write. Please try again")


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
