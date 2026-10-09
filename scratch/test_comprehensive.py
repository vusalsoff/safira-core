import requests
import json
import uuid

API_URL = "http://localhost:8000/api"

print("="*50)
print("SAFIRA COMPREHENSIVE E2E VERIFICATION")
print("="*50)

# MODE 1 & 5 & ISOLATION
print("\n--- TEST A: SCIENTIFIC RESEARCH AI ---")
res = requests.post(f"{API_URL}/libraries", json={
    "ai_identity": "Scientific_Research_AI", "name": "Science Library", "description": "Science", "purpose": "Research"
})
lib_sci = res.json()["library_id"]

# Ingest
requests.post(f"{API_URL}/libraries/{lib_sci}/ingest", json={
    "content": "Photosynthesis converts light into chemical energy.", "source_name": "Bio101", "context": "Biology"
})
requests.post(f"{API_URL}/libraries/{lib_sci}/ingest", json={
    "content": "Quantum entanglement links particles across space.", "source_name": "Physics Jnl", "context": "Physics"
})

print(f"Science Lib ID: {lib_sci}")
print("Retrieving science data...")
res = requests.post(f"{API_URL}/libraries/{lib_sci}/retrieve", json={"query": "light energy", "max_results": 2})
print(res.json().get('results', [])[0]['meaning'])


print("\n--- TEST B: GAMING WORLD AI ---")
res = requests.post(f"{API_URL}/libraries", json={
    "ai_identity": "Gaming_World_AI", "name": "Gaming Library", "description": "Games", "purpose": "Lore"
})
lib_game = res.json()["library_id"]

requests.post(f"{API_URL}/libraries/{lib_game}/ingest", json={
    "content": "The Master Sword seals the darkness.", "source_name": "Zelda Lore", "context": "Weapons"
})
requests.post(f"{API_URL}/libraries/{lib_game}/ingest", json={
    "content": "Hyrule is a kingdom created by golden goddesses.", "source_name": "Zelda Lore", "context": "Locations"
})
print(f"Gaming Lib ID: {lib_game}")

print("\n--- TEST C: ISOLATION ---")
# Query Gaming library for 'light energy' (which is in Science). Should return nothing or low score, certainly not the science record.
res = requests.post(f"{API_URL}/libraries/{lib_game}/retrieve", json={"query": "light energy photosynthesis", "max_results": 2})
leaked = [r for r in res.json().get('results', []) if 'Photosynthesis' in r['meaning']]
print(f"Cross-library leakage detected: {len(leaked) > 0}")

print("\n--- TEST D: RECONSTRUCTION ---")
# Dry run reconstruct on Gaming library
res = requests.post(f"{API_URL}/libraries/{lib_game}/reconstruct", json={
    "guidance": "Group all Zelda lore under a 'Zelda Franchise' category.",
    "dry_run": True
})
print("Reconstruct proposed changes keys:", list(res.json().get('proposed_changes', {}).keys()))

print("\n--- TEST E: SEMANTIC GUARDIAN ---")
res = requests.post("http://localhost:8000/api/semantic/analyze", json={
    "text_a": "Employees must work in the office exactly three days per week.",
    "text_b": "Employees must work in the office at least three days per week."
})
data = res.json()
print("Equivalent:", data.get('are_equivalent'))
print("Contradiction:", data.get('contradiction_detected'))
print("Differences:", data.get('differences_noted'))

print("\n--- TEST F: RELATION ENGINE ---")
res = requests.get(f"{API_URL}/libraries/{lib_game}/relations")
relations = res.json().get('relations', [])
print(f"Relations found: {len(relations)}")
for r in relations:
    print(f" - {r['relation_type']} between {r['source_id']} and {r['target_id']}")

