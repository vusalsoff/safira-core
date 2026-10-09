import os
import sqlite3
import pytest
from safira.core.engine import SafiraEngine
from safira.providers.base import LLMProvider, EmbeddingProvider

# Mock Providers for deterministic architectural tests
class MockLLM(LLMProvider):
    def call_json(self, prompt: str) -> dict:
        if "Data Architect" in prompt:
            return {
                "extracted_meaning": "Mock Meaning",
                "placements": [{"type": "new", "name": "EngineCat", "description": "Desc", "parent_id": None}]
            }
        elif "Data Reconstructor" in prompt:
            return {
                "proposed_changes": [{"action": "create", "id": "cat_test_recon", "name": "ReconCat", "parent_id": None}]
            }
        elif "Semantic Guardian" in prompt:
            return {
                "are_equivalent": True,
                "contradiction_detected": False,
                "similarity_score": 0.9,
                "differences_noted": "None"
            }
        return {}

class MockEmbed(EmbeddingProvider):
    def get_embedding(self, text: str) -> list:
        return [0.1, 0.2, 0.3]

def setup_db():
    db_file = "safira_engine_test.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    
    # Init schema
    import main
    original_db = main.DB_FILE
    main.DB_FILE = db_file
    main.init_db()
    main.DB_FILE = original_db
    return conn

def test_engine_directly():
    conn = setup_db()
    c = conn.cursor()
    
    # 1. Create a library
    lib_id = "lib_engine_1"
    c.execute("INSERT INTO libraries (id, ai_identity, name, description, purpose, created_at, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (lib_id, "Engine AI", "Engine Lib", "Desc", "Testing", "2026-01-01", "owner_1"))
    conn.commit()
    
    engine = SafiraEngine(MockLLM(), MockEmbed())
    
    # 2. Organizing knowledge (Ingest)
    res = engine.ingest_knowledge(conn, lib_id, "Test content", "Test source", "Test context")
    assert res["status"] == "success"
    assert res["extracted_meaning"] == "Mock Meaning"
    assert len(res["categories_assessed"]) == 1
    
    # 3. Validating hierarchy (Reconstruct)
    recon = engine.reconstruct_library(conn, lib_id, "Make it better", dry_run=False)
    assert recon["status"] == "applied"
    
    # 4. Retrieving knowledge
    ret = engine.retrieve_knowledge(conn, lib_id, "query", max_results=5)
    assert len(ret["results"]) > 0
    assert ret["results"][0]["meaning"] == "Mock Meaning"
    
    # 5. Enforcing library isolation
    # If we try to ingest into a nonexistent library
    try:
        engine.ingest_knowledge(conn, "lib_fake", "x", "y", "z")
        assert False, "Should have failed"
    except ValueError as e:
        assert "Library not found" in str(e)
        
    # 6. Handling provider failure safely
    class FailingEmbed(EmbeddingProvider):
        def get_embedding(self, text):
            raise Exception("API Limit Reached")
            
    engine_fail = SafiraEngine(MockLLM(), FailingEmbed())
    try:
        engine_fail.retrieve_knowledge(conn, lib_id, "query")
        assert False, "Should have failed"
    except Exception as e:
        assert "Embedding provider failure" in str(e)
        
    print("ALL CORE ENGINE DIRECT TESTS PASSED")

if __name__ == "__main__":
    test_engine_directly()
