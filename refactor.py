import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace health check -> ingest_knowledge
content = re.sub(
    r'def cosine_similarity.*?(?=@app\.get\("/health"\))',
    '''from safira.providers.ollama import OllamaProvider
from safira.providers.gemini import GeminiProvider
from safira.core.engine import SafiraEngine, get_library_tree, validate_hierarchy

llm_provider = OllamaProvider(model=OLLAMA_MODEL) if ACTIVE_PROVIDER == "ollama" else GeminiProvider()
embed_provider = GeminiProvider()
engine = SafiraEngine(llm_provider, embed_provider)

''', content, flags=re.DOTALL
)

# Replace ingest_knowledge
content = re.sub(
    r'def ingest_knowledge.*?def reconstruct_library',
    '''def ingest_knowledge(lib_id: str, req: IngestRequest, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    try:
        return engine.ingest_knowledge(db, lib_id, req.content, req.source_name, req.context)
    except ValueError as e:
        if str(e) == 'Library not found': raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/libraries/{lib_id}/reconstruct")
def reconstruct_library''', content, flags=re.DOTALL
)

# Replace reconstruct_library
content = re.sub(
    r'def reconstruct_library.*?def retrieve_knowledge',
    '''def reconstruct_library(lib_id: str, req: ReconstructRequest, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    try:
        return engine.reconstruct_library(db, lib_id, req.guidance, req.dry_run)
    except ValueError as e:
        if str(e) == 'Library not found': raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/libraries/{lib_id}/retrieve")
def retrieve_knowledge''', content, flags=re.DOTALL
)

# Replace retrieve_knowledge
content = re.sub(
    r'def retrieve_knowledge.*?def semantic_analyze',
    '''def retrieve_knowledge(lib_id: str, req: RetrieveRequest, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    try:
        return engine.retrieve_knowledge(db, lib_id, req.query, req.max_results, req.category_filter)
    except ValueError as e:
        if str(e) == 'Library not found': raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if str(e).startswith('Embedding provider failure'): raise HTTPException(status_code=502, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/semantic/analyze")
def semantic_analyze''', content, flags=re.DOTALL
)

# Replace semantic_analyze
content = re.sub(
    r'def semantic_analyze.*?def get_library_relations',
    '''def semantic_analyze(req: SemanticAnalyzeRequest, client_id: str = Depends(verify_api_key)):
    try:
        return engine.semantic_analyze(req.text_a, req.text_b)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/libraries/{lib_id}/relations")
def get_library_relations''', content, flags=re.DOTALL
)

# Replace get_library_relations
content = re.sub(
    r'def get_library_relations.*?if __name__ == "__main__":',
    '''def get_library_relations(lib_id: str, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    try:
        return engine.get_library_relations(db, lib_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":''', content, flags=re.DOTALL
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
