import requests

API_KEY = "REDACTED"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "http://localhost:8000/api"

print("--- LIVE TEST ---")

# 1. Create Library
r = requests.post(f"{BASE_URL}/libraries", headers=HEADERS, json={"name": "Live Test", "ai_identity": "Tester", "description": "Testing", "purpose": "Test"})
print(f"Create Library: {r.status_code}")
if r.status_code != 200:
    print(r.text)
    exit(1)
lib_id = r.json()["library_id"]

# 2. Mode 1: Ingest
r = requests.post(f"{BASE_URL}/libraries/{lib_id}/ingest", headers=HEADERS, json={
    "content": "The mitochondria is the powerhouse of the cell.",
    "source_name": "Biology 101",
    "context": ""
})
print(f"Mode 1 Ingest: {r.status_code} {r.json()}")

# 3. Mode 2: Reconstruct (Dry Run)
r = requests.post(f"{BASE_URL}/libraries/{lib_id}/reconstruct", headers=HEADERS, json={"dry_run": True})
print(f"Mode 2 Reconstruct: {r.status_code} {r.json().get('status', r.json())}")

# 4. Mode 3: Semantic Guardian
r = requests.post(f"{BASE_URL}/semantic/analyze", headers=HEADERS, json={
    "text_a": "The dog ran fast.", "text_b": "The canine sprinted quickly."
})
print(f"Mode 3 Semantic Guardian: {r.status_code} {r.json()}")

# 5. Mode 4: Relation Engine
r = requests.get(f"{BASE_URL}/libraries/{lib_id}/relations", headers=HEADERS)
print(f"Mode 4 Relations: {r.status_code} {r.json()}")

# 6. Mode 5: Precision Retrieval
r = requests.post(f"{BASE_URL}/libraries/{lib_id}/retrieve", headers=HEADERS, json={"query": "cell energy powerhouse"})
print(f"Mode 5 Retrieval: {r.status_code} {r.json().get('results', r.json())}")

