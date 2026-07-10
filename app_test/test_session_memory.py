from app.storage.in_memory_store import InMemorySessionStore
from app.services.conversation_context_builder import ConversationContextBuilder
from app.models.message import Message

print("================ EXECUTING ADAPTIVE PHASE 2 VALIDATION ================")

# 1. Initialize our decoupled components
master_vault = InMemorySessionStore(max_stored=200)
context_processor = ConversationContextBuilder(target_window_size=4)
session_key = "user_adil_dex_turn"

print("\n[Test 1] Simulating heavy conversation loop (10 user/character message turns)...")
for i in range(1, 6):
    master_vault.append_message(session_key, Message(role="user", content=f"User phrase query variant index #{i}"))
    master_vault.append_message(session_key, Message(role="character", content=f"Character punchline response variant index #{i}"))

# 2. Check preservation safety inside master data vault storage layer
saved_history = master_vault.get_history(session_key)
print(f" -> Preservation Vault Storage Check: Total elements saved = {len(saved_history)} (Expected: 10)")

# 3. Process the identical tracking data through our sliding window engine for Gemini payload packaging
gemini_payload = context_processor.build_payload(saved_history)
print(f" -> AI Switchboard Pipeline Check: Sliced Window Element Array Size = {len(gemini_payload)} (Expected: 5 -> 1 summary + 4 active items)")

print("\nInspecting the structured Gemini processing token string pack array layout:")
for index, element in enumerate(gemini_payload):
    print(f"   Slot {index+1} [{element.role}]: {element.content[:85]}...")

if len(saved_history) == 10 and len(gemini_payload) == 5 and "SYSTEM BRIEFING NOTE" in gemini_payload[0].content:
    print("\n -> SUCCESS: Phase 2 Decoupled Session Memory Engine completely verified!")
else:
    print("\n -> FAILURE: Context window sizing metadata mismatch detected inside execution track.")
print("=======================================================================")
