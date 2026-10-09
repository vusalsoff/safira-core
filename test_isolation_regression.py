import os
import sqlite3
import pytest
import json
from fastapi.testclient import TestClient

# Must set before import main
os.environ["SAFIRA_DB_FILE"] = "safira_isolation_test.db"
if os.path.exists("safira_isolation_test.db"):
    os.remove("safira_isolation_test.db")

from main import app
import main

# Mock call_llm_json to inject deterministic payloads
MOCK_PAYLOAD = {}
def mock_call_llm_json(prompt):
    return MOCK_PAYLOAD
main.engine.llm.call_json = mock_call_llm_json

client = TestClient(app)
import hashlib
db = sqlite3.connect(os.environ.get('SAFIRA_DB_FILE', 'safira.db'))
c = db.cursor()
c.execute("INSERT OR IGNORE INTO api_clients (id, api_key_hash, name) VALUES ('test_client', ?, 'test')", (hashlib.sha256(b'test_key').hexdigest(),))
db.commit()
db.close()

original_client = client
class AuthClient:
    def get(self, url, **kwargs):
        headers = kwargs.get('headers', {})
        headers['Authorization'] = 'Bearer test_key'
        kwargs['headers'] = headers
        return original_client.get(url, **kwargs)
    def post(self, url, **kwargs):
        headers = kwargs.get('headers', {})
        headers['Authorization'] = 'Bearer test_key'
        kwargs['headers'] = headers
        return original_client.post(url, **kwargs)

client = AuthClient()

PASS = 0
FAIL = 0
results = []

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}: {detail}")

print("=" * 60)
print("SAFIRA LIBRARY ISOLATION & REGRESSION TEST SUITE")
print("=" * 60)

# Setup Environment
r = client.post("/api/libraries", json={"ai_identity": "LibA", "name": "A", "description": "A", "purpose": "A"})
lib_a = r.json()["library_id"]
r = client.post("/api/libraries", json={"ai_identity": "LibB", "name": "B", "description": "B", "purpose": "B"})
lib_b = r.json()["library_id"]

db = sqlite3.connect("safira_isolation_test.db")
c = db.cursor()

# Manually insert some data into both libraries
rec_a = "rec_A1"; cat_a = "cat_A1"
rec_b = "rec_B1"; cat_b = "cat_B1"

c.execute("INSERT INTO categories (id, library_id, name) VALUES (?, ?, ?)", (cat_a, lib_a, "Cat A"))
c.execute("INSERT INTO records (id, library_id, meaning) VALUES (?, ?, ?)", (rec_a, lib_a, "Rec A"))
c.execute("INSERT INTO record_categories (record_id, category_id) VALUES (?, ?)", (rec_a, cat_a))

c.execute("INSERT INTO categories (id, library_id, name) VALUES (?, ?, ?)", (cat_b, lib_b, "Cat B"))
c.execute("INSERT INTO records (id, library_id, meaning) VALUES (?, ?, ?)", (rec_b, lib_b, "Rec B"))
c.execute("INSERT INTO record_categories (record_id, category_id) VALUES (?, ?)", (rec_b, cat_b))
db.commit()

def verify_lib_b_intact():
    c.execute("SELECT category_id FROM record_categories WHERE record_id=?", (rec_b,))
    res = c.fetchone()
    return res and res[0] == cat_b

# 1. & 2. Cross-library category assignment is rejected (Library A steals Library B's record)
MOCK_PAYLOAD = {
    "record_reassignments": [{"record_id": rec_b, "assign_to_category_ids": [cat_a]}]
}
r = client.post(f"/api/libraries/{lib_a}/reconstruct", json={"guidance": "malicious", "dry_run": False})
check("Cross-library record reassignment rejected", "error" in r.json().get("status", ""), r.json())
check("Library B intact after attack 1", verify_lib_b_intact())

# 3. Cross-library relationships are rejected
MOCK_PAYLOAD = {
    "semantic_relations": [{"source_record_id": rec_a, "target_record_id": rec_b, "relation_type": "SHARES_CONTEXT"}]
}
r = client.post(f"/api/libraries/{lib_a}/reconstruct", json={"guidance": "malicious", "dry_run": False})
check("Cross-library relationship rejected", "error" in r.json().get("status", ""), r.json())

# 4. Cross-library parent category references are rejected
MOCK_PAYLOAD = {
    "category_moves": [{"category_id": cat_a, "new_parent_id": cat_b}]
}
r = client.post(f"/api/libraries/{lib_a}/reconstruct", json={"guidance": "malicious", "dry_run": False})
check("Cross-library parent link rejected", "error" in r.json().get("status", ""), r.json())

# 5. Invalid record/category IDs do not cause partial writes & 6. Rollback works
MOCK_PAYLOAD = {
    "category_renames": [{"category_id": cat_a, "new_name": "Renamed A"}], # Valid operation
    "record_reassignments": [{"record_id": "invalid_id_999", "assign_to_category_ids": [cat_a]}] # Invalid operation
}
r = client.post(f"/api/libraries/{lib_a}/reconstruct", json={"guidance": "malicious", "dry_run": False})
check("Invalid ID causes rollback", "error" in r.json().get("status", ""), r.json())
c.execute("SELECT name FROM categories WHERE id=?", (cat_a,))
check("Transaction rollback prevented partial write", c.fetchone()[0] == "Cat A")

# 7. Valid same-library operations still work
MOCK_PAYLOAD = {
    "category_renames": [{"category_id": cat_a, "new_name": "Valid Rename"}],
    "record_reassignments": [{"record_id": rec_a, "assign_to_category_ids": [cat_a]}],
    "new_categories": [{"temp_id": "t1", "name": "New Cat", "parent_id": None}]
}
r = client.post(f"/api/libraries/{lib_a}/reconstruct", json={"guidance": "valid", "dry_run": False})
check("Valid same-library operation succeeds", r.json().get("status") == "success", r.json())

# 8. Existing library-scoped retrieval remains functional
# Mock get_embedding since retrieval uses it
main.engine.embed.get_embedding = lambda x: [0.1]*3072
c.execute("UPDATE records SET embedding=? WHERE id=?", (json.dumps([0.1]*3072), rec_a))
db.commit()

r = client.post(f"/api/libraries/{lib_a}/retrieve", json={"query": "test"})
check("Library retrieval works", r.status_code == 200 and len(r.json()["results"]) > 0)


print("\n--- SUMMARY ---")
print(f"  PASS: {PASS}")
print(f"  FAIL: {FAIL}")
print("=" * 60)



