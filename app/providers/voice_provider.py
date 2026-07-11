from abc import ABC, abstractmethod

class VoiceProvider(ABC):
    """
    Abstract Base Class enforcing the Dependency Inversion Principle (DIP).
    Ensures that our application logic layer interacts with abstract contracts 
    rather than a specific audio synthesis SDK.
    """
    @abstractmethod
    def synthesize(self, text: str, voice_id: str) -> bytes:
        """
        Synthesizes a text string into playable raw audio bytes 
        using a specific character voice profile ID.
        """
        pass
