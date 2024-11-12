
class NFCReading:
    """
    Helper class to store a reading from the reader
    Each reading contains a single quest and user id

    The ids are not prefixed or suffixed and are as is once read from the nfc tags
    """
    def __init__(self, quest_id, user_id):
        self.quest_id = quest_id
        self.user_id = user_id
