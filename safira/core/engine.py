import sqlite3
import uuid
import json
import math
from datetime import datetime
from typing import List, Optional, Dict, Any

def get_library_tree(cursor: sqlite3.Cursor, library_id: str) -> list:
    cursor.execute("SELECT * FROM categories WHERE library_id=?", (library_id,))
    cats = [dict(r) for r in cursor.fetchall()]
    return build_tree(cats, None)

def build_tree(cats: list, parent_id: Optional[str]) -> list:
    tree = []
    for c in cats:
        if c["parent_id"] == parent_id:
            node = dict(c)
            node["children"] = build_tree(cats, c["id"])
            tree.append(node)
    return tree

def validate_hierarchy(cursor: sqlite3.Cursor, library_id: str):
    cursor.execute("SELECT id, parent_id FROM categories WHERE library_id=?", (library_id,))
    cats = {r["id"]: r["parent_id"] for r in cursor.fetchall()}
    
    for cid, pid in cats.items():
        if pid is not None:
            if pid not in cats:
                raise ValueError(f"Category {cid} has nonexistent parent {pid}")
            if pid == cid:
                raise ValueError(f"Category {cid} cannot be its own parent")
            
            visited = set()
            curr = pid
            while curr is not None:
                if curr == cid:
                    raise ValueError(f"Circular dependency detected involving category {cid}")
                if curr in visited:
                    break
                visited.add(curr)
                curr = cats.get(curr)

def cosine_similarity(v1, v2):
    if not v1 or not v2: return None
    if len(v1) != len(v2): return None
    try:
        dot = sum(float(a) * float(b) for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(float(a) * float(a) for a in v1))
        norm2 = math.sqrt(sum(float(b) * float(b) for b in v2))
        if norm1 <= 0.0 or norm2 <= 0.0: return None
        return dot / (norm1 * norm2)
    except (ValueError, TypeError, OverflowError):
        return None

class SafiraEngine:
    def __init__(self, llm_provider, embed_provider):
        self.llm = llm_provider
        self.embed = embed_provider

    def ingest_knowledge(self, db: sqlite3.Connection, lib_id: str, content: str, source_name: str, context: str) -> dict:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM libraries WHERE id=?", (lib_id,))
        lib = cursor.fetchone()
        if not lib: raise ValueError("Library not found")
        
        tree = get_library_tree(cursor, lib_id)
        
        prompt = f"""You are SAFIRA Data Architect for library: {lib['name']}. Purpose: {lib['purpose']}.
Current Category Tree: {json.dumps(tree)}
New Knowledge: {content}
Context: {context}

Analyze the knowledge. Extract its core meaning. Decide where to place it in the hierarchy.
CRITICAL INSTRUCTION: If the Current Category Tree is empty, or no existing category matches perfectly, you MUST propose a 'new' category to place this in. DO NOT leave placements empty.
Return JSON ONLY:
{{
   "extracted_meaning": "string",
   "placements": [
      {{"type": "new", "name": "CategoryName", "description": "Category Description", "parent_id": null}}
   ]
}}"""
        ai_data = {}
        meaning = content
        embedding_json = "[]"
        
        for attempt in range(2):
            try:
                ai_data = self.llm.call_json(prompt)
                meaning = ai_data.get("extracted_meaning", content)
                placements = ai_data.get("placements", [])
                if isinstance(placements, dict):
                    placements = [placements]
                    ai_data["placements"] = placements
                if len(placements) > 0:
                    break
            except Exception as e:
                if attempt == 1:
                    raise Exception(f"LLM extraction failed: {str(e)}")
                continue

        try:
            emb = self.embed.get_embedding(meaning)
            if emb: embedding_json = json.dumps(emb)
        except Exception as e:
            pass

        record_id = f"rec_{uuid.uuid4().hex[:8]}"
        try:
            cursor.execute(
                "INSERT INTO records (id, library_id, original_expression, meaning, context, source_metadata, verification_status, embedding, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (record_id, lib_id, content, meaning, context, source_name, "unverified", embedding_json, datetime.utcnow().isoformat())
            )
            
            placed_categories = []
            for p in ai_data.get("placements", []):
                cat_id = None
                if p.get("type") == "existing":
                    cat_id = p.get("id")
                elif p.get("type") == "new":
                    cat_id = f"cat_{uuid.uuid4().hex[:8]}"
                    parent_id = p.get("parent_id")
                    
                    cursor.execute("SELECT id FROM categories WHERE id=? AND library_id=?", (parent_id, lib_id))
                    if parent_id and not cursor.fetchone():
                        db.rollback()
                        raise ValueError(f"Invalid parent_id: {parent_id}")
                        
                    cursor.execute(
                        "INSERT INTO categories (id, library_id, parent_id, name, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (cat_id, lib_id, parent_id, p.get("name"), p.get("description"), datetime.utcnow().isoformat())
                    )
                
                if cat_id:
                    cursor.execute("INSERT OR IGNORE INTO record_categories (record_id, category_id) VALUES (?, ?)", (record_id, cat_id))
                    placed_categories.append(cat_id)
            
            validate_hierarchy(cursor, lib_id)
            db.commit()
            return {
                "record_id": record_id,
                "extracted_meaning": meaning,
                "categories_assessed": placed_categories,
                "status": "success"
            }
        except Exception as e:
            db.rollback()
            raise e

    def reconstruct_library(self, db: sqlite3.Connection, lib_id: str, guidance: str, dry_run: bool) -> dict:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM libraries WHERE id=?", (lib_id,))
        lib = cursor.fetchone()
        if not lib: raise ValueError("Library not found")

        tree = get_library_tree(cursor, lib_id)
        
        prompt = f"""You are SAFIRA Data Reconstructor for library: {lib['name']}.
Current Category Tree: {json.dumps(tree)}
Guidance: {guidance}

Propose a better category structure. You may merge, rename, or regroup categories.
CRITICAL INSTRUCTION: Return ONLY JSON.
{{
   "proposed_changes": [
      {{"action": "create", "id": "temp_1", "name": "New Cat", "parent_id": null}},
      {{"action": "move_category", "id": "existing_cat_id", "new_parent_id": "temp_1"}},
      {{"action": "move_records", "from_category_id": "existing_cat_id", "to_category_id": "temp_1"}}
   ]
}}"""
        try:
            ai_data = self.llm.call_json(prompt)
        except Exception as e:
            raise Exception(f"LLM reconstruction failed: {str(e)}")

        if dry_run:
            return {"status": "proposed", "proposed_changes": ai_data.get("proposed_changes", [])}

        try:
            changes = ai_data.get("proposed_changes", [])
            id_map = {}
            for c in changes:
                act = c.get("action")
                if act == "create":
                    temp_id = c.get("id")
                    real_id = f"cat_{uuid.uuid4().hex[:8]}"
                    id_map[temp_id] = real_id
                    
                    parent_id = c.get("parent_id")
                    if parent_id in id_map: parent_id = id_map[parent_id]
                    
                    cursor.execute("INSERT INTO categories (id, library_id, parent_id, name, created_at) VALUES (?, ?, ?, ?, ?)",
                                   (real_id, lib_id, parent_id, c.get("name"), datetime.utcnow().isoformat()))
                elif act == "move_category":
                    cat_id = id_map.get(c.get("id"), c.get("id"))
                    new_parent_id = id_map.get(c.get("new_parent_id"), c.get("new_parent_id"))
                    cursor.execute("UPDATE categories SET parent_id=? WHERE id=? AND library_id=?", (new_parent_id, cat_id, lib_id))
                elif act == "move_records":
                    from_cat = id_map.get(c.get("from_category_id"), c.get("from_category_id"))
                    to_cat = id_map.get(c.get("to_category_id"), c.get("to_category_id"))
                    
                    cursor.execute("SELECT id FROM categories WHERE id=? AND library_id=?", (to_cat, lib_id))
                    if not cursor.fetchone():
                        raise ValueError(f"Category {to_cat} does not exist in library")
                        
                    cursor.execute("UPDATE record_categories SET category_id=? WHERE category_id=? AND record_id IN (SELECT id FROM records WHERE library_id=?)", 
                                   (to_cat, from_cat, lib_id))
            
            validate_hierarchy(cursor, lib_id)
            db.commit()
            return {"status": "applied", "changes_made": changes}
        except Exception as e:
            db.rollback()
            raise ValueError(f"Reconstruction failed: {str(e)}")

    def retrieve_knowledge(self, db: sqlite3.Connection, lib_id: str, query: str, max_results: int = 5, category_filter: list = None) -> dict:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM libraries WHERE id=?", (lib_id,))
        if not cursor.fetchone(): raise ValueError("Library not found")

        start_time = datetime.utcnow()
        try:
            query_emb = self.embed.get_embedding(query)
            if not query_emb: raise Exception("Received empty embedding vector from provider")
        except Exception as e:
            raise Exception(f"Embedding provider failure: {str(e)}")

        cursor.execute("SELECT r.* FROM records r WHERE r.library_id=?", (lib_id,))
        rows = cursor.fetchall()
        
        cursor.execute("SELECT id, name, parent_id FROM categories WHERE library_id=?", (lib_id,))
        all_cats = {c["id"]: dict(c) for c in cursor.fetchall()}
        
        scored_results = []
        for r in rows:
            db_emb_raw = r["embedding"]
            db_emb = []
            try:
                if db_emb_raw and db_emb_raw != "[]":
                    db_emb = json.loads(db_emb_raw)
            except json.JSONDecodeError:
                pass
                
            score = cosine_similarity(query_emb, db_emb)
            if score is None: continue
                
            cursor.execute("SELECT category_id FROM record_categories WHERE record_id=?", (r["id"],))
            cat_ids = [c["category_id"] for c in cursor.fetchall()]
            
            if category_filter and len(category_filter) > 0:
                if not any(cat in category_filter for cat in cat_ids): continue
            
            paths = []
            for cid in cat_ids:
                path = []
                curr = cid
                while curr and curr in all_cats:
                    path.insert(0, all_cats[curr]["name"])
                    curr = all_cats[curr]["parent_id"]
                if path:
                    paths.append(" > ".join(path))

            cursor.execute("SELECT target_record_id FROM relationships WHERE source_record_id=? AND library_id=?", (r["id"], lib_id))
            related = [rel["target_record_id"] for rel in cursor.fetchall()]

            if score > 0.0:
                scored_results.append({
                    "record_id": r["id"],
                    "library_id": lib_id,
                    "meaning": r["meaning"],
                    "source_metadata": r["source_metadata"],
                    "category_ids": cat_ids,
                    "categories": paths,
                    "related_records": related,
                    "relevance_score": round(score, 4),
                    "scoring_method": "cosine_similarity"
                })

        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        final_results = scored_results[:max_results]
        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "query": query,
            "results": final_results,
            "metadata": {
                "retrieval_time_ms": int(elapsed),
                "total_matches_found": len(scored_results)
            }
        }

    def semantic_analyze(self, text_a: str, text_b: str) -> dict:
        prompt = f"""You are SAFIRA Semantic Guardian. Analyze the two provided texts. 
Determine if they are semantically equivalent. Treat texts as equivalent if they convey the exact same underlying rule, fact, or instruction, even if they use different words or synonyms (e.g. 'employees' = 'staff', 'in the office' = 'on-site', '3 days per week' = 'three days weekly').
Also detect if they explicitly contradict each other. Do not force equivalence if there are meaningful differences.
Return ONLY valid JSON with exactly these keys: 
"are_equivalent" (boolean), 
"contradiction_detected" (boolean), 
"similarity_score" (float between 0.0 and 1.0), 
"differences_noted" (string)

Text A: {text_a}
Text B: {text_b}"""
        return self.llm.call_json(prompt)

    def get_library_relations(self, db: sqlite3.Connection, lib_id: str) -> dict:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM libraries WHERE id=?", (lib_id,))
        if not cursor.fetchone(): raise ValueError("Library not found")
            
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
