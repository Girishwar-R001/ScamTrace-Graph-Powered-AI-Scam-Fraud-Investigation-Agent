import React from 'react';
import type { CaseRecord } from '../types';
import { Briefcase, X, Clock, ArrowRight } from 'lucide-react';

interface CasesDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  cases: CaseRecord[];
  onSelectCase: (c: CaseRecord) => void;
}

export const CasesDrawer: React.FC<CasesDrawerProps> = ({
  isOpen,
  onClose,
  cases,
  onSelectCase,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs">
      <div className="st-drawer p-5 justify-between">
        <div className="flex flex-col h-full overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between pb-3.5 border-b border-[#242835] mb-4">
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-[#5e81f4]" />
              <h3 className="text-sm font-semibold text-[#e8eaf0]">
                Investigation Cases ({cases.length})
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-[#6b7280] hover:text-[#e8eaf0] p-1 rounded hover:bg-[#222634] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Cases List */}
          {cases.length === 0 ? (
            <div className="text-center py-16 text-[#6b7280] text-xs">
              No investigation cases recorded in this session yet.
              <p className="mt-1.5 text-[#9ba3b4]">
                Run an investigation to prepare formal cases.
              </p>
            </div>
          ) : (
            <div className="space-y-2.5 overflow-y-auto flex-1 pr-1">
              {cases.map((c) => (
                <div
                  key={c.case_id}
                  onClick={() => {
                    onSelectCase(c);
                    onClose();
                  }}
                  className="st-card cursor-pointer hover:border-[#3d4559] transition-all space-y-2 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-medium text-[#93c5fd]">
                      {c.case_id}
                    </span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                      c.action_status === 'APPROVED_AND_EXECUTED'
                        ? 'bg-[#12241b] text-[#34d399] border border-[#1f4834]'
                        : 'bg-[#241e12] text-[#fbbf24] border border-[#453719]'
                    }`}>
                      {c.action_status === 'APPROVED_AND_EXECUTED' ? 'Approved' : 'Pending'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-xs font-mono text-[#e8eaf0] font-medium">
                      {c.target}
                    </div>
                    <ArrowRight className="w-3 h-3 text-[#4b5262] group-hover:text-[#9ba3b4] transition-colors" />
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-[#6b7280] pt-1.5 border-t border-[#242835]">
                    <div className="flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <span className="text-[#9ba3b4] font-medium">
                      {c.recommended_action}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="btn-secondary w-full mt-4"
        >
          Close Drawer
        </button>
      </div>
    </div>
  );
};

export default CasesDrawer;
