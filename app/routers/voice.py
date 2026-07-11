from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
import io
from app.repositories.character_repository import CharacterRepository, CharacterNotFoundError
from app.providers.elevenlabs_provider import ElevenLabsProvider, VoiceUnavailableError
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/api/voice", tags=["Voice Engine"])

# Initialize singletons on module initialization scope
character_repository = CharacterRepository()
concrete_provider = ElevenLabsProvider()

def get_voice_service() -> VoiceService:
    return VoiceService(voice_provider=concrete_provider, character_repo=character_repository)

@router.get("/stream")
async def stream_character_voice(
    character_id: str = Query(..., description="Target character ID tracking key"),
    text: str = Query(..., description="Raw text statement context to synthesize"),
    service: VoiceService = Depends(get_voice_service)
):
    """
    Accepts text strings via GET queries, runs synthesis using VoiceService,
    and returns a buffered binary audio stream directly back to the browser window.
    """
    try:
        # Coordinate transactions through our newly built service layer class
        audio_bytes = service.generate_voice_stream(character_id=character_id, text_to_speak=text)
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")

    except CharacterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except VoiceUnavailableError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="The audio streaming hub experienced a network routing fault.")
