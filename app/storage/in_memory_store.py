from app.storage.session_store import SessionStore
from app.models.message import Message

class InMemorySessionStore(SessionStore):
    """
    Volatile in-memory implementation of SessionStore using a standard Python dict.
    Caps the history queue internally to prevent payload bloat.
    """
    def __init__(self, max_stored: int = 200):
        # Format: {"sessionID_characterID": [Message, Message]}
        self._vault: dict[str, list[Message]] = {}
        self.max_stored = max_stored

    def get_history(self, session_key: str) -> list[Message]:
        # Return a copy of the list so external layers don't accidentally mutate our storage state
        if session_key not in self._vault:
            return []
        return list(self._vault[session_key])

    def append_message(self, session_key: str, message: Message) -> None:
        if session_key not in self._vault:
            self._vault[session_key] = []
            
        self._vault[session_key].append(message)
        
        # Sliding memory window cap protection
        if len(self._vault[session_key]) > self.max_stored:
            self._vault[session_key] = self._vault[session_key][-self.max_stored:]