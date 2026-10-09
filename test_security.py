import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

# Setup Test DB
os.environ["SAFIRA_DB_FILE"] = "safira_security_test.db"
if os.path.exists("safira_security_test.db"):
    os.remove("safira_security_test.db")

from main import app
import main
import hashlib
import uuid

# Mock LLM for tests
main.call_llm_json = lambda x: {}

client = TestClient(app)

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}: {detail}")

print("=" * 60)
print("SAFIRA API SECURITY & AUTHORIZATION TEST SUITE")
print("=" * 60)

db = sqlite3.connect("safira_security_test.db")
c = db.cursor()

# Provision Test Clients Manually
client_a_id = "client_A"
client_a_key = "sk_A"
c.execute("INSERT INTO api_clients (id, api_key_hash, name, is_revoked) VALUES (?, ?, ?, ?)", 
          (client_a_id, hashlib.sha256(client_a_key.encode()).hexdigest(), "Client A", 0))

client_b_id = "client_B"
client_b_key = "sk_B"
c.execute("INSERT INTO api_clients (id, api_key_hash, name, is_revoked) VALUES (?, ?, ?, ?)", 
          (client_b_id, hashlib.sha256(client_b_key.encode()).hexdigest(), "Client B", 0))

client_revoked_id = "client_REV"
client_revoked_key = "sk_REV"
c.execute("INSERT INTO api_clients (id, api_key_hash, name, is_revoked) VALUES (?, ?, ?, ?)", 
          (client_revoked_id, hashlib.sha256(client_revoked_key.encode()).hexdigest(), "Client Revoked", 1))

db.commit()

headers_a = {"Authorization": f"Bearer {client_a_key}"}
headers_b = {"Authorization": f"Bearer {client_b_key}"}
headers_rev = {"Authorization": f"Bearer {client_revoked_key}"}

# 1. Missing API key returns 401
r = client.get("/api/libraries")
check(f"Missing API key returns 401: got {r.status_code}", r.status_code == 401)

# 2. Invalid API key returns 401
r = client.get("/api/libraries", headers={"Authorization": "Bearer invalid_key"})
check(f"Invalid API key returns 401: got {r.status_code}", r.status_code == 401)

# 3. Valid API key authenticates successfully
r = client.get("/api/libraries", headers=headers_a)
check(f"Valid API key authenticates successfully: got {r.status_code}", r.status_code == 200)

# 4. Revoked key returns 401
r = client.get("/api/libraries", headers=headers_rev)
check(f"Revoked key returns 401: got {r.status_code}", r.status_code == 401)

# 11. New library ownership is correctly assigned
r = client.post("/api/libraries", headers=headers_a, json={"ai_identity": "A", "name": "LibA", "description": "A", "purpose": "A"})
lib_a = r.json()["library_id"]
r = client.post("/api/libraries", headers=headers_b, json={"ai_identity": "B", "name": "LibB", "description": "B", "purpose": "B"})
lib_b = r.json()["library_id"]

c.execute("SELECT owner_id FROM libraries WHERE id=?", (lib_a,))
check("New library ownership assigned", c.fetchone()[0] == client_a_id)

# 5. Client A can access its own library
r = client.get(f"/api/libraries/{lib_a}/tree", headers=headers_a)
check("Client A can read own library", r.status_code == 200)

# 6. Client A cannot read Client B's library
r = client.get(f"/api/libraries/{lib_b}/tree", headers=headers_a)
check("Client A cannot read Client B's library", r.status_code == 403)

# 7. Client A cannot write to Client B's library
r = client.post(f"/api/libraries/{lib_b}/ingest", headers=headers_a, json={"content": "test", "source_name": "test", "context": "test"})
check(f"Client A cannot write to Client B's library: got {r.status_code}", r.status_code == 403)

# 8. Client A cannot reconstruct Client B's library
r = client.post(f"/api/libraries/{lib_b}/reconstruct", headers=headers_a, json={"guidance": "test", "dry_run": False})
check("Client A cannot reconstruct Client B's library", r.status_code == 403)

# 9. Client A cannot retrieve Client B's knowledge
r = client.post(f"/api/libraries/{lib_b}/retrieve", headers=headers_a, json={"query": "test"})
check("Client A cannot retrieve Client B's knowledge", r.status_code == 403)

# 10. Client A cannot read Client B's relationships
r = client.get(f"/api/libraries/{lib_b}/relations", headers=headers_a)
check("Client A cannot read Client B's relationships", r.status_code == 403)

# 13. Secrets are not returned by ordinary API endpoints
r = client.get("/api/libraries", headers=headers_a)
resp = r.json()
check("Secrets not exposed in library list", "api_key" not in str(resp) and "owner_id" not in str(resp))

# Health check remains public
r = client.get("/health")
check("Health check remains unauthenticated", r.status_code == 200)

print("\n--- SUMMARY ---")
print(f"  PASS: {PASS}")
print(f"  FAIL: {FAIL}")
print("=" * 60)
