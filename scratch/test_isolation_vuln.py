import sqlite3
import os

DB_FILE = "safira_iso_test.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Create schema minimal for test
db = sqlite3.connect(DB_FILE)
db.row_factory = sqlite3.Row
c = db.cursor()

c.execute("CREATE TABLE libraries (id TEXT PRIMARY KEY, name TEXT)")
c.execute("CREATE TABLE records (id TEXT PRIMARY KEY, library_id TEXT, meaning TEXT)")
c.execute("CREATE TABLE categories (id TEXT PRIMARY KEY, library_id TEXT, name TEXT)")
c.execute("CREATE TABLE record_categories (record_id TEXT, category_id TEXT)")
c.execute("CREATE TABLE relationships (id TEXT PRIMARY KEY, library_id TEXT, source_record_id TEXT, target_record_id TEXT)")

# Setup data
c.execute("INSERT INTO libraries (id, name) VALUES ('lib_A', 'Science')")
c.execute("INSERT INTO libraries (id, name) VALUES ('lib_B', 'Gaming')")

c.execute("INSERT INTO records (id, library_id, meaning) VALUES ('rec_A1', 'lib_A', 'Physics')")
c.execute("INSERT INTO records (id, library_id, meaning) VALUES ('rec_B1', 'lib_B', 'Zelda')")

c.execute("INSERT INTO categories (id, library_id, name) VALUES ('cat_A1', 'lib_A', 'Science Cat')")
c.execute("INSERT INTO categories (id, library_id, name) VALUES ('cat_B1', 'lib_B', 'Gaming Cat')")

c.execute("INSERT INTO record_categories (record_id, category_id) VALUES ('rec_A1', 'cat_A1')")
c.execute("INSERT INTO record_categories (record_id, category_id) VALUES ('rec_B1', 'cat_B1')")
db.commit()

# Simulate malicious reconstruct payload from LLM for lib_A
llm_payload = {
    "record_reassignments": [
        {"record_id": "rec_B1", "assign_to_category_ids": ["cat_A1"]} # Lib A tries to steal Lib B's record
    ],
    "semantic_relations": [
        {"source_record_id": "rec_B1", "target_record_id": "rec_A1", "relation_type": "SHARES_CONTEXT"}
    ]
}

print("Before Malicious Reconstruct:")
print("Lib B Record Categories:", [dict(r) for r in c.execute("SELECT * FROM record_categories WHERE record_id='rec_B1'").fetchall()])

# --- VULNERABLE CODE FROM main.py ---
lib_id = 'lib_A'
for rr in llm_payload.get("record_reassignments", []):
    rid = rr.get("record_id")
    # This deletes B's records from their categories!
    c.execute("DELETE FROM record_categories WHERE record_id=?", (rid,))
    for cid in rr.get("assign_to_category_ids", []):
        c.execute("INSERT OR IGNORE INTO record_categories (record_id, category_id) VALUES (?, ?)", (rid, cid))

for sr in llm_payload.get("semantic_relations", []):
    c.execute("INSERT INTO relationships (id, library_id, source_record_id, target_record_id) VALUES ('rel_1', ?, ?, ?)",
              (lib_id, sr.get("source_record_id"), sr.get("target_record_id")))

db.commit()

print("\nAfter Malicious Reconstruct:")
print("Lib B Record Categories (Expected: [{'record_id': 'rec_B1', 'category_id': 'cat_B1'}]):")
print("Actual:", [dict(r) for r in c.execute("SELECT * FROM record_categories WHERE record_id='rec_B1'").fetchall()])
print("Relations created (Expected: []):")
print("Actual:", [dict(r) for r in c.execute("SELECT * FROM relationships").fetchall()])

