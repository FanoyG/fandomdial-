from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.repositories.character_repository import CharacterRepository, CharacterNotFoundError
from app.storage.in_memory_store import InMemorySessionStore
from app.services.conversation_context_builder import ConversationContextBuilder
from app.providers.gemini_provider import GeminiProvider
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat Engine"])

# Global application tier dependency singletons
character_repository = CharacterRepository()
session_storage = InMemorySessionStore(max_stored=200)
context_processor = ConversationContextBuilder(target_window_size=8)
ai_engine = GeminiProvider()

def get_chat_service() -> ChatService:
    return ChatService(
        ai_provider=ai_engine,
        session_store=session_storage,
        character_repo=character_repository,
        context_builder=context_processor
    )

class ChatInput(BaseModel):
    session_id: str
    character_id: str
    user_name: str
    text: str

@router.post("/send")
async def send_chat_message(payload: ChatInput, service: ChatService = Depends(get_chat_service)):
    try:
        reply_string = service.handle_message(
            session_id=payload.session_id,
            character_id=payload.character_id,
            user_name=payload.user_name,
            user_text=payload.text
        )
        return {"status": "success", "reply": reply_string}
        
    except CharacterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal switchboard routing server deadlock.")
