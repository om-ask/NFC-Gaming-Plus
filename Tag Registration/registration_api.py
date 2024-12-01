import requests
import os

api_key = os.getenv("API_KEY")
print(api_key)

website_url = "https://gaming.kfupm.org/wp-json"
endpoint = "my-api/v1/register-ticket"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
