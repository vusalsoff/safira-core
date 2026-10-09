const API_URL = import.meta.env.VITE_SAFIRA_API_URL || 'http://localhost:8000/api';

async function authFetch(url: string, options: RequestInit = {}) {
  options.credentials = 'include'; // Send HttpOnly cookie
  let res = await fetch(url, options);
  if (res.status === 401) {
    const key = prompt("Authentication required. Please enter your SAFIRA API Key:");
    if (key) {
      const loginRes = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${key}` },
        credentials: 'omit' // Send header, get cookie
      });
      if (loginRes.ok) {
        // Retry original request
        res = await fetch(url, options);
      } else {
        alert("Invalid API Key");
      }
    }
  }
  return res;
}

export const safiraApi = {
  // Library Registry
  listLibraries: async () => {
    const res = await authFetch(`${API_URL}/libraries`);
    if (!res.ok) throw new Error('Failed to fetch libraries');
    return res.json();
  },
  
  createLibrary: async (data: { ai_identity: string, name: string, description: string, purpose: string }) => {
    const res = await authFetch(`${API_URL}/libraries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create library');
    return res.json();
  },

  getLibraryTree: async (libId: string) => {
    const res = await authFetch(`${API_URL}/libraries/${libId}/tree`);
    if (!res.ok) throw new Error('Failed to fetch tree');
    return res.json();
  },

  // Mode 1: Data Architect
  ingestData: async (libId: string, data: { content: string, source_name: string, context: string }) => {
    const res = await authFetch(`${API_URL}/libraries/${libId}/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to ingest');
    return res.json();
  },

  // Mode 2: Data Reconstructor
  reconstructData: async (libId: string, guidance: string) => {
    const res = await authFetch(`${API_URL}/libraries/${libId}/reconstruct`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ guidance, dry_run: true }) // using dry_run for demo safety
    });
    if (!res.ok) throw new Error('Failed to reconstruct');
    return res.json();
  },

  // Mode 3: Semantic Guardian
  runSemanticAnalysis: async (text_a: string, text_b: string) => {
    const res = await authFetch(`${API_URL}/semantic/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text_a, text_b })
    });
    if (!res.ok) throw new Error('Failed semantic analysis');
    return res.json();
  },

  // Mode 4: Relation Engine
  getLibraryRelations: async (libId: string) => {
    const res = await authFetch(`${API_URL}/libraries/${libId}/relations`);
    if (!res.ok) throw new Error('Failed to fetch relations');
    return res.json();
  },

  // Mode 5: Precision Retrieval
  retrieveKnowledge: async (libId: string, query: string) => {
    const res = await authFetch(`${API_URL}/libraries/${libId}/retrieve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, max_results: 5 })
    });
    if (!res.ok) throw new Error('Failed to retrieve');
    return res.json();
  },

  // Health
  getEngineHealth: async () => {
    try {
      const res = await authFetch('http://localhost:8000/health');
      if (!res.ok) return { status: 'disconnected' };
      return res.json();
    } catch (e) {
      return { status: 'disconnected' };
    }
  }
};

