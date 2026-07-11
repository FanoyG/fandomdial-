import logging
from elevenlabs.client import ElevenLabs
from app.providers.voice_provider import VoiceProvider
from app.config import settings

logger = logging.getLogger("cc_switchboard")

class VoiceUnavailableError(Exception):
    """Custom exception raised when audio synthesis breaks down or is unconfigured."""
    pass

class ElevenLabsProvider(VoiceProvider):
    def __init__(self):
        if not settings.ELEVENLABS_API_KEY:
            logger.error("ElevenLabsProvider Core Initialization Error: ELEVENLABS_API_KEY environment variable is unconfigured.")
            raise ValueError("ElevenLabsProvider Initialization Exception: Missing valid API key credentials.")
            
        # Initialize using the official ElevenLabs SDK client interface
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    def synthesize(self, text: str, voice_id: str) -> bytes:
        if not voice_id:
            raise VoiceUnavailableError("Voice synthesis rejected: voice_id string is missing or empty.")

        # Quota Protection Guard (Problem 3): Truncate input string to block accidental token draining
        safe_text = text[:300] if len(text) > 300 else text

        try:
            logger.info(f"Dispatching text-to-speech request loop via ElevenLabs for voice_id: {voice_id}")
            
            # Generate the live audio chunk stream
            audio_stream = self.client.text_to_speech.convert(
                text=safe_text,
                voice_id=voice_id,
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128",
            )
            
            # Collapse the dynamic streaming generator block directly into clean binary audio bytes
            audio_bytes = b"".join(chunck for chunck in audio_stream)
            return audio_bytes
            
        except Exception as e:
            logger.error(f"ElevenLabs core synthesis engine failed for voice_id '{voice_id}': {str(e)}")
            raise VoiceUnavailableError(f"Audio switchboard generation layer failure: {str(e)}")
