import React from 'react';
import type { InvestigationReport } from '../types';
import { ArrowRight, ArrowUpRight, ShieldCheck, AlertTriangle, ShieldAlert, HelpCircle, Network, Info } from 'lucide-react';

interface ReportViewProps {
  report: InvestigationReport;
  onInitiateAction: () => void;
}

export const ReportView: React.FC<ReportViewProps> = ({ report, onInitiateAction }) => {
  const getSeverityBadge = (strength: string) => {
    switch (strength) {
      case 'HIGH_CONFIDENCE_MALICIOUS':
        return {
          icon: <ShieldAlert className="w-3.5 h-3.5 text-[#f87171]" />,
          label: 'High Confidence Malicious',
          badgeClass: 'badge-malicious'
        };
      case 'MEDIUM_SUSPICIOUS':
        return {
          icon: <AlertTriangle className="w-3.5 h-3.5 text-[#fbbf24]" />,
          label: 'Medium Suspicious',
          badgeClass: 'badge-suspicious'
        };
      case 'BENIGN_INDEPENDENT':
        return {
          icon: <ShieldCheck className="w-3.5 h-3.5 text-[#34d399]" />,
          label: 'Benign Independent',
          badgeClass: 'badge-benign'
        };
      case 'INSUFFICIENT_EVIDENCE':
        return {
          icon: <HelpCircle className="w-3.5 h-3.5 text-[#fbbf24]" />,
          label: 'Insufficient Evidence',
          badgeClass: 'badge-suspicious'
        };
      default:
        return {
          icon: <Info className="w-3.5 h-3.5 text-[#94a3b8]" />,
          label: 'No Record Found',
          badgeClass: 'badge-neutral'
        };
    }
  };

  const badgeInfo = getSeverityBadge(report.evidence_strength);
  const target = report.entity_investigated;
  const targetId = target?.number || target?.domain_name || target?.account_id || target?.id;

  return (
    <div className="space-y-4">
      {/* Investigation Summary Panel */}
      <div className="st-panel">
        <div className="st-panel-header">
          <div className="flex items-center gap-2.5">
            <span className="text-[11px] font-mono uppercase text-[#6b7280]">
              {target?.label || 'Target'}:
            </span>
            <span className="text-sm font-mono font-semibold text-[#e8eaf0]">
              {targetId}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {report.case_id && (
              <span className="text-[11px] font-mono text-[#6b7280]">
                Case #{report.case_id}
              </span>
            )}
            <div className={`status-badge ${badgeInfo.badgeClass}`}>
              <span className="status-badge-dot"></span>
              <span>{badgeInfo.label}</span>
            </div>
          </div>
        </div>

        <div className="st-panel-body space-y-3">
          <p className="text-[13.5px] text-[#cbd5e1] leading-relaxed">
            {report.evidence_strength_rationale}
          </p>

          {/* Quick Stats Bar */}
          <div className="flex items-center gap-4 pt-3 border-t border-[#242835] text-xs text-[#9ba3b4]">
            <div>
              <span className="text-[#6b7280]">Connected Entities: </span>
              <span className="text-[#e8eaf0] font-medium">{report.key_connected_entities?.length || 0}</span>
            </div>
            <div>
              <span className="text-[#6b7280]">Forensic Artifacts: </span>
              <span className="text-[#e8eaf0] font-medium">{report.relevant_evidence?.length || 0}</span>
            </div>
            <div>
              <span className="text-[#6b7280]">Reports: </span>
              <span className="text-[#e8eaf0] font-medium">{report.source_report_ids?.length || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Connection Paths & Analysis */}
      {report.why_each_connection_matters && report.why_each_connection_matters.length > 0 && (
        <div className="st-panel">
          <div className="st-panel-header">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#e8eaf0]">
              <Network className="w-3.5 h-3.5 text-[#5e81f4]" />
              <span>Multi-Hop Connection Analysis</span>
            </div>
            <span className="text-[11px] text-[#6b7280] font-mono">
              FalkorDB Cypher Traversal
            </span>
          </div>

          <div className="st-panel-body space-y-2.5">
            {report.why_each_connection_matters.map((item, idx) => (
              <div key={idx} className="st-card space-y-1.5">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <span className="text-xs font-mono font-medium text-[#93c5fd]">
                    {item.connection}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-[#14161f] text-[#9ba3b4] border border-[#272b37] font-mono">
                    {item.provenance}
                  </span>
                </div>
                <p className="text-[13px] text-[#9ba3b4] leading-relaxed">
                  {item.importance}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evidence Gaps & Alternative Explanations */}
      <div className="st-panel">
        <div className="st-panel-header">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#e8eaf0]">
            <Info className="w-3.5 h-3.5 text-[#fbbf24]" />
            <span>Alternative Hypotheses & Evidence Gaps</span>
          </div>
        </div>

        <div className="st-panel-body space-y-2.5">
          <p className="text-[13px] text-[#9ba3b4] leading-relaxed">
            {report.missing_information_and_alternatives}
          </p>
          <div className="p-3 rounded bg-[#14161f] border border-[#242835] text-[11.5px] text-[#717a8c] leading-relaxed">
            <span className="text-[#9ba3b4] font-medium">Standard of Evidence Note: </span>
            FalkorDB graph connections demonstrate infrastructure association and co-location, but do not replace legal carrier evidentiary standards.
          </div>
        </div>
      </div>

      {/* Recommended Operational Action */}
      <div className="st-panel">
        <div className="st-panel-body flex flex-col sm:flex-row sm:items-center justify-between gap-3.5">
          <div className="space-y-1">
            <div className="text-[11px] font-medium uppercase tracking-wider text-[#6b7280]">
              Recommended Next Action
            </div>
            <div className="text-xs font-semibold text-[#e8eaf0] flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#5e81f4]"></span>
              {report.recommended_action}
            </div>
            <p className="text-xs text-[#9ba3b4] max-w-md">
              {report.action_details}
            </p>
          </div>

          {report.recommended_action && report.recommended_action !== 'NO_ACTION_REQUIRED' && (
            <button
              onClick={onInitiateAction}
              className="btn-primary shrink-0 self-start sm:self-center"
            >
              <span>Review & Execute</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportView;
