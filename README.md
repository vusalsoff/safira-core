<div align="center">
  <img src="https://via.placeholder.com/150/090a0f/00d2ff?text=SAFIRA" alt="SAFIRA Logo" width="120" height="120" />
  <h1>SAFIRA Knowledge Engine</h1>
  <p><strong>Universal, Secure, and Hybrid Knowledge Infrastructure for Autonomous AI Systems</strong></p>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
  [![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge)](https://ollama.ai/)
  [![Gemini](https://img.shields.io/badge/Gemini-Embeddings-blue?style=for-the-badge)](https://deepmind.google/technologies/gemini/)
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
</div>

<br/>

## ?? Overview

**SAFIRA** is not just another chatbot—it is a domain-agnostic, enterprise-grade **Knowledge Infrastructure Engine** designed specifically for external Main AIs. It transforms unstructured text into dynamic, heavily interconnected semantic graphs while maintaining strict boundaries across independent intelligence systems. 

Built with an abstraction-first architecture, SAFIRA dynamically orchestrates local LLM inference (via **Ollama**) for semantic parsing and cloud-based embeddings (via **Google Gemini**) for ultra-precise retrieval, operating completely behind a robust, authenticated HTTP API.

---

## ?? The 5 Engines of SAFIRA

SAFIRA operates on five distinct, highly optimized internal engines:

1. **?? Data Architect (Ingestion)**  
   *The builder.* Accepts unstructured knowledge, interprets semantic meaning using local LLMs, and autonomously structures the data into a hierarchical category tree dynamically built on the fly.
2. **?? Data Reconstructor (Structuring)**  
   *The architect.* Scans existing libraries and proposes structural optimizations. Features a safe `dry-run` transaction mechanism before committing massive relational changes.
3. **?? Semantic Guardian (Integrity Check)**  
   *The protector.* Evaluates new knowledge against existing records. It accurately detects semantic equivalences and stark contradictions to prevent AI hallucination loops.
4. **?? Relation Engine (Graph Mapping)**  
   *The linker.* Extracts and explicitly defines typed relationships (e.g., `contradicts`, `supports`, `expands_on`) between atomic pieces of knowledge across the graph.
5. **?? Precision Retrieval (Vector Search)**  
   *The oracle.* Leverages high-dimensional vector embeddings (Gemini) mixed with cosine-similarity ranking to fetch the exact semantic nodes and their full hierarchical paths instantly.

---

## ?? Enterprise-Grade Architecture

* **Strict Multi-Tenant Isolation:** Complete data segregation using Cryptographic Bearer Tokens. "Client A" cannot query, reconstruct, or even detect the presence of "Client B"'s library.
* **Provider Abstraction:** The `SafiraEngine` is completely decoupled from the specific AI models. Switching from `Ollama (qwen2.5)` to `OpenAI` or `Anthropic` requires zero changes to the core business logic.
* **Atomic Transactions:** Deeply nested category restructurings and database rewrites are wrapped in SQLite transactional blocks. If an AI fails mid-generation, SAFIRA rolls back instantly to protect data integrity.

---

## ?? Quick Start

### 1. Requirements
* Python 3.10+
* Node.js (for the React Frontend)
* [Ollama](https://ollama.ai/) installed locally (pull the `qwen2.5:3b` model: `ollama run qwen2.5:3b`)
* A Google Gemini API Key

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/safira.git
cd safira

# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Set your Gemini API Key in .env
echo "GOOGLE_API_KEY=your_key_here" > .env

# Provision your first API Key for testing
python provision_client.py "Master Client"

# Start the Engine
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
# Open a new terminal
cd frontend
npm install
npm run dev
```

---

## ?? Testing

SAFIRA ships with a massive, independent test suite guaranteeing 100% operational integrity across its pipelines.
```bash
python test_integration.py
python test_security.py
python test_isolation_regression.py
python test_hierarchy_integrity.py
python test_retrieval.py
```
*Current Coverage: 70/70 passing (Integration, Graph Security, Provider Isolation).*

---

## ?? License
This project is licensed under the MIT License.
