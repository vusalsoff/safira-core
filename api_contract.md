# SAFIRA Engine - Hybrid Logical Library API Contract (v2.0)

This system provides logically isolated, dynamically hierarchical knowledge libraries for different Main AI instances.

## 0. Authentication & Authorization (Phase 3 Security)

SAFIRA requires secure API Key authentication for all endpoints (except `/health`). 

### Authentication Requirements
- **Bearer Token Format:** You must provide your key in the HTTP Header: `Authorization: Bearer sk_safira_...`
- **HTTP 401 vs 403:**
  - `401 Unauthorized`: Missing API key, invalid API key, or revoked API key.
  - `403 Forbidden`: Valid API key, but attempting to access a library owned by another client.

### Client Provisioning & Key Revocation
Clients cannot generate keys via the API. System administrators must provision clients using the offline CLI script:
```bash
python provision_client.py "Main_AI_Science_Client"
```
This generates an API key. Only cryptographic hashes are stored. To revoke a key, administrators manually update the `api_clients` table (`is_revoked = 1`).

### Library Ownership & Migration Considerations
- **Ownership Check:** Any library created under a client's API key is owned permanently by that client.
- **Strict Isolation:** Client A cannot read, write, reconstruct, or retrieve data from Client B's library.
- **Legacy Migration:** Libraries created before v2.0 (Phase 3) have no owner (`owner_id` is NULL). For security, they are blocked from all client access. Administrators must manually map legacy libraries to clients by running `UPDATE libraries SET owner_id = ? WHERE id = ?`.

## 1. Libraries (Registry)

### `POST /api/libraries`
Create a new isolated library for a specific AI.
**Request:**
```json
{
  "ai_identity": "ScienceAI_01",
  "name": "Global Scientific Knowledge Base",
  "description": "Library for storing strict scientific facts.",
  "purpose": "Analyze physics, genetics, and thermodynamics."
}
```
**Response:**
```json
{
  "status": "success",
  "library_id": "lib_3f92d1c"
}
```

### `GET /api/libraries/{lib_id}/tree`
Retrieve the autonomous hierarchical category tree for a library.
**Response:**
```json
{
  "library_id": "lib_3f92d1c",
  "categories": [
    {"id": "cat_1", "parent_id": null, "name": "Physics"},
    {"id": "cat_2", "parent_id": "cat_1", "name": "Quantum Mechanics"}
  ]
}
```

---

## 2. Ingestion (Mode 1 & 4)

### `POST /api/libraries/{lib_id}/ingest`
Analyzes knowledge, automatically generates/selects hierarchical categories within the AI's isolated library, maps embeddings, and creates context relationships.
**Request:**
```json
{
  "content": "Quantum entanglement links particles instantly across space.",
  "source_name": "Physics Jnl",
  "context": "Quantum Mechanics"
}
```
**Response:**
```json
{
  "status": "success",
  "record_id": "rec_91f4a",
  "categories": ["cat_2"],
  "meaning": "Particles can be instantly linked across space via quantum entanglement."
}
```

---

## 3. Data Reconstructor (Mode 2 - Guided)

### `POST /api/libraries/{lib_id}/reconstruct`
Analyzes the existing hierarchy. Reorganizes the tree (moves, renames, merges) based on autonomous logic and Main AI guidance.
**Request:**
```json
{
  "guidance": "Group all Lore under a single Root Category called 'Lore'.",
  "dry_run": false
}
```
**Response:**
```json
{
  "status": "success",
  "applied_changes": {
    "new_categories": [{"temp_id": "temp_lore", "name": "Lore", "parent_id": null}],
    "category_moves": [{"category_id": "cat_kingdoms", "new_parent_id": "temp_lore"}],
    "record_reassignments": []
  }
}
```

---

## 4. Precision Retrieval (Mode 5)

### `POST /api/libraries/{lib_id}/retrieve`
Strictly scoped embedding retrieval. The engine will NEVER return results from another library.
**Request:**
```json
{
  "query": "Who rules the north?"
}
```
**Response:**
```json
{
  "library_id": "lib_gaming99",
  "results": [
    {
      "record_id": "rec_abc",
      "meaning": "King Alaric rules the Northern Wastes.",
      "categories": ["Kingdoms"],
      "source_name": "World Map",
      "relevance_score": 0.9412
    }
  ]
}
```
*(Returns HTTP 404 "Library not found" if an invalid `lib_id` is passed).*

## 5. Relation Engine (Mode 4)

### `GET /api/libraries/{lib_id}/relations`
Retrieve all knowledge relationships within a library.

**Response (200):**
```json
{
  "library_id": "lib_3f92d1c",
  "relations": [
    {
      "relation_id": "rel_abc",
      "relation_type": "SHARES_CONTEXT",
      "reason": null,
      "source_id": "rec_1",
      "source_meaning": "Knowledge A",
      "target_id": "rec_2",
      "target_meaning": "Knowledge B"
    }
  ]
}
```
*(Returns HTTP 404 "Library not found" if an invalid `lib_id` is passed).*
