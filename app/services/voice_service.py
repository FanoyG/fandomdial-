import logging
from app.repositories.character_repository import CharacterRepository
from app.providers.voice_provider import VoiceProvider

logger = logging.getLogger("cc_switchboard")

class VoiceService:
    def __init__(self, voice_provider: VoiceProvider, character_repo: CharacterRepository):
        """
        Orchestration layer managing voice processing pipelines.
        Dependencies injected cleanly via abstract contracts (DIP).
        """
        self.voice_provider = voice_provider
        self.character_repo = character_repo

    def generate_voice_stream(self, character_id: str, text_to_speak: str) -> bytes:
        if not text_to_speak or not text_to_speak.strip():
            raise ValueError("Audio creation rejected: Input text context is completely blank.")

        # 1. Fetch character data to locate their active voice configurations profile
        character = self.character_repo.get(character_id)

        # 2. Check if the voice calling capability is active for this persona profile boundary
        if not character.voice_id:
            logger.warning(f"Voice call button triggered for unconfigured character line profile: {character_id}")
            raise ValueError(f"Voice synthesis unavailable: Character '{character_id}' has no assigned voice_id profile.")

        logger.info(f"VoiceService coordinating audio turnaround pipeline for character: {character_id}")
        
        # 3. Route parameters straight into our decoupled voice provider architecture
        audio_payload_bytes = self.voice_provider.synthesize(text=text_to_speak, voice_id=character.voice_id)
        return audio_payload_bytes
