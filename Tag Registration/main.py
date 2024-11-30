import requests

def main():

    while True:
        print("SCAN TICKET")
        print()

        # Wait for scan
        ticket = input()

        if not ticket:
            print()
            print("Could not scan ticket")
            continue

        # Send request to api





if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            raise
        except Exception:
            continue
