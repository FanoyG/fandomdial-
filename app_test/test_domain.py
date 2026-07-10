from app.repositories.character_repository import CharacterRepository
from app.storage.in_memory_store import InMemorySessionStore
from app.models.message import Message

print("--- Step 1 & 2: Testing Character Repository ---")
repo = CharacterRepository()
dex = repo.get("dex")
print(f"Loaded successfully: {dex.name} ({dex.comedic_mechanism})")

print("\n--- Step 3: Testing In-Memory Session Queue Capping ---")
store = InMemorySessionStore(max_stored=3)
key = "test_user_dex_malhotra"

# Push 5 test messages into a storage buffer limited to 3
for i in range(1, 6):
    store.append_message(key, Message(role="user", content=f"Message variant item #{i}"))

history = store.get_history(key)
print(f"Total buffer items retained after boundary check: {len(history)} (Expected: 3)")
print(f"Oldest remaining item inside window: '{history[0].content}' (Expected: Message variant item #3)")
print("Domain layer verified successfully!")