# SAFIRA Frontend - NeuroBridge.SI Hackathon 2026

This is the frontend application for SAFIRA (Semantic Architecture for Information Refinement and Access), designed for the NeuroBridge.SI Hackathon. 

It is built with React, TypeScript, Vite, and Tailwind CSS.

## Getting Started

Since Node.js was not detected in the current environment, you will need to run this on a system that has Node.js (v18+) installed.

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and set your backend API URL:
```bash
cp .env.example .env
```
Ensure `VITE_SAFIRA_API_URL` points to your active SAFIRA backend engine.

### 3. Run Development Server
```bash
npm run dev
```

## Implemented Features (Priority 1)
- **Home Page**: Complete with Hero section, the 6 core AI knowledge problems, and workflow diagram.
- **Architecture (5 Modes)**: Visualized page detailing Data Architect, Data Reconstructor, Semantic Guardian, Relation Engine, and Precision Retrieval.
- **Live Engine (Demo Interface)**: An integration-ready interface for connecting the backend API. Currently handles UI states for Ingestion, Knowledge Explorer, and mock states for others to prove the concept.
- **API Client Layer**: Defined in `src/services/api.ts`, ready to be wired up to the real Python/backend API.

## Pending (Priority 2 & 3 - For further Hackathon iterations)
- Detailed Knowledge Graph Visualization (React Flow)
- Real-time Performance Metrics Dashboard
- Gaming Use Case Interface
