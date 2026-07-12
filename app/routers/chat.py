from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.repositories.character_repository import CharacterRepository, CharacterNotFoundError
from app.storage.in_memory_store import InMemorySessionStore
from app.services.conversation_context_builder import ConversationContextBuilder
from app.providers.gemini_provider import GeminiProvider
from app.services.chat_service import ChatService
from app.services.message_splitter import split_into_bubbles
from app.services.rate_limiter import RateLimiter
from app.services.voice_trigger import VoiceTriggerDecider

router = APIRouter(prefix="/api/chat", tags=["Chat Engine"])

# Global application tier dependency singletons
character_repository = CharacterRepository()
session_storage = InMemorySessionStore(max_stored=200)
context_processor = ConversationContextBuilder(target_window_size=8)
ai_engine = GeminiProvider()
rate_guard = RateLimiter(max_requests=12, window_seconds=60)
voice_trigger = VoiceTriggerDecider(probability=0.2)  # ~1-in-5 replies auto-play as voice


def get_chat_service() -> ChatService:
    return ChatService(
        ai_provider=ai_engine,
        session_store=session_storage,
        character_repo=character_repository,
        context_builder=context_processor,
        rate_limiter=rate_guard
    )

class ChatInput(BaseModel):
    session_id: str
    character_id: str
    user_name: str
    text: str
    language: str = "hi"  # "hi" or "en"

@router.get("/history")
async def get_chat_history(
    session_id: str,
    character_id: str,
    service: ChatService = Depends(get_chat_service),
):
    """
    Returns the stored conversation for a given (session_id, character_id) pair
    so the frontend can restore it when a user switches back to a character.
    """
    session_key = f"{session_id}_{character_id}"
    history = service.session_store.get_history(session_key)
    return {
        "messages": [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]
    }

@router.post("/send")
async def send_chat_message(payload: ChatInput, service: ChatService = Depends(get_chat_service)):
    try:
        reply_string = service.handle_message(
            session_id=payload.session_id,
            character_id=payload.character_id,
            user_name=payload.user_name,
            user_text=payload.text,
            language=payload.language
        )

        reply_bubbles = split_into_bubbles(reply_string, max_parts=3)
        return {"status": "success", "reply": reply_string, "reply_bubbles": reply_bubbles, "auto_voice": voice_trigger.should_auto_play()}
        
    except CharacterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal switchboard routing server deadlock.")
