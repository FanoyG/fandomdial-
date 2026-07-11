from app.repositories.character_repository import CharacterRepository
from app.providers.gemini_provider import GeminiProvider
from app.models.message import Message

print("================ STARTING PHASE 3 GEMINI PROVIDER CHECK ================")

try:
    repo = CharacterRepository()
    gemini = GeminiProvider()
    
    # Load your humanized Dex configuration from JSON
    dex = repo.get("dex")
    print(f" -> Successfully loaded data profile for: {dex.name}")
    
    # Build a sample message payload thread to test the model
    test_history = [
        Message(role="user", content="Hey Dex, I am feeling incredibly lazy today and I think I'll skip my run.")
    ]
    
    print(f"\nSending message context to Gemini Engine...")
    print(f"User input content: '{test_history[0].content}'")
    print("Awaiting model response output string...")
    
    # Process turn
    reply = gemini.generate_reply(character=dex, optimized_history=test_history)
    
    print("\n================= DYNAMIC AI RESPONSE ACCESSED =================")
    print(reply)
    print("================================================================")
    print("\n -> SUCCESS: Phase 3 Text Brain verified completely!")
    
except Exception as e:
    print(f"\n -> FAILURE: Execution broken during inference pass check: {str(e)}")
print("=========================================================================")
