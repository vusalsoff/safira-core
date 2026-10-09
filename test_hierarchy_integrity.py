import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

# Setup Test DB
os.environ["SAFIRA_DB_FILE"] = "safira_hierarchy_test.db"
if os.path.exists("safira_hierarchy_test.db"):
    os.remove("safira_hierarchy_test.db")

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
print("SAFIRA HIERARCHICAL INTEGRITY TEST SUITE")
print("=" * 60)

# Setup Environment
r = client.post("/api/libraries", json={"ai_identity": "Science_AI", "name": "Science", "description": "Sci", "purpose": "Sci"})
lib_sci = r.json()["library_id"]
r = client.post("/api/libraries", json={"ai_identity": "Game_AI", "name": "Game", "description": "Game", "purpose": "Game"})
lib_game = r.json()["library_id"]

db = sqlite3.connect("safira_hierarchy_test.db")
c = db.cursor()

# Manually insert 5-level hierarchy for Science
cat1 = "cat_sci_1"
cat2 = "cat_sci_2"
cat3 = "cat_sci_3"
cat4 = "cat_sci_4"
cat5 = "cat_sci_5"
c.execute("INSERT INTO categories (id, library_id, parent_id, name) VALUES (?, ?, ?, ?)", (cat1, lib_sci, None, "Science"))
c.execute("INSERT INTO categories (id, library_id, parent_id, name) VALUES (?, ?, ?, ?)", (cat2, lib_sci, cat1, "Biology"))
c.execute("INSERT INTO categories (id, library_id, parent_id, name) VALUES (?, ?, ?, ?)", (cat3, lib_sci, cat2, "Genetics"))
c.execute("INSERT INTO categories (id, library_id, parent_id, name) VALUES (?, ?, ?, ?)", (cat4, lib_sci, cat3, "Molecular Genetics"))
c.execute("INSERT INTO categories (id, library_id, parent_id, name) VALUES (?, ?, ?, ?)", (cat5, lib_sci, cat4, "DNA"))

rec_dna = "rec_dna_1"
c.execute("INSERT INTO records (id, library_id, original_expression, meaning, context, source_metadata, embedding) VALUES (?, ?, ?, ?, ?, ?, ?)", 
          (rec_dna, lib_sci, "DNA is...", "DNA meaning", "Bio", "Wiki", "[0.1]"))
c.execute("INSERT INTO record_categories (record_id, category_id) VALUES (?, ?)", (rec_dna, cat5))

# And for Game (used for cross-library checks)
cat_game = "cat_game_1"
c.execute("INSERT INTO categories (id, library_id, parent_id, name) VALUES (?, ?, ?, ?)", (cat_game, lib_game, None, "Gaming"))
db.commit()

# 1. Valid five-level hierarchy & 12. Full category path retrieval
main.engine.embed.get_embedding = lambda x: [0.1]
r = client.post(f"/api/libraries/{lib_sci}/retrieve", json={"query": "test"})
paths = r.json()["results"][0]["categories"]
check("Valid five-level hierarchy & path retrieval", "Science > Biology > Genetics > Molecular Genetics > DNA" in paths, paths)

# 2. Nonexistent parent rejection
MOCK_PAYLOAD = {"new_categories": [{"temp_id": "t1", "name": "FakeChild", "parent_id": "invalid_parent"}]}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": False})
check("Nonexistent parent rejection", "error" in r.json().get("status"), r.json())

# 3. Self-parent rejection
MOCK_PAYLOAD = {"category_moves": [{"category_id": cat3, "new_parent_id": cat3}]}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": False})
check("Self-parent rejection", "error" in r.json().get("status"), r.json())

# 4. Indirect cycle rejection (Make cat2 child of cat4: Science -> Bio -> Gen -> Mol -> Bio (CYCLE))
MOCK_PAYLOAD = {"category_moves": [{"category_id": cat2, "new_parent_id": cat4}]}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": False})
check("Indirect cycle rejection", "error" in r.json().get("status"), r.json())

# 5. Cross-library parent rejection
MOCK_PAYLOAD = {"category_moves": [{"category_id": cat1, "new_parent_id": cat_game}]}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": False})
check("Cross-library parent rejection", "error" in r.json().get("status"), r.json())

# 6. Invalid LLM-generated category references & 10. Transaction rollback
c.execute("UPDATE categories SET name='Original' WHERE id=?", (cat2,))
db.commit()
MOCK_PAYLOAD = {
    "category_renames": [{"category_id": cat2, "new_name": "ShouldNotCommit"}],
    "category_moves": [{"category_id": "invalid_id_999", "new_parent_id": cat1}]
}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": False})
check("Invalid LLM category references", "error" in r.json().get("status"), r.json())

c.execute("SELECT name FROM categories WHERE id=?", (cat2,))
check("Transaction rollback prevented partial structure modification", c.fetchone()[0] == "Original")

# 7. Multiple category assignments for one record
MOCK_PAYLOAD = {"record_reassignments": [{"record_id": rec_dna, "assign_to_category_ids": [cat4, cat5]}]}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": False})
check("Valid multiple category assignment succeeds", r.json().get("status") == "success", r.json())
c.execute("SELECT category_id FROM record_categories WHERE record_id=?", (rec_dna,))
assigned_cats = set(row[0] for row in c.fetchall())
check("Multiple categories properly saved", cat4 in assigned_cats and cat5 in assigned_cats)

# 8. Preservation of source records during restructuring
c.execute("SELECT meaning, source_metadata FROM records WHERE id=?", (rec_dna,))
record_data = c.fetchone()
check("Preservation of source records", record_data[0] == "DNA meaning" and record_data[1] == "Wiki")

# 9. Dry-run database immutability
MOCK_PAYLOAD = {"category_renames": [{"category_id": cat2, "new_name": "DryRunName"}]}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": True})
c.execute("SELECT name FROM categories WHERE id=?", (cat2,))
check("Dry-run immutability", c.fetchone()[0] == "Original")

# 11. Valid reconstruction application
MOCK_PAYLOAD = {"category_renames": [{"category_id": cat2, "new_name": "Biological Sciences"}]}
r = client.post(f"/api/libraries/{lib_sci}/reconstruct", json={"guidance": "test", "dry_run": False})
c.execute("SELECT name FROM categories WHERE id=?", (cat2,))
check("Valid reconstruction application", c.fetchone()[0] == "Biological Sciences")


print("\n--- SUMMARY ---")
print(f"  PASS: {PASS}")
print(f"  FAIL: {FAIL}")
print("=" * 60)



