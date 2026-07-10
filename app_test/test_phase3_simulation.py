from app.repositories.character_repository import CharacterRepository
from app.providers.gemini_provider import GeminiProvider
from app.models.message import Message

print("================ STARTING EXPANDED 10-MESSAGE PANCHAYAT-MIRZAPUR SIMULATION ================")

try:
    repo = CharacterRepository()
    gemini = GeminiProvider()
    
    # ----------------------------------------------------
    # RUN 1: TESTING SACHIV JI (Panchayat Annoyance Tone)
    # ----------------------------------------------------
    sachiv = repo.get("sachiv_ji")
    print(f"\n📞 CONNECTING LINE: {sachiv.name}...")
    
    sachiv_history = []
    
    user_msg_1 = "Taiyari Babu, humri bakri chori hogyii haa, cctv chal raha haa mandir ka?"
    print(f"User: {user_msg_1}")
    sachiv_history.append(Message(role="user", content=user_msg_1))
    
    reply_1 = gemini.generate_reply(character=sachiv, optimized_history=sachiv_history)
    print(f"Sachiv Ji: {reply_1}")
    sachiv_history.append(Message(role="character", content=reply_1))
    
    user_msg_2 = "Ok"
    print(f"\nUser: {user_msg_2}")
    sachiv_history.append(Message(role="user", content=user_msg_2))
    
    reply_2 = gemini.generate_reply(character=sachiv, optimized_history=sachiv_history)
    print(f"Sachiv Ji: {reply_2}")
    sachiv_history.append(Message(role="character", content=reply_2))

    # ----------------------------------------------------
    # RUN 2: TESTING DR. KRANTI (Clinic Slang Roast)
    # ----------------------------------------------------
    doctor = repo.get("dr_kranti")
    print(f"\n🏥 ENTERING CLINIC: {doctor.name}...")
    
    doc_history = []
    
    user_msg_3 = "Doctor sahib, chowk par 10 chai pi li thi subah se, ab pet me hugni ki samasya ho gayi hai."
    print(f"User: {user_msg_3}")
    doc_history.append(Message(role="user", content=user_msg_3))
    
    reply_3 = gemini.generate_reply(character=doctor, optimized_history=doc_history)
    print(f"Dr. Kranti: {reply_3}")
    doc_history.append(Message(role="character", content=reply_3))

    # ----------------------------------------------------
    # RUN 3: TESTING GATTU BHAIYA (Mirzapur Slow Menace)
    # ----------------------------------------------------
    gattu = repo.get("gattu_bhaiya")
    print(f"\n🔫 DIALING SEAT OF POWER: {gattu.name}...")
    
    gattu_history = []
    
    user_msg_4 = "Gattu Bhaiya, chowk ke ladke hume pareshan kar rahe hain aur moron bol rahe hain."
    print(f"User: {user_msg_4}")
    gattu_history.append(Message(role="user", content=user_msg_4))
    
    reply_4 = gemini.generate_reply(character=gattu, optimized_history=gattu_history)
    print(f"Gattu Bhaiya: {reply_4}")
    gattu_history.append(Message(role="character", content=reply_4))

    user_msg_5 = "Whatever"
    print(f"\nUser: {user_msg_5}")
    gattu_history.append(Message(role="user", content=user_msg_5))
    
    reply_5 = gemini.generate_reply(character=gattu, optimized_history=gattu_history)
    print(f"Gattu Bhaiya: {reply_5}")
    gattu_history.append(Message(role="character", content=reply_5))

    print("\n -> SUCCESS: 10-Message comprehensive multi-universe simulation executed completely!")

except Exception as e:
    print(f"\n -> FAILURE: Simulation loop broke down: {str(e)}")
print("=========================================================================")
