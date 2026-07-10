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
        # Case A: Conversation is fresh, return everything without modification
        if len(full_history) <= self.target_window_size:
            return list(full_history)

        # Case B: Thread exceeds target window. Slice recent messages
        recent_messages = full_history[-self.target_window_size:]
        
        # Calculate messages dropped behind the window track
        evicted_messages = full_history[:-self.target_window_size]
        
        # Analyze historical traits to build an implicit tracking summary directive injection 
        character_joke_count = 0
        user_joke_responses = 0
        
        # Simple metadata processing calculation to stop repetitive jokes loop (Problem 5)
        for msg in evicted_messages:
            if msg.role == "character":
                character_joke_count += 1
            else:
                user_joke_responses += 1

        # Craft a structural catch-up summarization briefing context instruction message
        summary_directive = (
            f"[SYSTEM BRIEFING NOTE: This conversation is ongoing. In the older dropped part of this chat, "
            f"you have already delivered approximately {character_joke_count} jokes/roasts, and the user has responded "
            f"to them {user_joke_responses} times. Acknowledge this context naturally—DO NOT repeat previous punchlines "
            f"or loop back to the same opening jokes. Continue the dialogue fluently using the recent flow below.]"
        )
        
        # Construct the synthetic context array injected directly on front of the processing stream window
        synthetic_context = [
            Message(role="character", content=summary_directive)
        ] + recent_messages

        logger.info(f"Context builder condensed history down from {len(full_history)} items into a smart optimized slice window.")
        return synthetic_context