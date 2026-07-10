from abc import ABC, abstractmethod
from app.models.message import Message

class SessionStore(ABC):
    """
    Abstact interface for managing chat history tracks.
    Enforces SOLID compliance so we can switch to a database later without changes upstream.
    """
    @abstractmethod
    def get_history(self, session_key: str) -> list[Message]:
        """Retrieve the historical message logs for a specific session channel."""
        pass

    @abstractmethod
    def append_message(self, session_key: str, message: Message) -> None:
        """Append a validated message into the session channel's history path."""
        pass