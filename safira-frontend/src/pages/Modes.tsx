import { Layers, RefreshCw, Shield, Network, Crosshair } from 'lucide-react';

const modes = [
  {
    id: 1,
    title: 'Data Architect',
    icon: <Layers className="h-10 w-10 text-cyan-400" />,
    color: 'from-cyan-500/20 to-transparent border-cyan-500/30',
    description: 'Builds an organized knowledge structure from newly ingested information.',
    responsibilities: [
      'Analyze incoming information.',
      'Identify meaning, context, domain, and source.',
      'Assign appropriate internal classifications.',
      'Establish relevant relationships.',
      'Generate or update internal knowledge addresses.',
      'Prevent unnecessary information fragmentation.'
    ]
  },
  {
    id: 2,
    title: 'Data Reconstructor',
    icon: <RefreshCw className="h-10 w-10 text-blue-400" />,
    color: 'from-blue-500/20 to-transparent border-blue-500/30',
    description: 'Reorganizes existing accessible knowledge repositories, either partially or completely.',
    responsibilities: [
      'Examine existing datasets and structures.',
      'Identify fragmentation, duplication, and inconsistent classifications.',
      'Rebuild organizational relationships.',
      'Preserve source information and important distinctions.',
      'Support controlled, traceable restructuring.'
    ]
  },
  {
    id: 3,
    title: 'Semantic Guardian',
    icon: <Shield className="h-10 w-10 text-emerald-400" />,
    color: 'from-emerald-500/20 to-transparent border-emerald-500/30',
    description: 'Protects semantic integrity and information quality.',
    responsibilities: [
      'Detect repeated information and different expressions.',
      'Distinguish genuine equivalence from similarity.',
      'Preserve variations in language, style, and source.',
      'Identify contradictions and uncertainty.',
      'Evaluate newly arriving info against existing records.',
      'Avoid destructive merging when uncertain.'
    ]
  },
  {
    id: 4,
    title: 'Relation Engine',
    icon: <Network className="h-10 w-10 text-violet-400" />,
    color: 'from-violet-500/20 to-transparent border-violet-500/30',
    description: 'Maintains multidimensional relationships across knowledge.',
    responsibilities: [
      'Connect related concepts, facts, contexts, and applications.',
      'Support multiple simultaneous classifications.',
      'Avoid rigid hierarchical categories.',
      'Maintain reusable relationships without copying.',
      'Support internal addressing and knowledge navigation.'
    ]
  },
  {
    id: 5,
    title: 'Precision Retrieval',
    icon: <Crosshair className="h-10 w-10 text-rose-400" />,
    color: 'from-rose-500/20 to-transparent border-rose-500/30',
    description: 'Provides targeted knowledge retrieval for the Main AI.',
    responsibilities: [
      'Interpret structured knowledge requests.',
      'Locate relevant internal knowledge addresses.',
      'Search multiple related directions when necessary.',
      'Return separate knowledge records appropriately.',
      'Include context, source, confidence, and verification.',
      'Support follow-up requests from the Main AI.'
    ]
  }
];

export default function Modes() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-20 relative z-10">
      <div className="text-center mb-24">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">Five Operating Modes</h1>
        <p className="text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
          SAFIRA operates in five distinct modes that share an underlying classification and addressing architecture. They can operate independently or in concert.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-12">
        {modes.map((mode) => (
          <div key={mode.id} className={`glass-panel overflow-hidden border-l-4 ${mode.color.split(' ')[2]} flex flex-col md:flex-row relative group`}>
            <div className={`absolute inset-0 bg-gradient-to-r ${mode.color.split(' ')[0]} ${mode.color.split(' ')[1]} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
            
            <div className="p-8 md:p-12 md:w-1/3 flex flex-col items-start border-b md:border-b-0 md:border-r border-surface-border">
              <div className="mb-6 p-4 rounded-2xl bg-surface border border-surface-border group-hover:scale-110 transition-transform duration-500 shadow-lg">
                {mode.icon}
              </div>
              <h2 className="text-3xl font-bold mb-3 text-white">
                <span className="text-primary/50 text-xl block mb-1">Mode {mode.id}</span>
                {mode.title}
              </h2>
              <p className="text-gray-400 text-lg">{mode.description}</p>
            </div>
            
            <div className="p-8 md:p-12 md:w-2/3 flex flex-col justify-center">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-primary mb-6 flex items-center gap-2">
                <span className="w-8 h-px bg-primary/50"></span>
                Core Responsibilities
              </h3>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                {mode.responsibilities.map((resp, i) => (
                  <li key={i} className="flex items-start gap-3 text-gray-300 text-base">
                    <span className="text-primary mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0 shadow-[0_0_8px_rgba(14,165,233,0.8)]"></span>
                    <span>{resp}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
