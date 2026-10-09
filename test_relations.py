import requests
import json
import uuid

API_URL = "http://localhost:8000/api"

print("1. Creating library...")
res = requests.post(f"{API_URL}/libraries", json={
    "ai_identity": "RelationTest",
    "name": "Relation Logic Library",
    "description": "Test relationships",
    "purpose": "Test"
})
lib_id = res.json()["library_id"]
print(f"Library ID: {lib_id}")

print("2. Ingesting item 1 (Context: 'Magic')...")
res1 = requests.post(f"{API_URL}/libraries/{lib_id}/ingest", json={
    "content": "A wand casts fireballs.",
    "source_name": "Book 1",
    "context": "Magic"
})
print("Result 1:", res1.json())

print("3. Ingesting item 2 (Context: 'Magic') to trigger SHARES_CONTEXT relation...")
res2 = requests.post(f"{API_URL}/libraries/{lib_id}/ingest", json={
    "content": "A staff casts ice storms.",
    "source_name": "Book 2",
    "context": "Magic"
})
print("Result 2:", res2.json())

print("4. Fetching relations...")
rel_res = requests.get(f"{API_URL}/libraries/{lib_id}/relations")
print("Relations API response:")
print(json.dumps(rel_res.json(), indent=2))
