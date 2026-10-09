import requests
import sys
import json

BASE_URL = "http://localhost:8000/api"
API_KEY = sys.argv[1] if len(sys.argv) > 1 else "MISSING_KEY"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def run_demo():
    print("=== SCIENTIFIC RESEARCH MAIN AI ===")
    
    # 1. Create Library
    r = requests.post(f"{BASE_URL}/libraries", headers=HEADERS, json={"name": "Science AI Lib", "description": "Physics and Biology"})
    if r.status_code != 200:
        print(f"Failed to create library: {r.text}")
        return
    lib_id = r.json()["library_id"]
    print(f"[SUCCESS] Created Library: {lib_id}")
    
    # 2. Ingest Knowledge
    knowledge = {
        "content": "Quantum entanglement links particles instantly across any distance.",
        "source_name": "Quantum Physics Journal",
        "context": "Physics"
    }
    r = requests.post(f"{BASE_URL}/libraries/{lib_id}/ingest", headers=HEADERS, json=knowledge)
    print(f"[SUCCESS] Ingested record: {r.json().get('record_id')}")
    
    # 3. Retrieve Knowledge
    r = requests.post(f"{BASE_URL}/libraries/{lib_id}/retrieve", headers=HEADERS, json={"query": "quantum mechanics"})
    print(f"[SUCCESS] Retrieved {len(r.json().get('results', []))} results")
    
    # 4. Semantic Guardian
    r = requests.post(f"{BASE_URL}/semantic/analyze", headers=HEADERS, json={"text_a": "DNA holds genetic data.", "text_b": "Genetic information is stored in DNA."})
    print(f"[SUCCESS] Semantic Guardian: equivalent={r.json().get('are_equivalent')}")

if __name__ == "__main__":
    run_demo()

