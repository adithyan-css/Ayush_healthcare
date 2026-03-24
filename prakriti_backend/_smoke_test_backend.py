import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

email = f"test_{uuid.uuid4().hex[:8]}@example.com"
password = "StrongPass123!"

register_payload = {
    "email": email,
    "password": password,
    "display_name": "Test User",
    "language": "en"
}

r1 = client.post('/api/v1/auth/register', json=register_payload)
print('register', r1.status_code)
if r1.status_code not in (200, 201):
    print(r1.text)
    raise SystemExit(1)

login_payload = {"email": email, "password": password}
r2 = client.post('/api/v1/auth/login', json=login_payload)
print('login', r2.status_code)
if r2.status_code != 200:
    print(r2.text)
    raise SystemExit(1)

tokens = r2.json()
access_token = tokens['access_token']
headers = {"Authorization": f"Bearer {access_token}"}

r3 = client.get('/api/v1/auth/me', headers=headers)
print('me', r3.status_code)
if r3.status_code != 200:
    print(r3.text)
    raise SystemExit(1)

profile_payload = {
    "vata_score": 36,
    "pitta_score": 28,
    "kapha_score": 22,
    "dominant_dosha": "vata",
    "risk_score": 0
}
r4 = client.post('/api/v1/prakriti/profile', json=profile_payload, headers=headers)
print('prakriti_profile_create', r4.status_code)
if r4.status_code != 200:
    print(r4.text)
    raise SystemExit(1)

rec_payload = {
    "symptoms": ["anxiety", "dryness"],
    "free_text": "sleep disturbance",
    "variation": False
}
r5 = client.post('/api/v1/recommendations/generate', json=rec_payload, headers=headers)
print('recommend_generate', r5.status_code)
if r5.status_code != 200:
    print(r5.text)
    raise SystemExit(1)

r6 = client.get('/api/v1/recommendations/history', headers=headers)
print('recommend_history', r6.status_code)
if r6.status_code != 200:
    print(r6.text)
    raise SystemExit(1)

print('smoke_ok')
