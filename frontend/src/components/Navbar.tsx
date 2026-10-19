import React from 'react';
import { Shield, GitFork, Briefcase, Database, Cpu } from 'lucide-react';
import type { FalkorHealth } from '../types';

interface NavbarProps {
  health: FalkorHealth | null;
  casesCount: number;
  onOpenCases: () => void;
  onOpenPathFinder: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  casesCount,
  onOpenCases,
  onOpenPathFinder,
}) => {
  return (
    <header className="app-navbar">
      <div className="navbar-container">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-md bg-[#5e81f4]/15 border border-[#5e81f4]/30 flex items-center justify-center text-[#5e81f4] shrink-0">
            <Shield className="w-4 h-4" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-[14px] font-semibold tracking-tight text-[#e8eaf0]">
              ScamTrace
            </span>
            <span className="text-[11px] text-[#6b7280] font-mono">
              FalkorDB Graph Agent
            </span>
          </div>
        </div>

        {/* Center: Quiet System Telemetry */}
        <div className="hidden md:flex items-center gap-4 text-xs text-[#9ba3b4]">
          <div className="flex items-center gap-1.5 font-mono text-[11px]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#34d399]"></span>
            <span className="text-[#6b7280]">FalkorDB:</span>
            <span className="text-[#c7cbd5]">
              {health?.falkordb_live_available ? 'Live Server' : 'Embedded Engine'}
            </span>
            <span className="text-[#4b5262]">|</span>
            <span className="text-[#9ba3b4]">
              {health ? `${health.total_nodes} nodes, ${health.total_edges} edges` : 'connecting...'}
            </span>
          </div>

          <div className="flex items-center gap-1.5 font-mono text-[11px]">
            <Cpu className="w-3 h-3 text-[#6b7280]" />
            <span className="text-[#6b7280]">Model:</span>
            <span className="text-[#c7cbd5]">Gemini 3.8 Flash</span>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenPathFinder}
            className="btn-secondary"
            title="Inspect shortest relationship path between two entities"
          >
            <GitFork className="w-3.5 h-3.5 text-[#9ba3b4]" />
            <span>Path Inspector</span>
          </button>

          <button
            onClick={onOpenCases}
            className="btn-secondary"
            title="View saved local investigation cases"
          >
            <Briefcase className="w-3.5 h-3.5 text-[#9ba3b4]" />
            <span>Cases</span>
            {casesCount > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded bg-[#2a3040] text-[#c7cbd5] text-[10px] font-mono font-medium">
                {casesCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
