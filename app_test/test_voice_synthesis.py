"""
Run with: python -m app_test.test_voice_synthesis
Generates one real audio sample per character using actual in-character
Hinglish lines — NOT English filler text — so we can judge real pronunciation
quality before trusting any voice pick.
"""
from app.repositories.character_repository import CharacterRepository
from app.providers.elevenlabs_provider import ElevenLabsProvider

print("================ PHASE 5 VOICE SYNTHESIS PRONUNCIATION TEST ================")

repo = CharacterRepository()
voice_provider = ElevenLabsProvider()

# Real Hinglish lines per character, matching their actual comedic style
test_lines = {
    "gullu": "Nahi, theek hai, kitni madad karu. Problem mera haath se solve karna ka liya?",
    "sohail": "Accha, Delhi jaa rahi ho? Kitne dino ke liye? Pata nahi? Relative hai kya wahan?",
    "zaid": "Iska bhi jugaad hai bhai, bas thoda idhar-udhar karna hai, ho jayega!",
}

for character_id, line in test_lines.items():
    character = repo.get(character_id)

    if not character.voice_id:
        print(f"\n -> SKIPPED: {character.name} has no voice_id configured.")
        continue

    print(f"\n -> Synthesizing for {character.name} (voice_id={character.voice_id})")
    print(f"    Text: \"{line}\"")

    try:
        audio_bytes = voice_provider.synthesize(text=line, voice_id=character.voice_id)
        output_path = f"app_test/voice_samples/{character_id}_sample.mp3"
        import os
        os.makedirs("app_test/voice_samples", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"    -> SUCCESS: saved to {output_path} ({len(audio_bytes)} bytes)")
    except Exception as e:
        print(f"    -> FAILED: {e}")

print("\n================================================================")
print("Play each mp3 in app_test/voice_samples/ and listen for Hinglish pronunciation quality.")
print("=========================================================================")