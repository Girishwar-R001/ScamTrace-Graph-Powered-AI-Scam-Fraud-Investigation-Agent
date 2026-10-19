import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, X, AlertTriangle, Loader2 } from 'lucide-react';

interface ActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
  targetEntity: string;
  recommendedAction: string;
  onConfirm: (caseId: string, actionType: string, notes: string) => Promise<void>;
}

export const ActionModal: React.FC<ActionModalProps> = ({
  isOpen,
  onClose,
  caseId,
  targetEntity,
  recommendedAction,
  onConfirm,
}) => {
  const [confirmed, setConfirmed] = useState(false);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirmed || isSubmitting) return;

    try {
      setIsSubmitting(true);
      await onConfirm(caseId, recommendedAction, notes);
      setResultMessage(`Action '${recommendedAction}' successfully approved and committed to local case records.`);
      setTimeout(() => {
        setIsSubmitting(false);
        setResultMessage(null);
        onClose();
      }, 1500);
    } catch (err: any) {
      setIsSubmitting(false);
      alert('Action confirmation failed: ' + (err.message || 'Unknown error'));
    }
  };

  return (
    <div className="st-dialog-backdrop">
      <div className="st-dialog">
        {/* Header */}
        <div className="st-dialog-header">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-4 h-4 text-[#5e81f4]" />
            <div>
              <h3 className="text-sm font-semibold text-[#e8eaf0]">
                Review & Confirm Operational Action
              </h3>
              <p className="text-[11.5px] text-[#6b7280]">
                Human-in-the-Loop Controlled Execution Guardrail
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#6b7280] hover:text-[#e8eaf0] p-1 rounded hover:bg-[#222634] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="st-dialog-body">
          {resultMessage ? (
            <div className="p-3.5 rounded bg-[#12241b] border border-[#1f4834] text-[#34d399] text-xs flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{resultMessage}</span>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
              {/* Case Details */}
              <div className="p-3 rounded bg-[#12141a] border border-[#242835] space-y-2">
                <div className="flex justify-between items-center text-[11.5px]">
                  <span className="text-[#6b7280]">Case Reference:</span>
                  <span className="font-mono text-[#93c5fd] font-medium">{caseId}</span>
                </div>
                <div className="flex justify-between items-center text-[11.5px]">
                  <span className="text-[#6b7280]">Target Entity:</span>
                  <span className="font-mono text-[#e8eaf0] font-medium">{targetEntity}</span>
                </div>
                <div className="flex justify-between items-center pt-2 border-t border-[#1f232e] text-[11.5px]">
                  <span className="text-[#6b7280]">Proposed Action:</span>
                  <span className="px-2 py-0.5 rounded bg-[#1f2433] text-[#93c5fd] border border-[#2e364a] font-mono font-medium">
                    {recommendedAction}
                  </span>
                </div>
              </div>

              {/* Safety Notice */}
              <div className="p-2.5 rounded bg-[#1f1d16] border border-[#3b341f] text-[#d97706] flex items-start gap-2 text-[11px] leading-relaxed">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5 text-[#fbbf24]" />
                <span className="text-[#d5a557]">
                  Safety Guardrail: Actions are strictly contained within the local ScamTrace environment. External networks or endpoints are never touched without authorized operator credentials.
                </span>
              </div>

              {/* Reviewer Notes */}
              <div className="space-y-1">
                <label className="block text-[11.5px] font-medium text-[#9ba3b4]">
                  Reviewer Notes (Optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g., Verified 4-hop graph association and forensic SMS reverse proxy payload."
                  className="w-full h-18 p-2.5 rounded bg-[#12141a] border border-[#2c3142] text-[#e8eaf0] placeholder-[#6b7280] text-xs focus:border-[#5e81f4] outline-none resize-none font-sans"
                />
              </div>

              {/* Confirmation Checkbox */}
              <label className="flex items-start gap-2 p-2.5 rounded bg-[#12141a] border border-[#242835] cursor-pointer hover:bg-[#1a1d26] transition-colors">
                <input
                  type="checkbox"
                  checked={confirmed}
                  onChange={(e) => setConfirmed(e.target.checked)}
                  className="mt-0.5 rounded border-[#2c3142] text-[#5e81f4] focus:ring-0"
                />
                <span className="text-[11.5px] text-[#cbd5e1] leading-normal select-none">
                  I have independently reviewed the FalkorDB relationship chain and corroborate this local operational recommendation.
                </span>
              </label>

              {/* Actions */}
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#242835]">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!confirmed || isSubmitting}
                  className="btn-primary"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin-custom" />
                      <span>Committing...</span>
                    </>
                  ) : (
                    <span>Confirm Action</span>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ActionModal;
