import os
import sqlite3
import secrets, uuid, hashlib, datetime

# Set DB before importing main
os.environ["SAFIRA_DB_FILE"] = "safira_phase6_test.db"
if os.path.exists("safira_phase6_test.db"):
    os.remove("safira_phase6_test.db")

from fastapi.testclient import TestClient
from main import app, init_db

def run_phase6_test():
    print("="*60)
    print("SAFIRA - PHASE 6: EXTERNAL MAIN AI VERIFICATION")
    print("="*60)
    
    init_db()
    db = sqlite3.connect("safira_phase6_test.db")
    client = TestClient(app)
    
    key_a = "sk_" + secrets.token_urlsafe(32)
    client_a_id = uuid.uuid4().hex
    db.execute("INSERT INTO api_clients (id, api_key_hash, name, is_revoked, created_at) VALUES (?, ?, ?, 0, ?)", 
               (client_a_id, hashlib.sha256(key_a.encode()).hexdigest(), "Client A", datetime.datetime.utcnow().isoformat()))
               
    key_b = "sk_" + secrets.token_urlsafe(32)
    client_b_id = uuid.uuid4().hex
    db.execute("INSERT INTO api_clients (id, api_key_hash, name, is_revoked, created_at) VALUES (?, ?, ?, 0, ?)", 
               (client_b_id, hashlib.sha256(key_b.encode()).hexdigest(), "Client B", datetime.datetime.utcnow().isoformat()))
    db.commit()
    
    headers_a = {"Authorization": f"Bearer {key_a}"}
    headers_b = {"Authorization": f"Bearer {key_b}"}
    
    PASS = 0
    FAIL = 0
    
    def check(name, cond):
        nonlocal PASS, FAIL
        if cond:
            print(f"  [PASS] {name}")
            PASS += 1
        else:
            print(f"  [FAIL] {name}")
            FAIL += 1

    r_a = client.post("/api/libraries", headers=headers_a, json={"name": "Science Lib", "ai_identity": "Scientific AI", "description": "Physics", "purpose": "Research"})
    check("Client A created library", r_a.status_code == 200)
    lib_a = r_a.json().get("library_id"); print(r_a.json())
    
    r_b = client.post("/api/libraries", headers=headers_b, json={"name": "Gaming Lib", "ai_identity": "Gaming AI", "description": "Games", "purpose": "Entertainment"})
    check("Client B created library", r_b.status_code == 200)
    lib_b = r_b.json()["library_id"]
    
    r_b_try_a = client.get(f"/api/libraries/{lib_a}/tree", headers=headers_b)
    check("Client B blocked from Client A library", r_b_try_a.status_code in [403, 404])
    
    r_ingest = client.post(f"/api/libraries/{lib_a}/ingest", headers=headers_a, json={
        "content": "DNA holds genetic data.", "source_name": "Bio101", "context": ""
    })
    check("Mode 1: Data Architect (Ingest)", r_ingest.status_code == 200 and "record_id" in r_ingest.json())
    
    r_recon = client.post(f"/api/libraries/{lib_a}/reconstruct", headers=headers_a, json={"dry_run": True})
    check("Mode 2: Data Reconstructor (Dry Run)", r_recon.status_code == 200 and "status" in r_recon.json())
    
    r_guard = client.post("/api/semantic/analyze", headers=headers_a, json={
        "text_a": "The car is fast", "text_b": "The automobile is quick"
    })
    check("Mode 3: Semantic Guardian", r_guard.status_code == 200 and "are_equivalent" in r_guard.json()); 
    
    r_rel = client.get(f"/api/libraries/{lib_a}/relations", headers=headers_a)
    check("Mode 4: Relation Engine", r_rel.status_code == 200 and "relations" in r_rel.json())
    
    r_ret = client.post(f"/api/libraries/{lib_a}/retrieve", headers=headers_a, json={"query": "DNA"})
    check("Mode 5: Precision Retrieval", r_ret.status_code == 200 and "results" in r_ret.json())
    
    print("\n--- SUMMARY ---")
    print(f"PASS: {PASS}")
    print(f"FAIL: {FAIL}")

if __name__ == "__main__":
    run_phase6_test()





