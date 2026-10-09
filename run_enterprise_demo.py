import os
import json

# Ensure strict DB isolation for the Enterprise Demo
os.environ["SAFIRA_DB_FILE"] = "safira_enterprise_demo.db"
if os.path.exists("safira_enterprise_demo.db"):
    os.remove("safira_enterprise_demo.db")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

DATASET = [
    {"content": "Employees must work from the office 3 days a week.", "source_name": "HR Policy 2026", "context": "Office Attendance"},
    {"content": "Staff are required to be on-site at least three days weekly.", "source_name": "Employee Handbook", "context": "Office Attendance"},
    {"content": "Remote work is permitted 5 days a week for all staff.", "source_name": "Remote Policy Draft", "context": "Office Attendance"},
    {"content": "All laptops must be connected to the corporate VPN when off-site.", "source_name": "IT Security v2", "context": "Security"},
    {"content": "Vacation requests need 14 days prior notice.", "source_name": "HR Policy 2026", "context": "Leave Policy"},
    {"content": "Holiday applications require two weeks of advance warning.", "source_name": "Employee Handbook", "context": "Leave Policy"}
]

def run_demo():
    print("=== SAFIRA v2.0 ENTERPRISE DEMONSTRATION ===")
    
    # Create isolated library
    print("\n[0] Creating Enterprise Knowledge Library...")
    lib_res = client.post("/api/libraries", json={
        "ai_identity": "EnterpriseCorp_AI",
        "name": "Corporate Policies",
        "description": "Internal HR and IT rules",
        "purpose": "Govern employee conduct and remote work."
    })
    lib_id = lib_res.json()["library_id"]
    
    # 1. Ingest
    print("\n[Mode 1 & 4] INGESTING DATASET (Autonomous Categorization)...")
    for idx, item in enumerate(DATASET):
        print(f"Ingesting #{idx+1}: {item['content'][:40]}...")
        res = client.post(f"/api/libraries/{lib_id}/ingest", json=item)
        if res.status_code != 200:
            print("Error:", res.text)
            
    # 2. Reconstruct
    print("\n[Mode 2] DATA RECONSTRUCTOR: Reorganizing hierarchy and finding semantic links...")
    res = client.post(f"/api/libraries/{lib_id}/reconstruct", json={"guidance": "Group all HR and Office rules under Human Resources."})
    reconstruct_data = res.json()
    print("Reconstruction output:", json.dumps(reconstruct_data.get("applied_changes", {}), indent=2))

    # 3. Benchmark Retrieval
    print("\n[Mode 5] PRECISION RETRIEVAL BENCHMARK")
    query = "How many days must I be in the office?"
    print(f"Test Query: '{query}'")
    
    res_saf = client.post(f"/api/libraries/{lib_id}/retrieve", json={"query": query, "max_results": 3})
    saf_results = res_saf.json()
    print(f"\n-> SAFIRA (Semantic Embedding) [Time: {saf_results.get('metadata', {}).get('retrieval_time_ms', 0)}ms]:")
    for r in saf_results.get("results", []):
        print(f"   - [Score: {r['relevance_score']}] {r['meaning']} (Source: {r['source_name']}, Categories: {r.get('categories')})")
        
    print("\n=== ENTERPRISE DEMO COMPLETE ===")

if __name__ == "__main__":
    run_demo()
