import type { DemoScenario } from '../types';
import { Network, ShieldCheck, HelpCircle, ArrowRight, GitBranch } from 'lucide-react';

interface DemoScenariosProps {
  scenarios: DemoScenario[];
  onSelectScenario: (scenario: DemoScenario) => void;
  activeScenarioId?: string;
  isLoading: boolean;
}

export const DemoScenarios: React.FC<DemoScenariosProps> = ({
  scenarios,
  onSelectScenario,
  activeScenarioId,
  isLoading,
}) => {
  const getScenarioIcon = (id: string) => {
    switch (id) {
      case 'scenario_1':
        return <Network className="w-5 h-5 text-red-400" />;
      case 'scenario_2':
        return <ShieldCheck className="w-5 h-5 text-emerald-400" />;
      case 'scenario_3':
        return <HelpCircle className="w-5 h-5 text-amber-400" />;
      default:
        return <GitBranch className="w-5 h-5 text-cyan-400" />;
    }
  };

  const getBadgeStyle = (conf: string) => {
    if (conf.includes('MALICIOUS')) return 'badge-malicious';
    if (conf.includes('BENIGN')) return 'badge-benign';
    return 'badge-insufficient';
  };

  return (
    <div className="w-full max-w-6xl mx-auto mb-10">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            Prepared Hackathon Investigation Scenarios
          </h2>
          <p className="text-xs text-slate-400">
            Click any scenario to run an end-to-end FalkorDB graph traversal and agent evaluation
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {scenarios.map((sc) => {
          const isActive = activeScenarioId === sc.id;
          return (
            <div
              key={sc.id}
              onClick={() => !isLoading && onSelectScenario(sc)}
              className={`p-4 rounded-xl cursor-pointer transition-all flex flex-col justify-between ${
                isActive
                  ? 'glass-panel-glow border-cyan-500/60 bg-slate-900/90'
                  : 'glass-panel hover:border-white/20 bg-slate-900/60 hover:bg-slate-900/80'
              }`}
            >
              <div>
                {/* Header & Icon */}
                <div className="flex items-start justify-between gap-3 mb-2.5">
                  <div className="p-2 rounded-lg bg-white/5 border border-white/10 shrink-0">
                    {getScenarioIcon(sc.id)}
                  </div>
                  <span className={`badge ${getBadgeStyle(sc.expected_confidence)} text-[10px]`}>
                    {sc.expected_confidence.replace(/_/g, ' ')}
                  </span>
                </div>

                {/* Title & Target */}
                <h3 className="text-sm font-bold text-white mb-1.5 leading-snug">
                  {sc.title}
                </h3>
                <div className="inline-block px-2 py-0.5 rounded bg-black/40 border border-white/10 text-xs font-mono text-cyan-300 mb-2.5">
                  {sc.query_identifier}
                </div>

                {/* Description */}
                <p className="text-xs text-slate-400 mb-3 line-clamp-3 leading-relaxed">
                  {sc.description}
                </p>
              </div>

              {/* Footer: Why It Matters & Action */}
              <div className="pt-3 border-t border-white/5">
                <div className="text-[11px] text-slate-400 italic mb-3">
                  <span className="text-slate-300 font-semibold not-italic">Graph Value: </span>
                  {sc.why_it_matters}
                </div>
                <button
                  type="button"
                  disabled={isLoading}
                  className="w-full flex items-center justify-center gap-1.5 py-1.5 text-xs font-semibold rounded-lg bg-white/5 hover:bg-white/10 text-cyan-300 transition-colors border border-white/5"
                >
                  <span>Launch Live Investigation</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
