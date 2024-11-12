# points repo 

class PointsRepo:
    """
    A class to interact with an SQLite database to manage user points and visits.

    This class provides methods to add users, retrieve user points, add points,
    check if a user has visited a specific place, and close the database connection.

    Attributes:
        dbPath (str): The file path to the SQLite database used for storing user points and visits.

    Methods:
        connect() -> None:
            Establishes a connection to the SQLite database.

        addUser(userId: str) -> None:
            Adds a new user to the database.

        getUserPoints(userId: str) -> int:
            Retrieves the current point balance for the specified user.

        addUserPoints(userId: str, readerId: str, points: int) -> None:
            Adds points to a user's account after a visit to a specific place.

        hasUserVisitedPlace(userId: str, readerId: str) -> bool:
            Checks whether the specified user has visited a particular place (represented by `readerId`).

        close() -> None:
            Closes the connection to the SQLite database.
    """
    
    def __init__(self, dbPath):
        """
        Initializes the PointsRepo class with the path to the SQLite database.

        Args:
            dbPath (str): The file path to the SQLite database.
        """
        self.dbPath = dbPath
    
    def connect(self):
        """
        Establishes a connection to the SQLite database.

        This method should be called before performing any operations on the database.
        
        Returns:
            None
        
        Raises:
            sqlite3.DatabaseError: If the connection to the database cannot be established.
        """
        pass
    
    def addUser(self, userId: str) -> None: 
        """
        Adds a new user to the database.

        If the user already exists, this method should handle the situation
        by not adding the user again.

        Args:
            userId (str): The unique identifier for the user to be added.

        Returns:
            None
        
        """
        pass
    
    def getUserPoints(self, userId) -> int:
        """
        Retrieves the current total points for the specified user.

        Args:
            userId (str): The unique identifier for the user whose points are to be retrieved.

        Returns:
            int: The current point balance for the user.
        """
        pass
    
    def addUserPoints(self, userId, readerId, points) -> None:
        """
        Adds points to a user's account after they visit a specific place.

        This method updates the user's point balance in the database by adding
        the specified number of points given they have not visited the place before.

        Args:
            userId (str): The unique identifier for the user to whom the points will be added.
            readerId (str): The unique identifier for the place the user visited.
            points (int): The number of points to be added to the user's account.

        Returns:
            None
        """
        pass
    
    def hasUserVisitedPlace(self, userId, readerId) -> bool:
        """
         Checks whether the specified user has visited a particular place.

        This method checks if there is a record of the user visiting the specified
        place (represented by `readerId`) in the database.

        Args:
            userId (str): The unique identifier for the user.
            readerId (str): The unique identifier for the place to check.

        Returns:
            bool: `True` if the user has visited the place, `False` otherwise.
        
        Raises:
            sqlite3.DatabaseError: If there is an issue querying the database.
        """
        pass
    
    """
        Closes the connection to the SQLite database.

        This method should be called once all database operations have been completed
        to ensure that resources are properly released.

        Returns:
            None
    """
    def getPlacePoints(self, placeId: str) -> int:
        pass
    
    def close(self) -> None:
        pass
    