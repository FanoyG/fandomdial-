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
            
        last_user_message = optimized_history[-1].content if optimized_history else ""
        word_count = len(last_user_message.split())

        if word_count <= 2:
            enforcement_suffix = (
                "\n[CRITICAL LENGTH GUARDRAIL: The user sent a tiny phrase. You MUST respond with exactly "
                "ONE single punchy word or local conversational filler sound only. Examples: 'Bhak!', 'Acha?', "
                "'Hatt!', 'Sigh.'. Absolutely no full sentences or explanations allowed.]"
            )
        elif word_count <= 6:
            enforcement_suffix = (
                "\n[CRITICAL LENGTH GUARDRAIL: Respond with exactly ONE short, punchy single-sentence line, "
                "fully in character. Let your character's own personality decide the tone naturally based on content.]"
            )
        else:
            enforcement_suffix = (
                "\n[CRITICAL LENGTH GUARDRAIL: Respond with a full, realistic 2 to 3 sentence humorous conversational paragraph. "
                "Do not look like a corporate robot; stay fully inside your character persona.]"
            )

        # FIX: Force character-specific rules to override general guardrails
        enforcement_suffix += (
            "\nIMPORTANT: If this character's own persona above specifies a strict reply length "
            "(for example, always short or always 1-2 sentences), follow that character-specific limit "
            "instead of this general guardrail, even if the guardrail suggests a longer response."
        )

        # Enforce universal comedy engines and block culture locks globally (Problem 2)
        enforcement_suffix += (
            f"\nRely fully on your universal comedic mechanism: '{character.comedic_mechanism}'. "
            "Do not use external copyrighted properties or show titles in your response."
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

        # Terminal Fallback Layer (Updated to support Gullu, Sohail, and Zaid)
        logger.error(f"All Gemini API models in the chain are temporarily congested for character '{character.id}'")
        fallbacks = {
            "gullu": "Nahi, theek hai. Abhi network kharab hai toh kya tower pe chad ke baith jau line clear karne?",
            "sohail": "Arre network down hai bhai! Ticket kab ka hai? Baad me call karna, paise ke alawa sab help karenge.",
            "zaid": "Arre iska bhi jugaad hai bhai! Abhi signal chala gaya hai, do minute me bypass karta hu server, ruko."
        }
        return fallbacks.get(character.id, "The switchboard line is currently facing system network congestion. Please try again shortly.")
