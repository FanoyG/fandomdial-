import logging
from google import genai
from google.genai import types
from app.providers.ai_provider import AIProvider
from app.models.character import Character
from app.models.message import Message
from app.config import settings

logger = logging.getLogger("cc_switchboard")

class GeminiProvider(AIProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.error("GeminiProvider Core Initialization Error: GEMINI_API_KEY environment variable is unconfigured.")
            raise ValueError("GeminiProvider Initialization Exception: Missing valid API key credentials.")
            
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Order of execution models to loop over if one experiences a 503/429 load spike
        self.model_fallback_chain = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]

    def generate_reply(self, character: Character, optimized_history: list[Message]) -> str:
        formatted_contents = []
        for msg in optimized_history:
            gemini_role = "model" if msg.role == "character" else "user"
            formatted_contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )
        # Grab the absolute newest message text from the user
        last_user_message = optimized_history[-1].content if optimized_history else ""
        word_count = len(last_user_message.split())

        # Rule 1: If the input is ultra short (1-2 words), force a single word/sound response
        if word_count <= 2:
            enforcement_suffix = (
                "\n[CRITICAL LENGTH GUARDRAIL: The user sent a tiny phrase. You MUST respond with exactly "
                "ONE single punchy word or local conversational filler sound only. Examples: 'Bhak!', 'Acha?', "
                "'Hatt!', 'Sigh.'. Absolutely no full sentences or explanations allowed.]"
            )
        # Rule 2: If the input is direct hostility or a sharp single sentence, return a crisp 1-line comeback
        elif "moron" in last_user_message.lower() or "idiot" in last_user_message.lower() or word_count <= 6:
            enforcement_suffix = (
                "\n[CRITICAL LENGTH GUARDRAIL: Respond with exactly ONE short, sharp, biting single-sentence line. "
                "Match their energy directly and cut the conversation off cleanly.]"
            )
        # Rule 3: For complex stories, village problems, or riddles, return a full 2-3 sentence humorous response
        else:
            enforcement_suffix = (
                "\n[CRITICAL LENGTH GUARDRAIL: Respond with a full, realistic 2 to 3 sentence humorous conversational paragraph. "
                "Do not look like a corporate robot; stay fully inside your character persona.]"
            )

        # Loop down your resilient fallback chain models
        for model_name in self.model_fallback_chain:
            try:
                logger.info(f"Attempting text inference via model: {model_name} for persona: {character.id}")
                
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=character.system_prompt + enforcement_suffix,
                        temperature=0.82,
                    )
                )
                
                if response.text and response.text.strip():
                    return response.text.strip()
                    
            except Exception as target_error:
                logger.info(f" -> Line busy on model tier '{model_name}'. Re-routing call automatically...")
                continue # Failover target failed, loop to the next option automatically

        # Absolute Fallback Layer (Executed only if all cloud tiers are unavailable)
        logger.error(f"All Gemini API models in the chain are temporarily congested for character '{character.id}'")
        fallbacks = {
            "dex": "Hold on, kid! My trainer is tape-wrapping my knuckles for the next round. Redial in a minute!",
            "circuit": "Main database connection leak detected on deck 4. Patching firmware, hold off on telemetry requests.",
            "uncle_verma": "Acha... listen. The electricity lines in the market are acting up. Let me fix the bulb and get back to you.",
            "rosa": "Oh great, the phone towers are failing just like your sense of humor. Try calling again when the signal bar wakes up!"
        }
        return fallbacks.get(character.id, "The switchboard line is currently facing system network congestion. Please try again shortly.")
