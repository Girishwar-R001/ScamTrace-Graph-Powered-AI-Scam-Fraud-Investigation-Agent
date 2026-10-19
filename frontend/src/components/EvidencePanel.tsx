import React, { useState } from 'react';
import type { GraphNode } from '../types';
import { Key, FileText, ChevronDown, ChevronRight, Hash, Clock, CheckCircle2 } from 'lucide-react';

interface EvidencePanelProps {
  evidence: GraphNode[];
  reports: string[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidence, reports }) => {
  const [expandedPayloads, setExpandedPayloads] = useState<Record<string, boolean>>({});

  const togglePayload = (id: string) => {
    setExpandedPayloads((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-4">
      {/* Forensic Evidence Panel */}
      <div className="st-panel">
        <div className="st-panel-header">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#e8eaf0]">
            <Key className="w-3.5 h-3.5 text-[#34d399]" />
            <span>Forensic Evidence Records ({evidence.length})</span>
          </div>
          <span className="text-[11px] text-[#6b7280] font-mono">
            Grounded in FalkorDB
          </span>
        </div>

        <div className="st-panel-body space-y-3">
          {evidence.length === 0 ? (
            <div className="py-6 text-center text-xs text-[#6b7280]">
              No forensic evidence records cataloged for this entity.
            </div>
          ) : (
            <div className="space-y-2.5">
              {evidence.map((ev, idx) => {
                const evId = ev.evidence_id || ev.id || `ev-${idx}`;
                const isExpanded = Boolean(expandedPayloads[evId]);

                return (
                  <div key={evId} className="st-card space-y-2">
                    {/* Header Row */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#34d399] shrink-0" />
                        <span className="text-xs font-mono font-medium text-[#e8eaf0]">
                          {evId}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#12141a] text-[#9ba3b4] border border-[#272b37] uppercase font-mono">
                          {ev.type || 'Telemetry'}
                        </span>
                      </div>

                      {ev.timestamp && (
                        <div className="flex items-center gap-1 text-[11px] font-mono text-[#6b7280]">
                          <Clock className="w-3 h-3" />
                          <span>{ev.timestamp}</span>
                        </div>
                      )}
                    </div>

                    {/* Description */}
                    <p className="text-[13px] text-[#cbd5e1] leading-relaxed">
                      {ev.description}
                    </p>

                    {/* Hash & Raw Payload Toggle */}
                    <div className="pt-2 border-t border-[#242835] space-y-1.5">
                      {ev.hash_signature && (
                        <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#9ba3b4]">
                          <Hash className="w-3 h-3 text-[#6b7280] shrink-0" />
                          <span className="text-[#6b7280]">hash:</span>
                          <span className="truncate text-[#93c5fd]">{ev.hash_signature}</span>
                        </div>
                      )}

                      {ev.raw_payload && (
                        <div>
                          <button
                            type="button"
                            onClick={() => togglePayload(evId)}
                            className="flex items-center gap-1 text-[11px] font-mono text-[#6b7280] hover:text-[#9ba3b4] transition-colors py-0.5"
                          >
                            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                            <span>{isExpanded ? 'Hide raw telemetry' : 'View raw telemetry record'}</span>
                          </button>

                          {isExpanded && (
                            <div className="mt-1.5 p-2.5 rounded bg-[#12141a] border border-[#242835] text-[11px] text-[#cbd5e1] overflow-x-auto font-mono">
                              <code>{ev.raw_payload}</code>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Referenced Source Reports */}
      {reports.length > 0 && (
        <div className="st-panel">
          <div className="st-panel-header">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#e8eaf0]">
              <FileText className="w-3.5 h-3.5 text-[#5e81f4]" />
              <span>Source Incident Reports ({reports.length})</span>
            </div>
          </div>

          <div className="st-panel-body">
            <div className="flex flex-wrap gap-2">
              {reports.map((rid, idx) => (
                <div
                  key={idx}
                  className="px-2.5 py-1 rounded bg-[#1b1e28] border border-[#272b37] text-xs font-mono text-[#9ba3b4] flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[#5e81f4]"></span>
                  <span>{rid}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvidencePanel;
