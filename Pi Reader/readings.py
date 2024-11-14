import enum
from typing import Self


class User:
    """
    Helper class to store and create Users from tag readings
    Each user has a user id

    The id alone is not prefixed or suffixed by anything

    To

    To generate a correctly prefixed user id reading for publishing,
    convert the User into a string or use the .message() method
    """
    # Message format for publishing
    USER_MESSAGE_FORMAT = "USER%s"

    def __init__(self, user_id: str):
        self._user_id = user_id

    @classmethod
    def user_from_tag(cls, tag_text: str) -> Self:
        return cls(tag_text[4:])

    @property
    def user_id(self) -> str:
        return self._user_id

    def message(self) -> str:
        """
        Format the user id string and prepare it for messages
        :return: A correctly formatted user id for publishing
        """
        return self.USER_MESSAGE_FORMAT % self.user_id

    def __str__(self) -> str:
        return self.message()

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False

        return other.user_id == self.user_id

    def __hash__(self):
        return hash(self.user_id)


class Quest:
    """
    Helper class to store and create Quests from quest card readings
    Each quest has a quest id and a user set

    The id alone is not prefixed or suffixed by anything

    To

    To generate a correctly prefixed quest id reading for publishing,
    convert the Quest into a string or use the .message() method
    """
    # Message format for publishing
    QUEST_MESSAGE_FORMAT = "QUEST%s"

    def __init__(self, quest_id: str, one_time:bool=False):
        self._quest_id = quest_id
        self._one_time = one_time
        self._quest_user_log: set[User] = set()
    
    @classmethod
    def quest_from_card(cls, card_text: str) -> Self:
        # TODO Handle special quests
        return cls(card_text[5:])

    @property
    def quest_id(self) -> str:
        return self._quest_id

    @property
    def one_time(self) -> bool:
        return self._one_time

    def message(self) -> str:
        """
        Format the quest id string and prepare it for messages
        :return: A correctly formatted quest id for publishing
        """
        return self.QUEST_MESSAGE_FORMAT % self.quest_id

    def record_user(self, user: User) -> bool:
        if user in self._quest_user_log:
            return False

        self._quest_user_log.add(user)
        return True
    
    def __str__(self) -> str:
        return self.message()

    def __eq__(self, other):
        if not isinstance(other, Quest):
            return False

        return other.quest_id == self.quest_id and other.one_time == self.one_time


class NFCReading:
    """
    Helper class to store a normal reading from the reader
    Each reading contains a single quest and user id

    The ids are not prefixed or suffixed by anything
    
    To generate a correctly prefixed quest or user id reading for publishing,
    use quest_string() and .user_string() respectively 
    """
    def __init__(self, quest: Quest, user: User):
        self._quest = quest
        self._user = user

    @property
    def quest_id(self):
        return self._quest.quest_id

    @property
    def user_id(self):
        return self._user.user_id
    
    def quest_string(self) -> str:
        return str(self._quest)
    
    def user_string(self) -> str:
        return str(self._user)
        


class TagType(enum.Enum):
    QUEST = "Q"
    USER= "U"
    INVALID = "I"

    @classmethod
    def tag_type(cls, string:str) -> Self:
        if string.startswith("QUEST") and len(string) > 5:
            return cls.QUEST
        elif string.startswith("USER") and len(string) > 4:
            return cls.USER
        else:
            return cls.INVALID
