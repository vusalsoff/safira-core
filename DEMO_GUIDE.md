# SAFIRA v2.0 - Final Demonstration Guide

## Startup Commands
1. Start the Ollama server for LLM operations:
   `ollama serve` (ensure qwen2.5:3b is pulled)
2. Start the FastAPI backend:
   `.\venv\Scripts\activate`
   `uvicorn main:app --host 0.0.0.0 --port 8000`
3. Start the Vite React Frontend:
   `npm run dev`

## API Authentication Overview
SAFIRA validates clients via Bearer tokens. Each AI client is assigned a unique `api_key` generated via `python provision_client.py "Client Name"`. The keys are hashed in the database.

## Two-Client Demonstration Sequence
Use the included test scripts to demonstrate true isolation:
- `python demo_client_science.py <API_KEY_A>` (Simulates Scientific Research AI)
- `python demo_client_gaming.py <API_KEY_B>` (Simulates Gaming World AI)
Both clients can query their respective libraries, but their data remains entirely segregated in the `safira.db` SQLite backend.

## Five-Mode Demonstration Sequence
1. **Mode 1: Data Architect**: Use `/api/libraries/{id}/ingest` to ingest unstructured knowledge.
2. **Mode 2: Data Reconstructor**: Use `/api/libraries/{id}/reconstruct` to safely propose and apply category structures.
3. **Mode 3: Semantic Guardian**: Use `/api/semantic/analyze` to detect equivalent or conflicting knowledge.
4. **Mode 4: Relation Engine**: Use `/api/libraries/{id}/relations` to explore node-edge relationships.
5. **Mode 5: Precision Retrieval**: Use `/api/libraries/{id}/retrieve` to search exact embeddings (using Gemini) and retrieve full category paths.

## Known Limitations
- The current embedding logic requires `google-generativeai` and a valid API key, failing securely (HTTP 502) if unreachable.
- Frontend interface requires manual API key configuration in `.env` if bypassing local proxy.

## Troubleshooting
If a client receives HTTP 401, verify the API key generated matches the database hash.
If HTTP 502 occurs during ingestion or retrieval, verify the Gemini API key is valid in the backend `.env`.

