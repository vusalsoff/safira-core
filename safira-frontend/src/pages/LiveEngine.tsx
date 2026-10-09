import { useState, useEffect } from 'react';
import { Upload, FileText, Database, ShieldAlert, Cpu, CheckCircle2, XCircle, Search, Network } from 'lucide-react';
import { cn } from '../utils/cn';
import { safiraApi } from '../services/api';

export default function LiveEngine() {
  const [activeTab, setActiveTab] = useState<'ingestion' | 'reconstructor' | 'guardian' | 'relation' | 'retrieval'>('ingestion');
  const [health, setHealth] = useState<any>(null);
  const [libraries, setLibraries] = useState<any[]>([]);
  const [selectedLib, setSelectedLib] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // Ingest State
  const [ingestForm, setIngestForm] = useState({ content: '', source_name: '', context: '' });
  const [ingestResult, setIngestResult] = useState<any>(null);

  // Relation State
  const [relations, setRelations] = useState<any[]>([]);

  // Retrieval State
  const [retrievalQuery, setRetrievalQuery] = useState('');
  const [retrievalResults, setRetrievalResults] = useState<any>(null);

  // Guardian State
  const [guardianForm, setGuardianForm] = useState({ text_a: '', text_b: '' });
  const [guardianResult, setGuardianResult] = useState<any>(null);

  // Tree State
  const [treeData, setTreeData] = useState<any[]>([]);
  const [reconstructGuidance, setReconstructGuidance] = useState('');
  const [reconstructResult, setReconstructResult] = useState<any>(null);

  useEffect(() => {
    safiraApi.getEngineHealth().then(setHealth);
    fetchLibraries();
  }, []);

  const fetchLibraries = async () => {
    try {
      const data = await safiraApi.listLibraries();
      setLibraries(data.libraries || []);
      if (data.libraries && data.libraries.length > 0 && !selectedLib) {
        setSelectedLib(data.libraries[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (selectedLib) {
      safiraApi.getLibraryTree(selectedLib).then(data => setTreeData(data.categories || []));
      safiraApi.getLibraryRelations(selectedLib).then(data => setRelations(data.relations || [])).catch(() => setRelations([]));
    }
  }, [selectedLib, activeTab]);

  // ... (keeping other handlers as is until sidebar)
  const handleCreateLib = async () => {
    const name = prompt("Enter library name (e.g. Science AI):");
    if (!name) return;
    setLoading(true);
    await safiraApi.createLibrary({ ai_identity: name.replace(/\s+/g,'_'), name, description: "Demo Library", purpose: "General" });
    await fetchLibraries();
    setLoading(false);
  };

  const handleIngest = async (e: any) => {
    e.preventDefault();
    if (!selectedLib) return alert("Select a library first");
    setLoading(true);
    try {
      const res = await safiraApi.ingestData(selectedLib, ingestForm);
      setIngestResult(res);
      setIngestForm({ content: '', source_name: '', context: '' });
      // Refresh relations
      safiraApi.getLibraryRelations(selectedLib).then(data => setRelations(data.relations || []));
    } catch (e: any) {
      alert("Ingest failed: " + e.message);
    }
    setLoading(false);
  };

  const handleRetrieve = async (e: any) => {
    e.preventDefault();
    if (!selectedLib) return;
    setLoading(true);
    try {
      const res = await safiraApi.retrieveKnowledge(selectedLib, retrievalQuery);
      setRetrievalResults(res);
    } catch(e: any) {
      alert("Retrieve failed: " + e.message);
    }
    setLoading(false);
  };

  const handleSemantic = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await safiraApi.runSemanticAnalysis(guardianForm.text_a, guardianForm.text_b);
      setGuardianResult(res);
    } catch (e: any) {
      alert("Analysis failed");
    }
    setLoading(false);
  };
  
  const handleReconstruct = async (e: any) => {
    e.preventDefault();
    if (!selectedLib) return;
    setLoading(true);
    try {
      const res = await safiraApi.reconstructData(selectedLib, reconstructGuidance);
      setReconstructResult(res);
    } catch (e: any) {
      alert("Reconstruction failed");
    }
    setLoading(false);
  };

  const isConnected = health && health.status === 'online';

  return (
    <div className="max-w-7xl mx-auto px-4 py-20 relative z-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">Live Engine</h1>
          <p className="text-gray-400 text-lg max-w-2xl">Connects to real SAFIRA backend API to process enterprise and game-world knowledge.</p>
        </div>
        
        <div className="flex flex-col gap-2 items-end">
          <div className={cn("px-4 py-2 rounded-full border text-sm font-medium flex items-center gap-3 shrink-0 backdrop-blur-md",
            isConnected ? "bg-green-500/10 text-green-400 border-green-500/30" : "bg-red-500/10 text-red-400 border-red-500/30")}>
            <span className="relative flex h-2.5 w-2.5">
              <span className={cn("absolute inline-flex h-full w-full rounded-full opacity-75", isConnected ? "animate-ping bg-green-400" : "bg-red-400")}></span>
              <span className={cn("relative inline-flex rounded-full h-2.5 w-2.5", isConnected ? "bg-green-500" : "bg-red-500")}></span>
            </span>
            {isConnected ? `Connected: ${health.active_provider}` : 'Backend Not Connected'}
          </div>

          <div className="flex items-center gap-2">
            <select className="bg-surface border border-surface-border rounded-lg px-3 py-1 text-sm" 
                    value={selectedLib} onChange={e => setSelectedLib(e.target.value)}>
              {libraries.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
            </select>
            <button onClick={handleCreateLib} className="bg-primary/20 text-primary px-3 py-1 rounded-lg text-sm hover:bg-primary/30">
              + New Lib
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-8 min-h-[70vh]">
        {/* Sidebar Tabs */}
        <div className="w-full lg:w-72 shrink-0 flex flex-row lg:flex-col gap-3 overflow-x-auto pb-4 lg:pb-0 scrollbar-hide">
          {[
            { id: 'ingestion', label: 'Data Architect (Mode 1)', icon: <Upload className="w-5 h-5" /> },
            { id: 'reconstructor', label: 'Data Reconstructor (Mode 2)', icon: <Database className="w-5 h-5" /> },
            { id: 'guardian', label: 'Semantic Guardian (Mode 3)', icon: <ShieldAlert className="w-5 h-5" /> },
            { id: 'relation', label: 'Relation Engine (Mode 4)', icon: <Network className="w-5 h-5" /> },
            { id: 'retrieval', label: 'Precision Retrieval (Mode 5)', icon: <FileText className="w-5 h-5" /> },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "flex items-center gap-4 px-5 py-4 rounded-xl text-base font-medium transition-all text-left whitespace-nowrap lg:whitespace-normal",
                activeTab === tab.id 
                  ? "bg-primary text-white shadow-[0_0_20px_rgba(14,165,233,0.3)] border border-primary/50" 
                  : "glass-panel text-gray-400 hover:text-white hover:bg-white/5 border-transparent hover:border-surface-border"
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="flex-1 glass-panel p-6 md:p-10 flex flex-col relative overflow-hidden h-[70vh] overflow-y-auto">
          {loading && (
            <div className="absolute inset-0 bg-darker/50 backdrop-blur-sm z-50 flex items-center justify-center">
              <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}

          {activeTab === 'ingestion' && (
            <div className="relative z-10 w-full max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">Autonomous Knowledge Ingestion</h2>
              <form onSubmit={handleIngest} className="space-y-4">
                <div><label className="text-sm text-gray-400">Knowledge Content</label>
                  <textarea required value={ingestForm.content} onChange={e => setIngestForm({...ingestForm, content: e.target.value})} className="w-full bg-surface border border-surface-border rounded-lg p-3 mt-1 h-32"></textarea>
                </div>
                <div className="flex gap-4">
                  <div className="flex-1"><label className="text-sm text-gray-400">Source Name</label>
                    <input required value={ingestForm.source_name} onChange={e => setIngestForm({...ingestForm, source_name: e.target.value})} className="w-full bg-surface border border-surface-border rounded-lg p-3 mt-1"/>
                  </div>
                  <div className="flex-1"><label className="text-sm text-gray-400">Context Hint</label>
                    <input required value={ingestForm.context} onChange={e => setIngestForm({...ingestForm, context: e.target.value})} className="w-full bg-surface border border-surface-border rounded-lg p-3 mt-1"/>
                  </div>
                </div>
                <button type="submit" disabled={!isConnected} className="w-full bg-primary hover:bg-sky-400 text-white font-bold py-3 rounded-xl transition-all shadow-lg">Submit to SAFIRA</button>
              </form>

              {ingestResult && (
                <div className="mt-8 p-6 border border-green-500/30 bg-green-500/10 rounded-xl">
                  <div className="flex items-center gap-2 text-green-400 font-bold mb-2"><CheckCircle2/> Ingestion Successful</div>
                  <div className="text-sm text-gray-300"><strong>Extracted Meaning:</strong> {ingestResult.meaning}</div>
                  <div className="text-sm text-gray-300 mt-2"><strong>Categories Assessed:</strong> {JSON.stringify(ingestResult.categories)}</div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'reconstructor' && (
            <div className="relative z-10 w-full max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">Library Organization & Reconstruction</h2>
              
              <div className="mb-6 p-4 bg-surface rounded-xl border border-surface-border">
                <h3 className="font-bold text-gray-300 mb-2">Current Category Tree</h3>
                {treeData.length === 0 ? <p className="text-gray-500 text-sm">Empty library.</p> : (
                  <ul className="text-sm text-gray-400 list-disc pl-4">
                    {treeData.map(c => <li key={c.id}>{c.name} {c.parent_id ? '(Child)' : '(Root)'}</li>)}
                  </ul>
                )}
              </div>

              <form onSubmit={handleReconstruct} className="space-y-4">
                <div><label className="text-sm text-gray-400">Main AI Guidance (e.g. "Group all rules under Policy")</label>
                  <input required value={reconstructGuidance} onChange={e => setReconstructGuidance(e.target.value)} className="w-full bg-surface border border-surface-border rounded-lg p-3 mt-1"/>
                </div>
                <button type="submit" disabled={!isConnected} className="w-full bg-indigo-500 hover:bg-indigo-400 text-white font-bold py-3 rounded-xl transition-all shadow-lg">Propose Reconstruction (Dry Run)</button>
              </form>

              {reconstructResult && (
                <div className="mt-8 p-6 border border-indigo-500/30 bg-indigo-500/10 rounded-xl overflow-x-auto">
                   <h3 className="font-bold text-indigo-400 mb-2">Proposed Changes</h3>
                   <pre className="text-xs text-gray-300">{JSON.stringify(reconstructResult.proposed_changes, null, 2)}</pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'retrieval' && (
            <div className="relative z-10 w-full max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">Precision Knowledge Retrieval</h2>
              <form onSubmit={handleRetrieve} className="relative">
                <Search className="absolute left-4 top-4 text-gray-400" />
                <input required value={retrievalQuery} onChange={e => setRetrievalQuery(e.target.value)} placeholder="Ask a question..." className="w-full bg-surface border border-surface-border rounded-xl py-4 pl-12 pr-4 text-white"/>
                <button type="submit" className="absolute right-2 top-2 bg-primary px-4 py-2 rounded-lg text-white font-bold hover:bg-sky-400">Search</button>
              </form>

              <div className="mt-8 space-y-4">
                {retrievalResults?.results?.map((res: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-surface border border-surface-border hover:border-primary/50 transition-all">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded">Score: {res.relevance_score}</span>
                      <span className="text-xs text-gray-500">Cats: {res.categories.join(', ') || 'Root'}</span>
                    </div>
                    <p className="text-gray-200">{res.meaning}</p>
                    <p className="text-xs text-gray-500 mt-3">Source: {res.source_name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'relation' && (
            <div className="relative z-10 w-full max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">Relation Engine (Knowledge Graph)</h2>
              
              <div className="mb-6">
                 {relations.length === 0 ? (
                   <div className="p-8 text-center text-gray-500 border border-surface-border border-dashed rounded-xl bg-surface">
                     No relationships found in this library yet. Ingest multiple related facts.
                   </div>
                 ) : (
                   <div className="grid grid-cols-1 gap-4">
                     {relations.map((rel, idx) => (
                       <div key={idx} className="p-4 bg-surface border border-surface-border rounded-xl flex flex-col md:flex-row items-center gap-4 hover:border-primary/50 transition-colors">
                          <div className="flex-1 p-3 bg-darker/50 rounded-lg text-sm text-gray-300 border border-surface-border">
                            {rel.source_meaning}
                          </div>
                          
                          <div className="flex flex-col items-center justify-center shrink-0 w-32">
                            <span className="text-xs font-bold text-primary mb-1">{rel.relation_type}</span>
                            <div className="w-full h-px bg-gradient-to-r from-transparent via-primary to-transparent relative">
                               <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t-2 border-r-2 border-primary rotate-45"></div>
                            </div>
                            {rel.reason && <span className="text-[10px] text-gray-500 mt-1 text-center leading-tight">{rel.reason}</span>}
                          </div>

                          <div className="flex-1 p-3 bg-darker/50 rounded-lg text-sm text-gray-300 border border-surface-border">
                            {rel.target_meaning}
                          </div>
                       </div>
                     ))}
                   </div>
                 )}
              </div>
            </div>
          )}

          {activeTab === 'guardian' && (
            <div className="relative z-10 w-full max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">Semantic Guardian (Equivalence & Contradiction)</h2>
              <form onSubmit={handleSemantic} className="space-y-4">
                <div><label className="text-sm text-gray-400">Text A</label>
                  <textarea required value={guardianForm.text_a} onChange={e => setGuardianForm({...guardianForm, text_a: e.target.value})} className="w-full bg-surface border border-surface-border rounded-lg p-3 mt-1 h-24"></textarea>
                </div>
                <div><label className="text-sm text-gray-400">Text B</label>
                  <textarea required value={guardianForm.text_b} onChange={e => setGuardianForm({...guardianForm, text_b: e.target.value})} className="w-full bg-surface border border-surface-border rounded-lg p-3 mt-1 h-24"></textarea>
                </div>
                <button type="submit" disabled={!isConnected} className="w-full bg-amber-500 hover:bg-amber-400 text-white font-bold py-3 rounded-xl transition-all shadow-lg">Analyze Semantics</button>
              </form>

              {guardianResult && (
                 <div className={cn("mt-8 p-6 border rounded-xl", 
                    guardianResult.contradiction_detected ? "border-red-500/30 bg-red-500/10" : 
                    guardianResult.are_equivalent ? "border-green-500/30 bg-green-500/10" : "border-surface-border bg-surface")}>
                    <h3 className="font-bold mb-2">Analysis Results</h3>
                    <div className="text-sm space-y-2 text-gray-300">
                      <p><strong>Equivalent:</strong> {guardianResult.are_equivalent ? 'Yes ✅' : 'No ❌'}</p>
                      <p><strong>Contradicts:</strong> {guardianResult.contradiction_detected ? 'Yes ⚠️' : 'No ✅'}</p>
                      <p><strong>Notes:</strong> {guardianResult.differences_noted}</p>
                    </div>
                 </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
