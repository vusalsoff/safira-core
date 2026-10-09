import requests
import sys

BASE_URL = "http://localhost:8000/api"
API_KEY = sys.argv[1] if len(sys.argv) > 1 else "MISSING_KEY"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def run_demo():
    print("=== GAMING WORLD MAIN AI ===")
    
    r = requests.post(f"{BASE_URL}/libraries", headers=HEADERS, json={"name": "Gaming AI Lib", "description": "Game Mechanics"})
    if r.status_code != 200:
        print(f"Failed to create library: {r.text}")
        return
    lib_id = r.json()["library_id"]
    print(f"[SUCCESS] Created Library: {lib_id}")
    
    knowledge = {
        "content": "A critical hit deals double damage.",
        "source_name": "Game Rules",
        "context": "Combat"
    }
    r = requests.post(f"{BASE_URL}/libraries/{lib_id}/ingest", headers=HEADERS, json=knowledge)
    print(f"[SUCCESS] Ingested record: {r.json().get('record_id')}")

if __name__ == "__main__":
    run_demo()
