import logging
from app.models.message import Message
from app.repositories.character_repository import CharacterRepository
from app.storage.session_store import SessionStore
from app.services.conversation_context_builder import ConversationContextBuilder
from app.providers.ai_provider import AIProvider

logger = logging.getLogger("cc_switchboard")

class ChatService:
    def __init__(
        self, 
        ai_provider: AIProvider, 
        session_store: SessionStore, 
        character_repo: CharacterRepository,
        context_builder: ConversationContextBuilder
    ):
        self.ai_provider = ai_provider
        self.session_store = session_store
        self.character_repo = character_repo
        self.context_builder = context_builder

    def handle_message(self, session_id: str, character_id: str, user_name: str, user_text: str) -> str:
        if not user_text or not user_text.strip():
            raise ValueError("Input violation: Message cannot be empty or whitespace.")

        # Fetch character configuration data
        character = self.character_repo.get(character_id)
        session_key = f"{session_id}_{character_id}"

        # Save incoming validated User input into the permanent preservation store
        user_message = Message(role="user", content=f"{user_name}: {user_text}")
        self.session_store.append_message(session_key, user_message)

        # Retrieve full conversation log context and slice it into an optimized window payload
        full_history = self.session_store.get_history(session_key)
        optimized_history = self.context_builder.build_payload(full_history)

        # Dispatch optimized package thread to the fault-tolerant AI Engine
        logger.info(f"ChatService orchestrating reply turnaround for session channel: {session_key}")
        reply_text = self.ai_provider.generate_reply(character, optimized_history)

        # Save generated character response back to the permanent preservation log tray
        char_message = Message(role="character", content=reply_text)
        self.session_store.append_message(session_key, char_message)

        return reply_text
