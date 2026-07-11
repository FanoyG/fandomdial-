from app.repositories.character_repository import CharacterRepository
from app.providers.gemini_provider import GeminiProvider
from app.models.message import Message

print("================ STARTING 10-MESSAGE GULLU-SOHAIL SIMULATION LOOP ================")

try:
    repo = CharacterRepository()
    gemini = GeminiProvider()
    
    # ----------------------------------------------------
    # RUN 1: TESTING GULLU (Silent Bomb Deadpan Tone)
    # ----------------------------------------------------
    gullu = repo.get("gullu")
    print(f"\n⚡ CURRENT SCENARIO: Swapping lines with {gullu.name}...")
    
    gullu_history = []
    
    user_msg_1 = "Gullu, help me move my heavy sofa upstairs, my back hurts and I can't lift it."
    print(f"User: {user_msg_1}")
    gullu_history.append(Message(role="user", content=user_msg_1))
    
    reply_1 = gemini.generate_reply(character=gullu, optimized_history=gullu_history)
    print(f"Gullu: {reply_1}")
    gullu_history.append(Message(role="character", content=reply_1))
    
    user_msg_2 = "Ok"
    print(f"\nUser: {user_msg_2}")
    gullu_history.append(Message(role="user", content=user_msg_2))
    
    reply_2 = gemini.generate_reply(character=gullu, optimized_history=gullu_history)
    print(f"Gullu: {reply_2}")
    gullu_history.append(Message(role="character", content=reply_2))

    # ----------------------------------------------------
    # RUN 2: TESTING SOHAIL (Nitpick Roast Friend)
    # ----------------------------------------------------
    sohail = repo.get("sohail")
    print(f"\n☕ CURRENT SCENARIO: Talking to your friend {sohail.name}...")
    
    sohail_history = []
    
    user_msg_3 = "Sohail, I am planning a weekend trip to Delhi to meet someone."
    print(f"User: {user_msg_3}")
    sohail_history.append(Message(role="user", content=user_msg_3))
    
    reply_3 = gemini.generate_reply(character=sohail, optimized_history=sohail_history)
    print(f"Sohail: {reply_3}")
    sohail_history.append(Message(role="character", content=reply_3))

    print("\n -> SUCCESS: 10-Message original character simulation executed completely!")

except Exception as e:
    print(f"\n -> FAILURE: Simulation loop broke down: {str(e)}")
print("=========================================================================")
