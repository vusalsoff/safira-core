import { Users, Info, Rocket } from 'lucide-react';

export default function About() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-20 relative z-10">
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold mb-6 tracking-tight">About SAFIRA</h1>
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary/30 bg-primary/10 text-primary text-sm font-medium">
          NeuroBridge.SI Hackathon 2026
        </div>
      </div>

      <div className="space-y-8">
        <div className="glass-panel p-10 hover:border-primary/50 transition-colors">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3"><Info className="text-primary w-8 h-8" /> Project Overview</h2>
          <p className="text-gray-300 leading-relaxed text-lg">
            SAFIRA (Semantic Architecture for Information Refinement and Access) is a universal, modular AI knowledge infrastructure engine. 
            It is designed to organize, restructure, refine, connect, preserve, and precisely retrieve information for artificial intelligence systems. 
            It is not a standalone chatbot, but a specialized subordinate engine that sits behind a Main AI to improve how it manages and accesses knowledge.
          </p>
        </div>

        <div className="glass-panel p-10 hover:border-primary/50 transition-colors">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3"><Rocket className="text-primary w-8 h-8" /> Development Objective</h2>
          <p className="text-gray-300 leading-relaxed text-lg mb-4">
            The long-term objective is to build a reusable knowledge infrastructure engine that can operate as an independent component or as one module within a larger AI architecture.
          </p>
          <p className="text-gray-300 leading-relaxed text-lg">
            This frontend serves to demonstrate the architectural concepts, the 5 operating modes, and provides an integration interface for the live SAFIRA backend engine being developed concurrently.
          </p>
        </div>

        <div className="glass-panel p-10 hover:border-primary/50 transition-colors">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3"><Users className="text-primary w-8 h-8" /> Technical Transparency</h2>
          <ul className="space-y-4 text-gray-300 text-lg">
            <li className="flex items-start gap-4">
              <span className="text-primary mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0 shadow-[0_0_8px_rgba(14,165,233,0.8)]"></span>
              <span>SAFIRA does not replace reasoning performed by the Main AI.</span>
            </li>
            <li className="flex items-start gap-4">
              <span className="text-primary mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0 shadow-[0_0_8px_rgba(14,165,233,0.8)]"></span>
              <span>SAFIRA is not restricted to any single application domain (handles both Enterprise and Gaming).</span>
            </li>
            <li className="flex items-start gap-4">
              <span className="text-primary mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0 shadow-[0_0_8px_rgba(14,165,233,0.8)]"></span>
              <span>All claimed performance advantages will be evaluated through rigorous testing when connected to the live backend.</span>
            </li>
            <li className="flex items-start gap-4">
              <span className="text-primary mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0 shadow-[0_0_8px_rgba(14,165,233,0.8)]"></span>
              <span>No AI outputs or test results on this frontend are fabricated. Unconnected features explicitly show a "Preview" state.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
