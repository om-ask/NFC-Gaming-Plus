import enum
from typing import Self


# TODO Document this code

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
