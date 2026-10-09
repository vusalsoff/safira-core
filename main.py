from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import os
import uuid
from datetime import datetime
import json
import math
from tenacity import retry, stop_after_attempt, wait_exponential

# Load .env
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line.strip() and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

ACTIVE_PROVIDER = os.environ.get("ACTIVE_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))
DB_FILE = os.environ.get("SAFIRA_DB_FILE", "safira.db")

# Gemini client is ALWAYS initialized for embeddings regardless of ACTIVE_PROVIDER
gemini_client = None
openai_client = None

import requests as _requests  # for Ollama HTTP calls

try:
    from google import genai
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as _e:
    print(f"[WARN] Gemini client init failed: {_e}")

if ACTIVE_PROVIDER == "openai":
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as _e:
        print(f"[WARN] OpenAI client init failed: {_e}")


app = FastAPI(title="SAFIRA Engine - Hybrid Logical Library", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 1. Libraries Registry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS libraries (
            id TEXT PRIMARY KEY,
            ai_identity TEXT,
            name TEXT,
            description TEXT,
            purpose TEXT,
            config TEXT,
            created_at TEXT
        )
    ''')
    # 2. Category Tree
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            library_id TEXT,
            parent_id TEXT,
            name TEXT,
            description TEXT,
            created_at TEXT,
            FOREIGN KEY(library_id) REFERENCES libraries(id),
            FOREIGN KEY(parent_id) REFERENCES categories(id)
        )
    ''')
    # 3. Records (Knowledge Units)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            library_id TEXT,
            original_expression TEXT,
            meaning TEXT,
            context TEXT,
            source_metadata TEXT,
            verification_status TEXT,
            embedding TEXT,
            created_at TEXT,
            FOREIGN KEY(library_id) REFERENCES libraries(id)
        )
    ''')
    # Legacy migration: add library_id if missing
    try:
        cursor.execute("ALTER TABLE records ADD COLUMN library_id TEXT DEFAULT 'legacy_lib'")
    except:
        pass

    # 4. Record-Category Junction
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS record_categories (
            record_id TEXT,
            category_id TEXT,
            PRIMARY KEY(record_id, category_id),
            FOREIGN KEY(record_id) REFERENCES records(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    # 5. Relationships
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            library_id TEXT,
            source_record_id TEXT,
            target_record_id TEXT,
            relation_type TEXT,
            reason TEXT,
            created_at TEXT,
            FOREIGN KEY(library_id) REFERENCES libraries(id),
            FOREIGN KEY(source_record_id) REFERENCES records(id),
            FOREIGN KEY(target_record_id) REFERENCES records(id)
        )
    ''')
    try:
        cursor.execute("ALTER TABLE relationships ADD COLUMN library_id TEXT DEFAULT 'legacy_lib'")
        cursor.execute("ALTER TABLE relationships ADD COLUMN reason TEXT")
    except:
        pass

    # 6. Audit Log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            library_id TEXT,
            action TEXT,
            details TEXT,
            created_at TEXT
        )
    ''')
    
    # 7. API Clients (Main AI identities)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_clients (
            id TEXT PRIMARY KEY,
            api_key_hash TEXT,
            name TEXT,
            is_revoked BOOLEAN DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    # Add ownership to libraries safely (additive migration)
    try:
        cursor.execute("ALTER TABLE libraries ADD COLUMN owner_id TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    conn.commit()
    conn.close()

init_db()

import hashlib
import secrets
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, Response

security = HTTPBearer(auto_error=False)

def verify_api_key(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security), db: sqlite3.Connection = Depends(get_db)):
    """Authenticate client via Bearer token or HttpOnly Cookie."""
    token = None
    if credentials:
        token = credentials.credentials
    elif "safira_session" in request.cookies:
        token = request.cookies.get("safira_session")
        
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    cursor = db.cursor()
    cursor.execute("SELECT id, is_revoked FROM api_clients WHERE api_key_hash=?", (token_hash,))
    client = cursor.fetchone()
    
    if not client:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if client["is_revoked"]:
        raise HTTPException(status_code=401, detail="API Key has been revoked")
        
    return client["id"]

@app.post("/api/auth/login")
def login(request: Request, response: Response, db: sqlite3.Connection = Depends(get_db)):
    """Backend-mediated login for the frontend demo."""
    data = request.headers.get("Authorization")
    if not data or not data.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token in header")
    
    token = data.split(" ")[1]
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    cursor = db.cursor()
    cursor.execute("SELECT id, is_revoked FROM api_clients WHERE api_key_hash=?", (token_hash,))
    client = cursor.fetchone()
    
    if not client or client["is_revoked"]:
        raise HTTPException(status_code=401, detail="Invalid or revoked API Key")
        
    response.set_cookie(key="safira_session", value=token, httponly=True, samesite="lax", max_age=86400)
    return {"status": "success", "client_id": client["id"]}

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("safira_session")
    return {"status": "success"}

def verify_library_access(lib_id: str, client_id: str, db: sqlite3.Connection):
    """Authorize authenticated client against library ownership."""
    cursor = db.cursor()
    cursor.execute("SELECT owner_id FROM libraries WHERE id=?", (lib_id,))
    lib = cursor.fetchone()
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
        
    if lib["owner_id"] != client_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this library")

# --- Helpers ---
from safira.providers.ollama import OllamaProvider
from safira.providers.gemini import GeminiProvider
from safira.core.engine import SafiraEngine, get_library_tree, validate_hierarchy

llm_provider = OllamaProvider(model=OLLAMA_MODEL) if ACTIVE_PROVIDER == 'ollama' else GeminiProvider()
embed_provider = GeminiProvider()
engine = SafiraEngine(llm_provider, embed_provider)

class LibraryCreate(BaseModel):
    ai_identity: str
    name: str
    description: str
    purpose: str
    config: Optional[dict] = {}

class IngestRequest(BaseModel):
    content: str
    source_name: str
    context: Optional[str] = ""

class SemanticAnalyzeRequest(BaseModel):
    text_a: str
    text_b: str

class RetrieveRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    category_filter: Optional[List[str]] = None

class ReconstructRequest(BaseModel):
    guidance: Optional[str] = "Organize logically based on data."
    dry_run: Optional[bool] = False

@app.get("/health")
def health_check():
    return {"status": "online", "engine": "SAFIRA v2 (Hybrid Library)", "active_provider": ACTIVE_PROVIDER.upper()}

# 1. Library Registry
@app.post("/api/libraries")
def create_library(req: LibraryCreate, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    lib_id = f"lib_{uuid.uuid4().hex[:8]}"
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO libraries (id, ai_identity, name, description, purpose, config, owner_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (lib_id, req.ai_identity, req.name, req.description, req.purpose, json.dumps(req.config), client_id, datetime.utcnow().isoformat())
    )
    db.commit()
    return {"status": "success", "library_id": lib_id}

@app.get("/api/libraries")
def list_libraries(client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM libraries WHERE owner_id=?", (client_id,))
    libraries = []
    for r in cursor.fetchall():
        lib = dict(r)
        lib.pop("owner_id", None)
        libraries.append(lib)
    return {"libraries": libraries}

@app.get("/api/libraries/{lib_id}/tree")
def get_tree(lib_id: str, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    cursor = db.cursor()
    tree = get_library_tree(cursor, lib_id)
    return {"library_id": lib_id, "categories": tree}

# Mode 1: Data Architect
@app.post("/api/libraries/{lib_id}/ingest")
def ingest_knowledge(lib_id: str, req: IngestRequest, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    try:
        return engine.ingest_knowledge(db, lib_id, req.content, req.source_name, req.context)
    except ValueError as e:
        if str(e) == 'Library not found': raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/libraries/{lib_id}/reconstruct")
def reconstruct_library(lib_id: str, req: ReconstructRequest, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    try:
        return engine.reconstruct_library(db, lib_id, req.guidance, req.dry_run)
    except ValueError as e:
        if str(e) == 'Library not found': raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/libraries/{lib_id}/retrieve")
def retrieve_knowledge(lib_id: str, req: RetrieveRequest, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
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
def semantic_analyze(req: SemanticAnalyzeRequest, client_id: str = Depends(verify_api_key)):
    try:
        return engine.semantic_analyze(req.text_a, req.text_b)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/libraries/{lib_id}/relations")
def get_library_relations(lib_id: str, client_id: str = Depends(verify_api_key), db: sqlite3.Connection = Depends(get_db)):
    verify_library_access(lib_id, client_id, db)
    cursor = db.cursor()
    cursor.execute("SELECT id FROM libraries WHERE id=?", (lib_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Library not found")
        
    cursor.execute("""
        SELECT 
            rel.id as relation_id,
            rel.relation_type,
            rel.reason,
            src.id as source_id,
            src.meaning as source_meaning,
            tgt.id as target_id,
            tgt.meaning as target_meaning
        FROM relationships rel
        JOIN records src ON rel.source_record_id = src.id
        JOIN records tgt ON rel.target_record_id = tgt.id
        WHERE rel.library_id = ?
    """, (lib_id,))
    relations = [dict(r) for r in cursor.fetchall()]
    return {"library_id": lib_id, "relations": relations}



