from fastapi.testclient import TestClient
from app.main import app

print("================ STARTING PHASE 4 API ENDPOINT CHECK ================")

client = TestClient(app)

# 1. Verify basic routing server operational health status
health_check = client.get("/health")
print(f" -> System Health Ping Status: {health_check.status_code} (Expected: 200)")

# 2. Fire mock JSON data down into our active API route endpoint
payload = {
    "session_id": "hackathon_test_session_99",
    "character_id": "sachiv_ji",
    "user_name": "Adil",
    "text": "Taiyari Babu, humri bakri chori hogyii haa, cctv chal raha haa mandir ka?"
}

print(f"\nDispatching payload via HTTP POST route to /api/chat/send...")
print(f"Testing Character ID: '{payload['character_id']}' (Sachiv Ji)")
print(f"User Input text: '{payload['text']}'")

response = client.post("/api/chat/send", json=payload)

print(f"\n -> Server HTTP response code: {response.status_code} (Expected: 200)")
data = response.json()

print("\n================== LIVE API ROUTER RESPONSE ==================")
print(data)
print("================================================================")

if response.status_code == 200 and data["status"] == "success":
    print("\n -> SUCCESS: Phase 4 Chat API Pipeline verified completely!")
else:
    print("\n -> FAILURE: Router transaction validation failed.")
print("=========================================================================")
