import React, { useState } from 'react';
import { Search, Loader2, ArrowRight, X, Layers, Phone, ShieldCheck, HelpCircle } from 'lucide-react';
import type { DemoScenario } from '../types';

interface SearchBarProps {
  onSearch: (identifier: string, maxDepth: number) => void;
  isLoading: boolean;
  currentQuery: string;
  scenarios: DemoScenario[];
  activeScenarioId?: string;
  onSelectScenario: (scenario: DemoScenario) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  isLoading,
  currentQuery,
  scenarios,
  activeScenarioId,
  onSelectScenario,
}) => {
  const [inputVal, setInputVal] = useState(currentQuery || '');
  const [maxDepth, setMaxDepth] = useState<number>(4);

  React.useEffect(() => {
    if (currentQuery) {
      setInputVal(currentQuery);
    }
  }, [currentQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputVal.trim() && !isLoading) {
      onSearch(inputVal.trim(), maxDepth);
    }
  };

  const getScenarioIcon = (id: string) => {
    switch (id) {
      case 'scenario_1':
        return <Phone className="w-3.5 h-3.5 text-[#f87171]" />;
      case 'scenario_2':
        return <ShieldCheck className="w-3.5 h-3.5 text-[#34d399]" />;
      case 'scenario_3':
        return <HelpCircle className="w-3.5 h-3.5 text-[#fbbf24]" />;
      default:
        return null;
    }
  };

  return (
    <div className="st-toolbar">
      {/* Primary Investigation Search Input & Controls */}
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
        <div className="st-input-container flex-1">
          <Search className="w-4 h-4 text-[#6b7280] shrink-0 mr-2.5" />
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Search phone number, domain, account, or campaign in FalkorDB..."
            className="st-input"
            disabled={isLoading}
          />
          {inputVal && (
            <button
              type="button"
              onClick={() => setInputVal('')}
              className="text-[#6b7280] hover:text-[#e8eaf0] p-1 mr-2"
              title="Clear input"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Inline Hop Selector */}
          <div className="flex items-center gap-1.5 pl-3 border-l border-[#2c3142] py-1 text-xs text-[#9ba3b4] shrink-0">
            <Layers className="w-3.5 h-3.5 text-[#6b7280]" />
            <select
              value={maxDepth}
              onChange={(e) => setMaxDepth(Number(e.target.value))}
              className="st-select"
              disabled={isLoading}
              title="Maximum Cypher traversal depth"
            >
              <option value={1} className="bg-[#161820]">1 Hop</option>
              <option value={2} className="bg-[#161820]">2 Hops</option>
              <option value={3} className="bg-[#161820]">3 Hops</option>
              <option value={4} className="bg-[#161820]">4 Hops</option>
            </select>
          </div>
        </div>

        {/* Action Button */}
        <button
          type="submit"
          disabled={!inputVal.trim() || isLoading}
          className="btn-primary"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin-custom" />
              <span>Traversing...</span>
            </>
          ) : (
            <>
              <span>Investigate</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </form>

      {/* Selectable Prepared Scenarios Bar */}
      {scenarios.length > 0 && (
        <div className="flex items-center gap-2 pt-1 border-t border-[#242835] flex-wrap">
          <span className="text-[11px] font-medium text-[#6b7280] shrink-0 mr-1">
            Demo Scenarios:
          </span>

          <div className="flex items-center gap-2 flex-wrap">
            {scenarios.map((sc) => {
              const isActive = activeScenarioId === sc.id;
              return (
                <button
                  key={sc.id}
                  type="button"
                  onClick={() => !isLoading && onSelectScenario(sc)}
                  disabled={isLoading}
                  className={`scenario-chip ${isActive ? 'active' : ''}`}
                >
                  {getScenarioIcon(sc.id)}
                  <span>{sc.title.split(':')[0]}</span>
                  <span className="font-mono text-[11px] text-[#9ba3b4]">
                    ({sc.query_identifier})
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
