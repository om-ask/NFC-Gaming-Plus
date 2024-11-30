import logging
logger = logging.getLogger(__name__)


class PointsManager:
    """
    A class that manages user visits and point allocations using the PointsRepo.

    The PointsManager interacts with the PointsRepo class to handle business logic
    related to user visits to specific places and the calculation and assignment of points.

    This class is responsible for verifying the existence of users and places, 
    ensuring no duplicate visits, and calculating the points awarded for each visit.

    Attributes:
        PointsRepo (PointsRepo): An instance of the PointsRepo class that manages interactions with the database.

    Methods:
        recordVisit(userId: str, readerId: str) -> None:
            Records a visit by a user to a particular place, checking for validity and awarding points.

        _checkIfUserExists(userId: str) -> bool:
            Checks if the user exists in the PointsRepo database.

        _checkIfReaderExists(readerId: str) -> bool:
            Checks if the reader (place) exists in the PointsRepo database.

        _checkIfVisitExists(userId: str, readerId: str) -> bool:
            Checks if the user has already visited the specified place.

        _calculatePoints(readerId: str) -> int:
            Calculates the points to be awarded for visiting the specified place.

        _addPoints(userId: str, readerId: str, points: int) -> None:
            Adds points to the user's account in the PointsRepo database.
    """
    
    def __init__(self, PointsRepo):
        """
        Initializes the PointsManager with an instance of PointsRepo.

        Args:
            PointsRepo (PointsRepo): The PointsRepo instance to manage user data and database operations.
        """
        self.PointsRepo = PointsRepo
        
    async def recordVisit(self, visitorId, questId):
        """
        Records a visit by a user to a specific place.

        This method first checks if the user and the place exist. Then it ensures that the user
        has not already visited the place. If everything is valid, it calculates and adds points
        to the user's account.

        Args:
            userId (str): The unique identifier for the user.
            readerId (str): The unique identifier for the place being visited.

        Returns:
            None
        
        """
        try:
            placePoints = await self._calculatePoints(questId)
            print(questId)
            if (placePoints != None):
                await self._addPoints(visitorId, questId, placePoints)
                return placePoints
            else:
                logger.error("No quest with id: %s", questId)
                return None
        except Exception as e:
            logger.error("Error recording visit: %s", str(e))
            return None
    
    def _checkIfUserExists(self, visitorId):
        """
        Checks if the user exists in the PointsRepo database.

        Args:
            userId (str): The unique identifier for the user.

        Returns:
            bool: `True` if the user exists, `False` otherwise.
        """
        pass
    
    def _checkIfQuestExists(self, questId):
        """
        Checks if the specified place (reader) exists in the PointsRepo database.

        Args:
            readerId (str): The unique identifier for the place.

        Returns:
            bool: `True` if the place exists, `False` otherwise.
        
        """
        pass
    
    def _checkIfVisitExists(self, userId, readerId):
        """
        Checks if a user has already visited a specific place.

        Args:
            userId (str): The unique identifier for the user.
            readerId (str): The unique identifier for the place.

        Returns:
            bool: `True` if the user has already visited the place, `False` otherwise.
        
        """
        pass
    
    async def _calculatePoints(self, questId):
        """
        Calculates the points to be awarded for visiting the specified place.

        This methods calculates the points according to the Game Development committee

        Args:
            readerId (str): The unique identifier for the place being visited.

        Returns:
            int: The number of points to be awarded for the visit.
    
        """
        return await self.PointsRepo.getQuestPoints(questId)
    
    async def _addPoints(self, visitorId, questId, points):
        """
        Adds the calculated points to the user's account in the PointsRepo database.

        Args:
            userId (str): The unique identifier for the user.
            readerId (str): The unique identifier for the place the user visited.
            points (int): The number of points to be added.

        Returns:
            None
        
        """
        await self.PointsRepo.addRecord(visitorId, questId, points)
        