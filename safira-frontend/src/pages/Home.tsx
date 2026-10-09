import { useState, useEffect } from 'react';
import { ArrowRight, Database, Network, Search, Cpu, Play, Square, RotateCcw, Shield, Target, Zap, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';

const words = [
  { full: 'Semantic', letter: 'S' },
  { full: 'Architecture', letter: 'A' },
  { full: 'For', letter: 'F' },
  { full: 'Information', letter: 'I' },
  { full: 'Refinement', letter: 'R' },
  { full: 'Access', letter: 'A' }
];

export default function Home() {
  // phase 0: vertical stacked, phase 1: trailing text fades, phase 2: merge horizontal small, phase 3: zoom
  const [phase, setPhase] = useState<0 | 1 | 2 | 3>(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let timer1: any, timer2: any, timer3: any;
    if (isPlaying && phase === 0) {
      // Step 1: Fade out trailing letters
      setPhase(1);
      timer1 = setTimeout(() => {
        // Step 2: Merge into small SAFIRA
        setPhase(2);
        
        timer2 = setTimeout(() => {
          // Step 3: Fade in Zoom Big
          setPhase(3);
          setIsPlaying(false); // sequence finished
        }, 1500);

      }, 2500);
    }
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [isPlaying, phase]);

  const handlePlay = () => {
    if (phase >= 2) {
      setPhase(0);
      setTimeout(() => setIsPlaying(true), 100);
    } else {
      setIsPlaying(true);
    }
  };

  const handleReset = () => {
    setIsPlaying(false);
    setPhase(0);
  };

  return (
    <div className="w-full relative z-10">
      {/* Hero Section */}
      <section className="relative px-4 pt-24 pb-20 max-w-7xl mx-auto flex flex-col items-center text-center overflow-hidden min-h-[80vh] justify-center">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-dark to-darker pointer-events-none" />
        
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-medium animate-float backdrop-blur-md">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
          </span>
          NeuroBridge.SI Hackathon 2026
        </div>

        {/* Animation Container */}
        <div className="relative w-full flex flex-col items-center justify-center h-[250px] sm:h-[200px] md:h-[160px] lg:h-[120px] my-2">
          
          <motion.div 
            layout
            animate={{ scale: phase === 3 ? 3 : 1 }}
            transition={{ layout: { duration: 1.5, type: "spring", bounce: 0.15 }, scale: { duration: 3, ease: "easeInOut" } }}
            className={cn(
              "flex flex-row flex-wrap items-center justify-center max-w-6xl",
              phase >= 2 ? "gap-0" : "gap-x-4 md:gap-x-6 gap-y-4"
            )}
          >
            {words.map((w, idx) => (
              <motion.div 
                layout 
                transition={{ layout: { duration: 2, ease: "easeInOut" } }} 
                key={idx} 
                className={cn(
                  "flex items-center",
                  phase >= 2 && idx > 0 ? "-ml-3 md:-ml-6 lg:-ml-10" : ""
                )}
              >
                <motion.span 
                  layout
                  transition={{ layout: { duration: 2, ease: "easeInOut" } }}
                  className={cn(
                    "bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-100 to-gray-500 drop-shadow-[0_0_15px_rgba(255,255,255,0.2)] font-extrabold tracking-tighter",
                    phase >= 2 ? "text-6xl md:text-7xl lg:text-8xl" : "text-4xl md:text-5xl lg:text-6xl"
                  )}
                  style={{ transformOrigin: "center center" }}
                >
                  {w.letter}
                </motion.span>
                
                <AnimatePresence>
                  {phase < 2 && (
                    <motion.span
                      layout
                      initial={{ opacity: 1, width: 'auto', filter: 'blur(0px)' }}
                      animate={{ 
                        opacity: phase === 1 ? 0 : 1, 
                        width: phase === 1 ? 0 : 'auto',
                        filter: phase === 1 ? 'blur(10px)' : 'blur(0px)'
                      }}
                      exit={{ opacity: 0, width: 0 }}
                      transition={{ duration: 2, ease: "easeInOut", layout: { duration: 1.5, type: "spring", bounce: 0.15 } }}
                      className="block bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-100 to-gray-500 text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight overflow-hidden"
                      style={{ whiteSpace: 'nowrap' }}
                    >
                      {w.full.slice(1)}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </motion.div>

        </div>

        {/* Media Controls */}
        <div className="flex items-center justify-center gap-4 mt-8 bg-surface border border-surface-border p-2 rounded-2xl backdrop-blur-md shadow-2xl relative z-20">
          <button 
            onClick={handlePlay}
            disabled={isPlaying}
            className={`p-3 rounded-xl flex items-center gap-2 font-semibold transition-all ${isPlaying ? 'bg-surface text-gray-500' : 'bg-primary text-white hover:bg-primary/80 shadow-[0_0_15px_rgba(14,165,233,0.4)]'}`}
          >
            <Play className="w-5 h-5 fill-current" /> Play Intro
          </button>
          <button 
            onClick={handleReset}
            className="p-3 rounded-xl flex items-center gap-2 bg-surface hover:bg-white/10 text-gray-300 transition-all font-semibold"
          >
            <RotateCcw className="w-5 h-5" /> Reset
          </button>
        </div>


        <p className="text-lg md:text-xl text-primary font-medium mt-12 mb-12 flex items-center gap-2">
          Intelligence needs knowledge. <span className="text-white/50">•</span> Knowledge needs architecture.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center max-w-lg relative z-20">
          <Link to="/engine" className="group flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-primary text-white font-semibold hover:bg-primary/90 transition-all shadow-[0_0_30px_rgba(14,165,233,0.3)] hover:shadow-[0_0_40px_rgba(14,165,233,0.5)] hover:-translate-y-1">
            Launch Engine Demo
            <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link to="/modes" className="flex items-center justify-center gap-3 px-8 py-4 rounded-xl border border-surface-border glass-panel hover:bg-white/10 transition-all hover:-translate-y-1 font-semibold text-gray-300 hover:text-white">
            Explore Architecture
          </Link>
        </div>
      </section>

      {/* Master Level Feature Sections - Simple, Elegant, Image & Text */}
      <section className="py-32 relative border-t border-surface-border bg-darker/80 backdrop-blur-3xl overflow-hidden">
        
        <div className="max-w-7xl mx-auto px-4 relative z-10 mb-32">
          <div className="text-center">
            <h2 className="text-4xl md:text-6xl font-black mb-6 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-500">
              The Architecture of Truth
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg leading-relaxed">
              We eliminated complex bento boxes and abstract grids. SAFIRA operates on three fundamental pillars to guarantee AI precision.
            </p>
          </div>
        </div>

        {/* Feature 1: Data Architect */}
        <div className="max-w-7xl mx-auto px-4 relative z-10 mb-40">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="w-full lg:w-1/2">
              <div className="relative rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(14,165,233,0.2)] group border border-surface-border">
                <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity duration-700 z-10 Mix-blend-overlay"></div>
                <img src="/safira_data_architect.jpg" alt="Data Architect" className="w-full h-auto object-cover transform group-hover:scale-105 transition-transform duration-1000" />
              </div>
            </div>
            <div className="w-full lg:w-1/2">
              <div className="flex items-center gap-4 mb-6">
                <div className="h-12 w-12 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center text-primary">
                  <Database className="w-6 h-6" />
                </div>
                <span className="text-primary font-bold tracking-widest uppercase text-sm">Pillar 01</span>
              </div>
              <h3 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">Data Architect</h3>
              <p className="text-gray-400 text-lg md:text-xl leading-relaxed mb-8">
                Raw data is chaotic. Before the Main AI can even begin to think, SAFIRA intercepts millions of unstructured files, databases, and logs. It magically organizes them into a glowing, flawless semantic grid.
              </p>
              <ul className="space-y-4">
                {[
                  'Transforms chaos into semantic graphs',
                  'Maps invisible relationships instantly',
                  'Eliminates duplicates and conflicts'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-gray-300">
                    <div className="h-2 w-2 rounded-full bg-primary" /> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Feature 2: Semantic Guardian */}
        <div className="max-w-7xl mx-auto px-4 relative z-10 mb-40">
          <div className="flex flex-col lg:flex-row-reverse items-center gap-16">
            <div className="w-full lg:w-1/2">
              <div className="relative rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(236,72,153,0.15)] group border border-surface-border">
                <div className="absolute inset-0 bg-accent/20 opacity-0 group-hover:opacity-100 transition-opacity duration-700 z-10 Mix-blend-overlay"></div>
                <img src="/safira_semantic_guardian.jpg" alt="Semantic Guardian" className="w-full h-auto object-cover transform group-hover:scale-105 transition-transform duration-1000" />
              </div>
            </div>
            <div className="w-full lg:w-1/2">
              <div className="flex items-center gap-4 mb-6">
                <div className="h-12 w-12 rounded-xl bg-accent/10 border border-accent/30 flex items-center justify-center text-accent">
                  <Shield className="w-6 h-6" />
                </div>
                <span className="text-accent font-bold tracking-widest uppercase text-sm">Pillar 02</span>
              </div>
              <h3 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">Semantic Guardian</h3>
              <p className="text-gray-400 text-lg md:text-xl leading-relaxed mb-8">
                AI hallucinations are born from bad data. The Guardian acts as a brutal, high-tech firewall. It aggressively filters out corrupt, contradictory, or malicious data particles, letting only pure knowledge pass through.
              </p>
              <ul className="space-y-4">
                {[
                  'Zero-tolerance policy for hallucinations',
                  'Blocks corrupt and contradictory facts',
                  'Ensures enterprise-grade security'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-gray-300">
                    <div className="h-2 w-2 rounded-full bg-accent" /> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Feature 3: Precision Retrieval */}
        <div className="max-w-7xl mx-auto px-4 relative z-10 mb-20">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="w-full lg:w-1/2">
              <div className="relative rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(255,255,255,0.1)] group border border-surface-border">
                <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 z-10 Mix-blend-overlay"></div>
                <img src="/safira_precision_retrieval.jpg" alt="Precision Retrieval" className="w-full h-auto object-cover transform group-hover:scale-105 transition-transform duration-1000" />
              </div>
            </div>
            <div className="w-full lg:w-1/2">
              <div className="flex items-center gap-4 mb-6">
                <div className="h-12 w-12 rounded-xl bg-white/10 border border-white/30 flex items-center justify-center text-white">
                  <Target className="w-6 h-6" />
                </div>
                <span className="text-white font-bold tracking-widest uppercase text-sm">Pillar 03</span>
              </div>
              <h3 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">Precision Retrieval</h3>
              <p className="text-gray-400 text-lg md:text-xl leading-relaxed mb-8">
                Standard search engines guess. SAFIRA aims like a laser. When the Main AI needs a specific fact, SAFIRA surgically targets and extracts the exact golden node from the vast sea of darkness, guaranteeing a perfect answer.
              </p>
              <ul className="space-y-4">
                {[
                  'Surgical extraction of facts',
                  'Bypasses token limits and noise',
                  'Delivers the exact vector to the Main AI'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-gray-300">
                    <div className="h-2 w-2 rounded-full bg-white" /> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

      </section>
    </div>
  );
}
