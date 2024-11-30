
from database import PointsRepo
async def main():
    repo = PointsRepo("database.db")
    flag = True
    with flag:
        questId = input("Enter the quest ID: ")
        questName = input("Enter the quest name: ")
        points = int(input("Enter the points for visiting the quest: "))
        try:
            await repo.addQuest(questId, questName, points)
            print("Quest added successfully.")
            print("=====================================================")
        except Exception as e:
            print(f"An error occurred: {e}")
             
        
        