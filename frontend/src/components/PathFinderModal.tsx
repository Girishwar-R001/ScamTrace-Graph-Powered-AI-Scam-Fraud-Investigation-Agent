import React, { useState } from 'react';
import { GitFork, ArrowRight, X, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

interface PathFinderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFindPath: (source: string, target: string) => Promise<any>;
}

export const PathFinderModal: React.FC<PathFinderModalProps> = ({
  isOpen,
  onClose,
  onFindPath,
}) => {
  const [source, setSource] = useState('+1-800-555-0144');
  const [target, setTarget] = useState('+1-800-555-0145');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  if (!isOpen) return null;

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!source.trim() || !target.trim() || loading) return;

    try {
      setLoading(true);
      setResult(null);
      const data = await onFindPath(source.trim(), target.trim());
      setResult(data);
    } catch (err: any) {
      setResult({ connected: false, message: err.message || 'Error executing query' });
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (s: string, t: string) => {
    setSource(s);
    setTarget(t);
  };

  return (
    <div className="st-dialog-backdrop">
      <div className="st-dialog max-w-xl">
        {/* Header */}
        <div className="st-dialog-header">
          <div className="flex items-center gap-2.5">
            <GitFork className="w-4 h-4 text-[#5e81f4]" />
            <div>
              <h3 className="text-sm font-semibold text-[#e8eaf0]">
                FalkorDB Path Reachability Inspector
              </h3>
              <p className="text-[11.5px] text-[#6b7280]">
                Inspect shortest relationship paths or verify disconnected entities
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
        <div className="st-dialog-body space-y-4">
          {/* Presets */}
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="text-[11px] text-[#6b7280]">Test Presets:</span>
            <button
              type="button"
              onClick={() => applyPreset('+1-800-555-0199', 'ACC-CRYPTO-MULE-8831')}
              className="scenario-chip text-[11.5px]"
            >
              Multi-Hop Phish ➔ Crypto Mule
            </button>
            <button
              type="button"
              onClick={() => applyPreset('+1-800-555-0144', '+1-800-555-0145')}
              className="scenario-chip text-[11.5px]"
            >
              Sequential Clinic vs Marketing (Unconnected)
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSearch} className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <div>
                <label className="block text-[11.5px] font-medium text-[#9ba3b4] mb-1">
                  Source Entity
                </label>
                <div className="st-input-container">
                  <input
                    type="text"
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    placeholder="e.g. +1-800-555-0144"
                    className="st-input"
                  />
                </div>
              </div>
              <div>
                <label className="block text-[11.5px] font-medium text-[#9ba3b4] mb-1">
                  Target Entity
                </label>
                <div className="st-input-container">
                  <input
                    type="text"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                    placeholder="e.g. +1-800-555-0145"
                    className="st-input"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                disabled={loading || !source || !target}
                className="btn-primary"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin-custom" />
                    <span>Traversing Graph...</span>
                  </>
                ) : (
                  <>
                    <span>Trace Relationship Path</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Results */}
          {result && (
            <div className="p-3.5 rounded bg-[#12141a] border border-[#242835] space-y-2 text-xs">
              {result.connected ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-[#34d399] font-medium">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>Connected via {result.hop_count} relationship hop(s)</span>
                  </div>
                  <div className="p-2.5 bg-[#171a22] rounded border border-[#242835] font-mono text-[11.5px] text-[#93c5fd]">
                    <div className="text-[10px] text-[#6b7280] mb-1">Traversal Sequence:</div>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {result.path_nodes?.map((nodeId: string, idx: number) => (
                        <React.Fragment key={idx}>
                          <span className="px-2 py-0.5 rounded bg-[#202533] text-[#e8eaf0] border border-[#2d3448]">
                            {nodeId}
                          </span>
                          {idx < result.path_nodes.length - 1 && (
                            <ArrowRight className="w-3 h-3 text-[#5e81f4]" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-[#fbbf24] font-medium">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>Graph Isolation Confirmed (0 Connections)</span>
                  </div>
                  <p className="text-[12px] text-[#9ba3b4] leading-relaxed">
                    {result.message}
                  </p>
                  <div className="text-[11px] text-[#6b7280]">
                    Sequential numbers or lexical similarity do not imply graph connectivity without verified edge evidence in FalkorDB.
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PathFinderModal;
