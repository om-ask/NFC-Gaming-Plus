import aiohttp
import logging
import asyncio 

logger = logging.getLogger(__name__)

class APIPoster:
    """
    A class to interact with the remote server API to post data such as attendees and points.

    This class allows communication with the remote server API by sending POST requests. It is designed
    to send the addition of attendees and the allocation of points to users.
    
    Attributes:
        url (str): The base URL of the remote server API.
        apiKey (str): The API key

    * refer to the documentation created by Mr. Omar
    Methods:
        
        
        addPoints(userIdentifier: str, points: int, placeId: str) -> dict:
            Sends a POST request to the API to add points for a user at a specific place.
    """
    
    def __init__(self, url, apiKey):
        self.url = url
        self.apiKey = apiKey
        self.max_retries = 4
        self.retry_delay = 5
        
    async def getTotalPoints(self, userIdentifier):
        pass
    
    async def addPoints(self, userIdentifier, points, questId):
        endpoint = "/my-api/v1/add-point"
        data = {"userIdentifier": userIdentifier, "points": points, "questId": questId}
        async with aiohttp.ClientSession() as session:
            response = await self._post(session, endpoint, data)
            return response
    
    
    
    async def _post(self, session, endpoint, data):
        """
        Helper function to send an asynchronous POST request with retries on failure.
        
        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for making requests.
            endpoint (str): The API endpoint to send the request to.
            data (dict): The data to be sent in the POST request.
        
        Returns:
            dict: The response JSON from the API if successful, None if all retries fail.
        """
        url = f"{self.url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.apiKey}", "Content-Type": "application/json"}

        retries = 0
        while retries < self.max_retries:
            try:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()  # Return JSON response if successful
                    else:
                        logging.error(f"Failed request with status {response.status}")
                        return None  # Return None if status is not 200
            except aiohttp.ClientError as e:
                retries += 1
                logging.error(f"Request failed with error: {e}. Retrying {retries}/{self.max_retries}...")
                if retries < self.max_retries:
                    await asyncio.sleep(self.retry_delay)  # Delay before retrying
                else:
                    logging.error(f"Max retries reached. Giving up.")
                    return None   
                
    async def _get(self, session, endpoint, params=None):
        """
        Helper function to send an asynchronous GET request with retries on failure.
        
        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for making requests.
            endpoint (str): The API endpoint to send the request to.
            params (dict): The parameters to be sent in the GET request (optional).
        
        Returns:
            dict: The response JSON from the API if successful, None if all retries fail.
        """
        url = f"{self.url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.apiKey}"}

        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()  # Return JSON response if successful
                else:
                    logging.error(f"Failed request with status {response.status}")
                    return None  # Return None if status is not 200
        except aiohttp.ClientError as e:
            logging.error(f"Request failed with error: {e}.")
            return None

    async def getTotalPoints(self, userIdentifier):
        """
        Sends a GET request to the API to retrieve the total points for a user.
        
        Args:
            userIdentifier (str): The unique identifier for the user.
        
        Returns:
            dict: The response from the API containing the total points if successful, None if all retries fail.
        """
        params = {"user_Identifier": userIdentifier}

        async with aiohttp.ClientSession() as session:
            return await self._get(session, "/my-api/v1/get-total-points", params)
                
     
        