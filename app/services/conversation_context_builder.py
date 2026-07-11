import logging
from app.models.message import Message

logger = logging.getLogger("cc_switchboard")

class ConversationContextBuilder:
    """
    Domain service responsible for filtering down a master conversation log thread 
    into a smart context payload slice optimized for the Gemini API.
    """
    def __init__(self, target_window_size: int = 8):
        self.target_window_size = target_window_size

    def build_payload(self, full_history: list[Message]) -> list[Message]:
        # Case A: Conversation is fresh, return everything directly
        if len(full_history) <= self.target_window_size:
            return list(full_history)

        # Case B: Thread exceeds target window. Slice recent messages
        recent_messages = full_history[-self.target_window_size:]
        evicted_messages = full_history[:-self.target_window_size]
        
        # Calculate metric attributes for the summary briefing note
        user_joke_responses = sum(1 for msg in evicted_messages if msg.role == "user")
        
        # Extract the character's last 3 spoken lines to prevent repetition (Problem 5)
        topic_snippets = [
            msg.content[:50] for msg in evicted_messages if msg.role == "character"
        ][-3:]

        # Compile the context note instruction payload string
        summary_directive = (
            f"[CONTEXT NOTE: Earlier in this chat, you already said: "
            f"{'; '.join(topic_snippets) if topic_snippets else 'general small talk'}. "
            f"The user has replied {user_joke_responses} times since then. "
            f"Do NOT repeat these punchlines — continue naturally from the recent messages below.]"
        )
        
        # Injected as "user" to prevent confusing Gemini's dialogue role mapping
        synthetic_context = [
            Message(role="user", content=summary_directive)
        ] + recent_messages

        logger.info(f"Context builder successfully generated an optimized payload slice from {len(full_history)} historic turns.")
        return synthetic_context
