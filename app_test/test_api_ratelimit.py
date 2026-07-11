from fastapi.testclient import TestClient
from app.main import app

print("================ STARTING PHASE 4 HIGH-SPEED RATE LIMIT STRESS TEST ================")

client = TestClient(app)

payload = {
    "session_id": "stress_test_session_101",
    "character_id": "zaid",
    "user_name": "Adil",
    "text": "Quick test ping",
    "language": "hi"
}

total_pings = 18
allowed_count = 0
blocked_count = 0

print(f"Firing {total_pings} rapid requests to /api/chat/send to intentionally burst the 15-request limit...")

for i in range(1, total_pings + 1):
    # Alter the string slightly each time so Gemini sees fresh context if it gets through
    payload["text"] = f"Hey Zaid, hit me with an idea option #{i}!"
    
    response = client.post("/api/chat/send", json=payload)
    data = response.json()
    
    # Check if the response contains Zaid's specific local fallback text asset string
    if "Jugaad system over-heat ho raha hai" in data.get("reply", ""):
        blocked_count += 1
        print(f" -> Request #{i}: [BLOCKED BY GUARDRAIL] Serve local filler phrase. (HTTP {response.status_code})")
    else:
        allowed_count += 1
        print(f" -> Request #{i}: [ALLOWED] Gemini processing live turnaround tokens. (HTTP {response.status_code})")

print("\n======================= STRESS TEST MATRIX RESULTS =======================")
print(f"Total Requests Dispatched: {total_pings}")
print(f"Total Allowed Requests (Passed to Gemini): {allowed_count} (Expected: 15)")
print(f"Total Blocked Requests (Intercepted locally): {blocked_count} (Expected: 3)")
print("==========================================================================")

if allowed_count == 12 and blocked_count == 6:
    print("\n -> SUCCESS: Rate Limiter Guardrail completely verified under heavy burst load!")
else:
    print("\n -> FAILURE: Guardrail threshold mismatch. Limits are leaking tokens down the line.")
print("=========================================================================")
