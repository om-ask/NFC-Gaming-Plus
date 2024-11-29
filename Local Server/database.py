import aiosqlite

class PointsRepo:
    """
    A class to interact with an SQLite database to manage user points and visits.

    This class provides methods to add users, retrieve user points, add points,
    check if a user has visited a specific place, and close the database connection.
    """

    def __init__(self, dbPath):
        """
        Initializes the PointsRepo class with the path to the SQLite database.
        Args:
            dbPath (str): The file path to the SQLite database.
        """
        self.dbPath = dbPath
        self.db = None  # Database connection

    async def connect(self):
        """
        Establishes a connection to the SQLite database.
        """
        self.db = await aiosqlite.connect(self.dbPath)
        # await self.db.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign keys are enabled

    async def addVisitor(self, visitorId: str) -> None:
        """
        Adds a new user to the database.
        Args:
            userId (str): The unique identifier for the user to be added.
        """
        async with self.db.execute("INSERT OR IGNORE INTO Visitor (visitor_id) VALUES (?)", (visitorId,)) as cursor:
            await self.db.commit()

    async def addQuest(self, questId: str, points: int) -> None:
        """
        Adds a place to the database.
        Args:
            placeId (str): The unique identifier for the place.
            points (int): The points for visiting the place.
        """
        async with self.db.execute("INSERT OR IGNORE INTO Quest (quest_id, points_visiting_now) VALUES (?, ?)", (questId, points)) as cursor:
            await self.db.commit()

    async def getVisitorPoints(self, visitorId: str) -> int:
        """
        Retrieves the total points of a user.
        Args:
            userId (str): The unique identifier for the user.
        Returns:
            int: The total points of the user.
        """
        async with self.db.execute("SELECT SUM(points) FROM PointRecords WHERE visitor_id = ?", (visitorId,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] is not None else None

    async def addRecord(self, visitorId: str, questId: str, points: int) -> None:
        """
        Adds points for a user after visiting a place.
        Args:
            userId (str): The unique identifier for the user.
            placeId (str): The unique identifier for the place.
            points (int): The points to add.
        """
        async with self.db.execute(
            "INSERT INTO PointRecords (visitor_id, quest_id, points) VALUES (?, ?, ?)", 
            (visitorId, questId, points)
        ) as cursor:
            await self.db.commit()

    async def getQuestPoints(self, questId: str) -> int:
        """
        Retrieves the points associated with a place.
        Args:
            placeId (str): The unique identifier for the place.
        Returns:
            int: The points of the place.
        """
        async with self.db.execute("SELECT points_visiting_now FROM Quest WHERE quest_id = ?", (questId,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def close(self):
        """
        Closes the database connection.
        """
        if self.db:
            await self.db.close()


# Example usage and testing
async def test():
    repo = PointsRepo("database.db")
    await repo.connect()

    # Add users
    await repo.addVisitor("user1")
    await repo.addVisitor("user2")
    await repo.addVisitor("user3")

    # Add places
    await repo.addQuest("place1", 10)
    await repo.addQuest("place2", 20)
    await repo.addQuest("place3", 30)

    # # Add visits and points
    # await repo.addUserPoints("user1", "place1", 10)
    # await repo.addUserPoints("user2", "place1", 10)
    # await repo.addUserPoints("user2", "place2", 20)
    # await repo.addUserPoints("user3", "place3", 30)

    # Retrieve data
    # print("____________________________ONE")
    # print(await repo.getUserPoints("user2sdf"))  # Expected: 30
    # print("____________________________TWO")
    # print(await repo.getPlacePoints("place1"))  # Expected: 10
    # print("____________________________THREE")

    # Close the database connection
    await repo.close()

# Run the test
if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
