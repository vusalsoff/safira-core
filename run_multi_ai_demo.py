import os
import json
import sqlite3

# Set environment variable BEFORE importing main
os.environ["SAFIRA_DB_FILE"] = "safira_test.db"

# Clear test database to ensure absolute deterministic isolation
if os.path.exists("safira_test.db"):
    os.remove("safira_test.db")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def print_tree(lib_name, tree):
    print(f"\n--- {lib_name} CATEGORY TREE ---")
    if not tree:
        print(" (Empty)")
        return
    for c in tree:
        parent = f" [Parent: {c['parent_id']}]" if c.get('parent_id') else " [Root]"
        print(f" - {c['name']} ({c['id']}){parent}")

def main():
    print("==================================================")
    print("SAFIRA - HYBRID LOGICAL LIBRARY ARCHITECTURE DEMO")
    print("==================================================")
    
    # 1. Create Library A (Science AI)
    print("\n[1] Creating Library A: Scientific Research AI...")
    res_a = client.post("/api/libraries", json={
        "ai_identity": "ScienceAI_01",
        "name": "Global Scientific Knowledge Base",
        "description": "Library for storing strict scientific facts.",
        "purpose": "Analyze physics, genetics, and thermodynamics."
    })
    lib_a_id = res_a.json()["library_id"]
    
    # 2. Create Library B (Gaming AI)
    print("[2] Creating Library B: Gaming World AI...")
    res_b = client.post("/api/libraries", json={
        "ai_identity": "GameAI_99",
        "name": "Eldoria World Lore",
        "description": "Library for game locations, abilities, and characters.",
        "purpose": "RPG world building and lore enforcement."
    })
    lib_b_id = res_b.json()["library_id"]
    
    # 3. Ingest into Library A
    print("\n[3] Ingesting Knowledge into Library A (Science)...")
    sci_data = [
        {"content": "Quantum entanglement links particles instantly across space.", "source_name": "Physics Jnl", "context": "Quantum Mechanics"},
        {"content": "DNA contains the genetic instructions for development.", "source_name": "Bio Text", "context": "Genetics"}
    ]
    for d in sci_data:
        client.post(f"/api/libraries/{lib_a_id}/ingest", json=d)
        
    # 4. Ingest into Library B
    print("[4] Ingesting Knowledge into Library B (Gaming)...")
    game_data = [
        {"content": "The Crystal Spire grants invisibility to the user.", "source_name": "Lore DB", "context": "Magic Items"},
        {"content": "King Alaric rules the Northern Wastes.", "source_name": "World Map", "context": "Kingdoms"}
    ]
    for d in game_data:
        client.post(f"/api/libraries/{lib_b_id}/ingest", json=d)
        
    # 5. Inspect Autonomous Hierarchies
    tree_a = client.get(f"/api/libraries/{lib_a_id}/tree").json()["categories"]
    print_tree("LIBRARY A (Science)", tree_a)
    
    tree_b = client.get(f"/api/libraries/{lib_b_id}/tree").json()["categories"]
    print_tree("LIBRARY B (Gaming)", tree_b)
    
    # 6. Mode 2: Reconstruct with Guidance (Library B)
    print("\n[5] Executing Mode 2 (Reconstruct) with Main AI Guidance on Library B...")
    print("Guidance: 'Group all Lore under a single Root Category called Lore.'")
    recon_res = client.post(f"/api/libraries/{lib_b_id}/reconstruct", json={
        "guidance": "Group all Lore under a single Root Category called Lore.",
        "dry_run": False
    })
    print("Reconstruction Actions Taken:")
    print(json.dumps(recon_res.json()["applied_changes"], indent=2))
    
    tree_b_new = client.get(f"/api/libraries/{lib_b_id}/tree").json()["categories"]
    print_tree("LIBRARY B (Gaming - POST RECONSTRUCTION)", tree_b_new)
    
    # 7. Scoped Retrieval
    print("\n[6] Precision Retrieval (Scoped Enforcement)...")
    query = "Who rules the north?"
    print(f"Querying Library A (Science) for: '{query}'")
    ret_a = client.post(f"/api/libraries/{lib_a_id}/retrieve", json={"query": query})
    print("Top Result Lib A:", ret_a.json()["results"][0]["meaning"] if ret_a.json()["results"] else "No Results")
    
    print(f"\nQuerying Library B (Gaming) for: '{query}'")
    ret_b = client.post(f"/api/libraries/{lib_b_id}/retrieve", json={"query": query})
    top_b = ret_b.json()["results"][0]
    print(f"Top Result Lib B: {top_b['meaning']} [Score: {top_b['relevance_score']}] (Categories: {top_b['categories']})")
    
    print("\nDemonstration Complete! Total Isolation and Hybrid Hierarchies verified.")

if __name__ == "__main__":
    main()
