import requests
import os

api_key = os.getenv("API_KEY")
# print(api_key)


class RegistrationEndpointAPI:
    website_url = "https://gaming.kfupm.org/wp-json"
    endpoint = "my-api/v1/register-ticket"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def register_ticket(self, ticket_code: str) -> tuple[str, str]:
        # Prepare data
        data = {"ticket_id": ticket_code}

        # Send data
        response = requests.post(url=f"{self.website_url}/{self.endpoint}", json=data, headers=self.headers)

        # Extract from response
        email = response.json()["email"]
        user_id = response.json()["hash"]

        return email, user_id
