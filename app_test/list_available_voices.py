"""
Run with: python -m app_test.list_available_voices
Lists voices actually usable via API on this account/tier —
avoids picking another Voice Library voice that will 402 again.
"""
from elevenlabs.client import ElevenLabs
from app.config import settings

client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

print("================ VOICES AVAILABLE TO THIS ACCOUNT ================")
response = client.voices.search()

for voice in response.voices:
    print(f"  name={voice.name!r:20} voice_id={voice.voice_id}  category={voice.category}")

print("=====================================================================")
print("Pick 3 from this list (any category other than 'Voice Library'/'professional' community shares).")