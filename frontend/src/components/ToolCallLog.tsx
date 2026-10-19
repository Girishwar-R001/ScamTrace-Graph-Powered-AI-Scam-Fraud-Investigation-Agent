import React, { useState } from 'react';
import type { ToolCallItem } from '../types';
import { Terminal, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';

interface ToolCallLogProps {
  toolCalls: ToolCallItem[];
  modelName?: string;
}

export const ToolCallLog: React.FC<ToolCallLogProps> = ({ toolCalls, modelName }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="st-panel">
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="st-panel-header cursor-pointer select-none hover:bg-[#1a1d28] transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <Terminal className="w-3.5 h-3.5 text-[#9ba3b4]" />
          <span className="text-xs font-semibold text-[#e8eaf0]">
            Agent Graph Tool Trail ({toolCalls.length})
          </span>
          {modelName && (
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#1f232e] text-[#9ba3b4] border border-[#2c3140] font-mono">
              {modelName}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-[#6b7280]">
          <span>{isOpen ? 'Collapse' : 'Inspect'}</span>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </div>

      {isOpen && (
        <div className="st-panel-body space-y-2 border-t border-[#242835]">
          <p className="text-[11.5px] text-[#6b7280]">
            Every investigation decision is verified against direct FalkorDB graph tool calls:
          </p>

          <div className="space-y-2 pt-1">
            {toolCalls.map((tc, idx) => (
              <div
                key={idx}
                className="st-card space-y-1.5"
              >
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded bg-[#12141a] text-[#9ba3b4] border border-[#272b37] flex items-center justify-center text-[10px] font-mono">
                      {idx + 1}
                    </span>
                    <span className="font-mono font-medium text-[#93c5fd] text-xs">
                      {tc.tool}()
                    </span>
                  </div>
                  <span className="text-[11.5px] text-[#9ba3b4]">
                    {tc.purpose}
                  </span>
                </div>

                {/* Arguments */}
                {tc.arguments && Object.keys(tc.arguments).length > 0 && (
                  <div className="text-[11px] font-mono text-[#cbd5e1] bg-[#12141a] px-2.5 py-1.5 rounded border border-[#242835]">
                    <span className="text-[#6b7280]">args: </span>
                    {JSON.stringify(tc.arguments)}
                  </div>
                )}

                {/* Result Summary */}
                {tc.result_summary && (
                  <div className="text-[11px] text-[#34d399] flex items-center gap-1.5 font-mono pt-0.5">
                    <CheckCircle2 className="w-3 h-3 text-[#34d399] shrink-0" />
                    <span>{tc.result_summary}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolCallLog;
