from dataclasses import dataclass, field
from datetime import datetime, timezone

MAX_MESSAGE_LENGTH = 1000  # simple guard against spam/paste attacks


@dataclass
class Message:
    """
    Represents a single turn in a conversation.
    role is "user" or "character" — kept as plain strings for now,
    can be swapped for an Enum later without touching callers.
    """
    role: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.role not in ("user", "character"):
            raise ValueError(f"Invalid role: {self.role}")
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty.")
        if len(self.content) > MAX_MESSAGE_LENGTH:
            self.content = self.content[:MAX_MESSAGE_LENGTH]
