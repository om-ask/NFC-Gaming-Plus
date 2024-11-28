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
        addAttendee(attendee: dict) -> dict:
            Sends a POST request to the API to add an attendee.
        
        addPoints(userIdentifier: str, points: int, placeId: str) -> dict:
            Sends a POST request to the API to add points for a user at a specific place.
    """
    
    def __init__(self, url, apiKey):
        self.url = url
        self.apiKey = apiKey
        
    def addAttendee(self, attendee):
        pass
    
    def addPoints(self, userIdentifier, points, placeId):
        pass