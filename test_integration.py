import os, json, time, sqlite3
os.environ["SAFIRA_DB_FILE"] = "safira_integration_test.db"

# Clean slate for deterministic isolation
if os.path.exists("safira_integration_test.db"):
    os.remove("safira_integration_test.db")

from fastapi.testclient import TestClient
from main import app

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
BLOCKED = 0
results = []

def check(name, condition, detail=""):
    global PASS, FAIL
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS += 1
    else:
        FAIL += 1
    results.append(f"  [{status}] {name}: {detail}")
    print(f"  [{status}] {name}: {detail}")

def blocked(name, reason):
    global BLOCKED
    BLOCKED += 1
    results.append(f"  [BLOCKED] {name}: {reason}")
    print(f"  [BLOCKED] {name}: {reason}")

print("=" * 60)
print("SAFIRA v2.0 — FULL INTEGRATION TEST SUITE")
print("Provider: OLLAMA (qwen2.5:3b) + GEMINI Embeddings")
print("=" * 60)

# -------------------------------------------------------
print("\n--- DETERMINISTIC TESTS (No LLM) ---")
# T1: Health check
r = client.get("/health")
check("Health endpoint", r.status_code == 200, r.json().get("engine",""))
check("Provider is ollama", r.json().get("active_provider","").lower() == "ollama", r.json().get("active_provider",""))

# T2: Library creation (DB only)
r = client.post("/api/libraries", json={
    "ai_identity": "ScienceAI_Test",
    "name": "Scientific Library",
    "description": "Physics and genetics",
    "purpose": "Research AI"
})
check("Library A creation", r.status_code == 200 and "library_id" in r.json(), str(r.json()))
lib_a = r.json().get("library_id", "")

r = client.post("/api/libraries", json={
    "ai_identity": "GameAI_Test",
    "name": "Gaming World Library",
    "description": "RPG kingdoms and characters",
    "purpose": "Game lore AI"
})
check("Library B creation", r.status_code == 200 and "library_id" in r.json(), str(r.json()))
lib_b = r.json().get("library_id", "")

# T3: Library listing
r = client.get("/api/libraries")
check("Library listing", r.status_code == 200 and len(r.json()["libraries"]) == 2, f"{len(r.json().get('libraries',[]))} libraries")

# T4: Empty tree
r = client.get(f"/api/libraries/{lib_a}/tree")
check("Empty tree on new library", r.status_code == 200 and r.json()["categories"] == [], str(r.json()))

# T5: Invalid library_id rejected at retrieval
r = client.post("/api/libraries/nonexistent_lib/retrieve", json={"query": "test"})
check("Invalid library_id returns 404", r.status_code == 404, str(r.status_code))

# -------------------------------------------------------
print("\n--- LIVE LLM INTEGRATION TESTS (Ollama) ---")

# T6: Ingest into Library A (Science)
print("  [INFO] Ingesting Science knowledge (Ollama LLM + Gemini Embedding)...")
t_start = time.time()
r = client.post(f"/api/libraries/{lib_a}/ingest", json={
    "content": "Quantum entanglement links particles instantly across any distance.",
    "source_name": "Physics Journal",
    "context": "Quantum Mechanics"
})
elapsed_a1 = int((time.time() - t_start) * 1000)
ok_a1 = r.status_code == 200 and r.json().get("status") == "success"
check("Ingest Science record 1", ok_a1, f"record_id={r.json().get('record_id','ERR')} [{elapsed_a1}ms]")
rec_a1 = r.json().get("record_id", "")

r = client.post(f"/api/libraries/{lib_a}/ingest", json={
    "content": "DNA double helix carries genetic information inherited across generations.",
    "source_name": "Biology Text",
    "context": "Genetics"
})
ok_a2 = r.status_code == 200 and r.json().get("status") == "success"
check("Ingest Science record 2", ok_a2, f"record_id={r.json().get('record_id','ERR')}")
rec_a2 = r.json().get("record_id", "")

# T7: Ingest into Library B (Gaming)
r = client.post(f"/api/libraries/{lib_b}/ingest", json={
    "content": "King Alaric rules the Northern Wastes with an iron fist.",
    "source_name": "World Lore DB",
    "context": "Kingdoms"
})
ok_b1 = r.status_code == 200 and r.json().get("status") == "success"
check("Ingest Game record 1", ok_b1, f"record_id={r.json().get('record_id','ERR')}")

r = client.post(f"/api/libraries/{lib_b}/ingest", json={
    "content": "The Crystal Spire grants invisibility to its wielder for 10 minutes.",
    "source_name": "Item Codex",
    "context": "Magic Items"
})
ok_b2 = r.status_code == 200 and r.json().get("status") == "success"
check("Ingest Game record 2", ok_b2, f"record_id={r.json().get('record_id','ERR')}")

# T8: Autonomous category hierarchy created
r = client.get(f"/api/libraries/{lib_a}/tree")
cats_a = r.json().get("categories", [])
check("Science library has categories", len(cats_a) > 0, f"{len(cats_a)} categories: {[c['name'] for c in cats_a]}")

r = client.get(f"/api/libraries/{lib_b}/tree")
cats_b = r.json().get("categories", [])
check("Gaming library has categories", len(cats_b) > 0, f"{len(cats_b)} categories: {[c['name'] for c in cats_b]}")

# T9: Different structures
sci_names = set(c["name"] for c in cats_a)
game_names = set(c["name"] for c in cats_b)
check("Libraries have different category structures", sci_names != game_names,
      f"Science={sci_names} | Gaming={game_names}")

# T10: Precision Retrieval - scoped to Library A
r = client.post(f"/api/libraries/{lib_a}/retrieve", json={"query": "particle physics quantum", "max_results": 3})
results_a = r.json().get("results", [])
check("Retrieval Library A returns results", len(results_a) > 0, f"{len(results_a)} results")
if results_a:
    check("Top result has relevance score", "relevance_score" in results_a[0], str(results_a[0].get("relevance_score")))
    check("Top result has category path", "categories" in results_a[0], str(results_a[0].get("categories")))

# T11: Cross-library isolation
r_b = client.post(f"/api/libraries/{lib_b}/retrieve", json={"query": "particle physics quantum", "max_results": 3})
results_b = r_b.json().get("results", [])
# Library B should NOT return science records
lib_a_record_ids = {rec_a1, rec_a2}
leaked = [r for r in results_b if r.get("record_id") in lib_a_record_ids]
check("No cross-library data leakage", len(leaked) == 0,
      f"Leaked records: {leaked if leaked else 'None'}")

# T12: Semantic Guardian
r = client.post("/api/semantic/analyze", json={
    "text_a": "All employees must be in the office 3 days per week.",
    "text_b": "Staff are required to work on-site at least three days weekly."
})
sem = r.json()
check("Semantic Guardian endpoint works", "are_equivalent" in sem, str(sem)[:80])
check("Equivalent texts detected as equivalent", sem.get("are_equivalent") == True, str(sem.get("are_equivalent")))

r2 = client.post("/api/semantic/analyze", json={
    "text_a": "Remote work is fully permitted every day.",
    "text_b": "All staff must be in the office 5 days a week."
})
sem2 = r2.json()
check("Contradiction detected between conflicting texts",
      sem2.get("contradiction_detected") == True, str(sem2.get("contradiction_detected")))

# T13: Mode 2 Reconstruction with guidance
r = client.post(f"/api/libraries/{lib_a}/reconstruct", json={
    "guidance": "Separate physics and biology into their own root sections.",
    "dry_run": True  # Safe: dry run only
})
recon = r.json()
check("Reconstruction dry-run works", r.status_code == 200 and "proposed_changes" in recon, str(list(recon.keys())))

# -------------------------------------------------------
print("\n--- SUMMARY ---")
print(f"  PASS:    {PASS}")
print(f"  FAIL:    {FAIL}")
print(f"  BLOCKED: {BLOCKED}")
print(f"  TOTAL:   {PASS+FAIL+BLOCKED}")
print("=" * 60)





