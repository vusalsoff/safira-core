import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    print("Health check passed. Engine:", res.json())

def main():
    test_health()
    
    print("\n--- Creating Test Library ---")
    lib_res = requests.post(f"{BASE_URL}/api/libraries", json={
        "ai_identity": "TestAI_01",
        "name": "General Test Knowledge",
        "description": "Library for automated testing",
        "purpose": "General rules and logic."
    })
    lib_id = lib_res.json()["library_id"]
    print(f"Library created: {lib_id}")

    print("\n--- Testing Mode 1 & 4 (Ingest & Relation) ---")
    data1 = {
        "content": "Vacation requests require 2 weeks notice for approval.",
        "source_name": "Policy v1",
        "context": "Leave"
    }
    data2 = {
        "content": "Employees must take at least 10 consecutive days of leave.",
        "source_name": "Policy v2",
        "context": "Leave"
    }
    r1 = requests.post(f"{BASE_URL}/api/libraries/{lib_id}/ingest", json=data1).json()
    print("Ingest 1:", r1)
    r2 = requests.post(f"{BASE_URL}/api/libraries/{lib_id}/ingest", json=data2).json()
    print("Ingest 2:", r2)
    
    print("\n--- Testing Mode 5 (Precision Retrieval) ---")
    ret = requests.post(f"{BASE_URL}/api/libraries/{lib_id}/retrieve", json={"query": "How many days notice?"}).json()
    print("Retrieval Top Result:", ret["results"][0]["meaning"] if ret.get("results") else "No results")
    
    print("\n--- Testing Mode 3 (Semantic Analysis directly via LLM) ---")
    sem = requests.post(f"{BASE_URL}/api/semantic/analyze", json={
        "text_a": "Staff must work from office on Tuesday.",
        "text_b": "Tuesday is a mandatory office day."
    }).json()
    print("Equivalence Test:", sem)

    print("\nAll Legacy Tests Ported and Completed.")

if __name__ == "__main__":
    main()
