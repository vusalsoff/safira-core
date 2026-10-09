import os
import sqlite3
import pytest
import json
from fastapi.testclient import TestClient

os.environ["SAFIRA_DB_FILE"] = "safira_retrieval_test.db"
if os.path.exists("safira_retrieval_test.db"):
    os.remove("safira_retrieval_test.db")

from main import app
import main
import hashlib

# Mock LLM for ingestion
main.engine.llm.call_json = lambda x: {
    "categories_assessed": ["cat_test"],
    "new_categories_proposed": [{"name": "Test", "description": "Test"}]
}

client = TestClient(app)

PASS = 0
FAIL = 0
BLOCKED = 0
SKIPPED = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}: {detail}")

print("=" * 60)
print("SAFIRA PRECISION RETRIEVAL TEST SUITE (PHASE 4)")
print("=" * 60)

# Provision Test Client
db = sqlite3.connect("safira_retrieval_test.db")
c = db.cursor()
client_id = "client_retrieval"
api_key = "sk_retrieval"
c.execute("INSERT INTO api_clients (id, api_key_hash, name, is_revoked) VALUES (?, ?, ?, 0)", 
          (client_id, hashlib.sha256(api_key.encode()).hexdigest(), "Test Client"))
db.commit()

headers = {"Authorization": f"Bearer {api_key}"}

# Create Library
r = client.post("/api/libraries", headers=headers, json={"ai_identity": "TestAI", "name": "Test", "description": "Test", "purpose": "Test"})
lib_id = r.json()["library_id"]

# --- Deterministic DB Retrieval Tests (Mocked Embeddings) ---

print("\n--- DETERMINISTIC TESTS ---")
# Insert records directly into DB to test specific cosine similarities
c.execute("INSERT INTO categories (id, library_id, name) VALUES ('cat_dna', ?, 'Biology')", (lib_id,))
c.execute("INSERT INTO categories (id, library_id, name) VALUES ('cat_quantum', ?, 'Physics')", (lib_id,))
c.execute("INSERT INTO categories (id, library_id, name) VALUES ('cat_gaming', ?, 'Gaming')", (lib_id,))

# Insert DNA record
c.execute("INSERT INTO records (id, library_id, original_expression, meaning, embedding) VALUES ('rec_dna', ?, 'DNA', 'DNA meaning', ?)", (lib_id, json.dumps([1.0, 0.0, 0.0])))
c.execute("INSERT INTO record_categories (record_id, category_id) VALUES ('rec_dna', 'cat_dna')")

# Insert Quantum record
c.execute("INSERT INTO records (id, library_id, original_expression, meaning, embedding) VALUES ('rec_quantum', ?, 'Quantum', 'Quantum meaning', ?)", (lib_id, json.dumps([0.0, 1.0, 0.0])))
c.execute("INSERT INTO record_categories (record_id, category_id) VALUES ('rec_quantum', 'cat_quantum')")

# Insert Game record
c.execute("INSERT INTO records (id, library_id, original_expression, meaning, embedding) VALUES ('rec_game', ?, 'Game', 'Game meaning', ?)", (lib_id, json.dumps([0.0, 0.0, 1.0])))
c.execute("INSERT INTO record_categories (record_id, category_id) VALUES ('rec_game', 'cat_gaming')")

# Insert Empty Embedding record
c.execute("INSERT INTO records (id, library_id, original_expression, meaning, embedding) VALUES ('rec_empty', ?, 'Empty', 'Empty meaning', '[]')", (lib_id,))

# Insert NaN/Zero norm record
c.execute("INSERT INTO records (id, library_id, original_expression, meaning, embedding) VALUES ('rec_zero', ?, 'Zero', 'Zero meaning', ?)", (lib_id, json.dumps([0.0, 0.0, 0.0])))

db.commit()

# Temporarily mock get_embedding to return specific vectors
original_get_embedding = main.engine.embed.get_embedding

main.engine.embed.get_embedding = lambda x: [1.0, 0.0, 0.0] if "DNA" in x else ([0.0, 0.0, 1.0] if "Game" in x else [0.0, 1.0, 0.0])

# 1. Correct semantic ranking
r = client.post(f"/api/libraries/{lib_id}/retrieve", headers=headers, json={"query": "DNA query"})
res = r.json()
check("Retrieves DNA record successfully", len(res["results"]) > 0 and res["results"][0]["record_id"] == "rec_dna")
check("Skips zero-norm and empty embeddings", all(item["record_id"] not in ["rec_empty", "rec_zero"] for item in res["results"]))

# 2. Category filtering works
r = client.post(f"/api/libraries/{lib_id}/retrieve", headers=headers, json={"query": "Game", "category_filter": ["cat_gaming"]})
res = r.json()
check("Category filter returns only Game record", len(res["results"]) == 1 and res["results"][0]["record_id"] == "rec_game")

r = client.post(f"/api/libraries/{lib_id}/retrieve", headers=headers, json={"query": "DNA", "category_filter": ["cat_gaming"]})
res = r.json()
check("Category filter blocks DNA record when querying Gaming", len(res["results"]) == 0, str(res))

# 3. Full paths and rich schema
r = client.post(f"/api/libraries/{lib_id}/retrieve", headers=headers, json={"query": "DNA"})
res = r.json()
top = res["results"][0]
check("Schema contains meaning", "meaning" in top)
check("Schema contains categories", "categories" in top and "Biology" in top["categories"][0])
check("Schema contains relevance_score", "relevance_score" in top and top["relevance_score"] == 1.0)
check("Schema contains related_records", "related_records" in top)

# 4. Empty vector rejection (API failure)
main.engine.embed.get_embedding = lambda x: []
r = client.post(f"/api/libraries/{lib_id}/retrieve", headers=headers, json={"query": "DNA"})
check("API failure (empty embedding) produces 502", r.status_code == 502)

# --- Live Gemini Tests ---
print("\n--- LIVE GEMINI TESTS ---")
main.engine.embed.get_embedding = original_get_embedding

try:
    live_emb = main.engine.embed.get_embedding("Test connectivity")
    if not live_emb or len(live_emb) == 0:
        raise Exception("Quota or connectivity failed")
    
    # 5. Live Retrieval
    # We ingest real knowledge
    r = client.post(f"/api/libraries/{lib_id}/ingest", headers=headers, json={"content": "Mitochondria is the powerhouse of the cell.", "source_name": "Biology 101", "context": ""})
    if r.status_code != 200:
        print(f"Ingest failed: {r.json()}")
        
    r = client.post(f"/api/libraries/{lib_id}/retrieve", headers=headers, json={"query": "cell energy"})
    if r.status_code == 200 and len(r.json()["results"]) > 0:
        check("Live Gemini semantic match works", r.json()["results"][0]["meaning"] != "")
    else:
        check("Live Gemini semantic match works", False, f"Status {r.status_code}, Resp {r.json()}")
except Exception as e:
    BLOCKED += 1
    print(f"  [BLOCKED] Live Gemini Tests skipped: {str(e)}")


print("\n--- SUMMARY ---")
print(f"  PASS: {PASS}")
print(f"  FAIL: {FAIL}")
print(f"  BLOCKED: {BLOCKED}")
print("=" * 60)

