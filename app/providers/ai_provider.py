from abc import ABC, abstractmethod
from app.models.character import Character
from app.models.message import Message

class AIProvider(ABC):
    """
    Abstract interface enforcing the Dependency Inversion Principle (DIP).
    Ensures that our business logic layers do not directly bind to specific cloud SDKs.
    """
    @abstractmethod
    def generate_reply(self, character: Character, optimized_history: list[Message], language: str = "hi") -> str:
        """
        Processes an optimized, context-built message log array to return a 
        personality-consistent text response string from the AI model.
        """
        pass
