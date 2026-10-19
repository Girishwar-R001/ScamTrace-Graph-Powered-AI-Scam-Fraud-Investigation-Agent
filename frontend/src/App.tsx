import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { SearchBar } from './components/SearchBar';
import { GraphView } from './components/GraphView';
import { ReportView } from './components/ReportView';
import { EvidencePanel } from './components/EvidencePanel';
import { ToolCallLog } from './components/ToolCallLog';
import { ActionModal } from './components/ActionModal';
import { PathFinderModal } from './components/PathFinderModal';
import { CasesDrawer } from './components/CasesDrawer';
import type {
  FalkorHealth,
  DemoScenario,
  GraphData,
  InvestigationReport,
  CaseRecord,
} from './types';
import { Network } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api';

export const App: React.FC = () => {
  const [health, setHealth] = useState<FalkorHealth | null>(null);
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [fullGraph, setFullGraph] = useState<GraphData>({ nodes: [], edges: [] });
  const [currentReport, setCurrentReport] = useState<InvestigationReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [activeScenarioId, setActiveScenarioId] = useState<string | undefined>('scenario_1');
  const [cases, setCases] = useState<CaseRecord[]>([]);

  // Modals state
  const [isActionModalOpen, setIsActionModalOpen] = useState<boolean>(false);
  const [isPathFinderOpen, setIsPathFinderOpen] = useState<boolean>(false);
  const [isCasesDrawerOpen, setIsCasesDrawerOpen] = useState<boolean>(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const healthRes = await fetch(`${API_BASE}/health`);
      if (healthRes.ok) setHealth(await healthRes.json());

      const scenRes = await fetch(`${API_BASE}/scenarios`);
      if (scenRes.ok) setScenarios(await scenRes.json());

      const graphRes = await fetch(`${API_BASE}/graph`);
      if (graphRes.ok) setFullGraph(await graphRes.json());

      const casesRes = await fetch(`${API_BASE}/cases`);
      if (casesRes.ok) setCases(await casesRes.json());

      handleSearch('+1-800-555-0199', 4);
    } catch (err) {
      console.error('Failed to load initial FalkorDB backend data:', err);
    }
  };

  const handleSearch = async (targetIdentifier: string, maxDepth: number = 4) => {
    try {
      setIsLoading(true);
      setCurrentQuery(targetIdentifier);

      const resp = await fetch(`${API_BASE}/investigate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_identifier: targetIdentifier, max_depth: maxDepth })
      });

      if (!resp.ok) throw new Error(`Server returned HTTP ${resp.status}`);

      const reportData: InvestigationReport = await resp.json();
      setCurrentReport(reportData);

      const casesRes = await fetch(`${API_BASE}/cases`);
      if (casesRes.ok) setCases(await casesRes.json());
    } catch (err: any) {
      console.error('Investigation error:', err);
      alert('Investigation query failed: ' + (err.message || 'Check if backend is running.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectScenario = (scenario: DemoScenario) => {
    setActiveScenarioId(scenario.id);
    handleSearch(scenario.query_identifier, scenario.expected_hops || 4);
  };

  const handleConfirmAction = async (caseId: string, actionType: string, notes: string) => {
    const res = await fetch(`${API_BASE}/action/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        case_id: caseId,
        action_type: actionType,
        confirmed_by_user: true,
        reviewer_notes: notes
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Confirmation failed');
    }

    const casesRes = await fetch(`${API_BASE}/cases`);
    if (casesRes.ok) setCases(await casesRes.json());
  };

  const handleFindPath = async (source: string, target: string) => {
    const res = await fetch(`${API_BASE}/path`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_entity: source, target_entity: target })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Path query failed');
    }
    return await res.json();
  };

  const activeGraphData: GraphData =
    currentReport && currentReport.investigation_graph && currentReport.investigation_graph.nodes.length > 0
      ? currentReport.investigation_graph
      : fullGraph;

  return (
    <div className="app-shell selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        health={health}
        casesCount={cases.length}
        onOpenCases={() => setIsCasesDrawerOpen(true)}
        onOpenPathFinder={() => setIsPathFinderOpen(true)}
      />

      {/* Main Studio Container with Centered Max-Width and Generous Margins */}
      <main className="app-main">
        {/* Top Control Bar with Integrated Scenario Switcher */}
        <SearchBar
          onSearch={handleSearch}
          isLoading={isLoading}
          currentQuery={currentQuery}
          scenarios={scenarios}
          activeScenarioId={activeScenarioId}
          onSelectScenario={handleSelectScenario}
        />

        {/* Studio Workspace Area */}
        {currentReport ? (
          <div className="space-y-4">
            {/* Header Status Bar */}
            <div className="flex items-center justify-between pb-2 border-b border-[#242835] px-0.5">
              <div className="flex items-center gap-2.5">
                <h2 className="text-xs font-semibold uppercase tracking-wider text-[#9ba3b4]">
                  Investigation Workspace
                </h2>
                <span className="text-xs text-[#6b7280] font-mono">
                  ({currentReport.entity_investigated?.label || 'Entity'}:{' '}
                  <span className="text-[#e8eaf0] font-medium">
                    {currentReport.entity_investigated?.number || currentReport.entity_investigated?.domain_name || currentReport.entity_investigated?.id}
                  </span>)
                </span>
              </div>
              <div className="text-[11.5px] text-[#6b7280] font-mono flex items-center gap-2">
                <span className="text-[#9ba3b4] font-medium">{activeGraphData.nodes.length}</span> nodes
                <span>•</span>
                <span className="text-[#9ba3b4] font-medium">{activeGraphData.edges.length}</span> relationships
              </div>
            </div>

            {/* Aligned 2-Column Grid */}
            <div className="studio-layout">
              {/* Left Column: Relationship Graph & Technical Audit Log */}
              <div className="space-y-4">
                <div className="st-panel">
                  <div className="st-panel-header">
                    <span className="text-xs font-semibold text-[#e8eaf0] flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#5e81f4]"></span>
                      Graph Topology & Connected Subgraph
                    </span>
                    <span className="text-[11px] font-mono text-[#6b7280]">
                      Interactive: Drag • Pan • Zoom • Inspect
                    </span>
                  </div>

                  <GraphView
                    graphData={activeGraphData}
                    targetId={currentReport.entity_investigated?.id}
                  />
                </div>

                <ToolCallLog
                  toolCalls={currentReport.tool_calls || []}
                  modelName={currentReport.agent_model}
                />
              </div>

              {/* Right Column: Dossier & Forensic Evidence */}
              <div className="space-y-4">
                <ReportView
                  report={currentReport}
                  onInitiateAction={() => setIsActionModalOpen(true)}
                />

                <EvidencePanel
                  evidence={currentReport.relevant_evidence || []}
                  reports={currentReport.source_report_ids || []}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="st-panel p-16 text-center text-[#6b7280] space-y-3">
            <Network className="w-8 h-8 mx-auto text-[#4b5262]" />
            <h4 className="text-sm font-semibold text-[#e8eaf0]">
              No Active Investigation Target
            </h4>
            <p className="text-xs max-w-sm mx-auto text-[#9ba3b4]">
              Select a prepared demo scenario in the toolbar above or search for an entity to traverse FalkorDB.
            </p>
          </div>
        )}
      </main>

      {/* Human Confirmation Action Modal */}
      {currentReport && (
        <ActionModal
          isOpen={isActionModalOpen}
          onClose={() => setIsActionModalOpen(false)}
          caseId={currentReport.case_id || 'CASE-LOCAL-01'}
          targetEntity={
            currentReport.entity_investigated?.number ||
            currentReport.entity_investigated?.domain_name ||
            currentReport.entity_investigated?.id ||
            currentQuery
          }
          recommendedAction={currentReport.recommended_action || 'FLAG_FOR_REVIEW'}
          onConfirm={handleConfirmAction}
        />
      )}

      {/* Path Reachability Inspector Modal */}
      <PathFinderModal
        isOpen={isPathFinderOpen}
        onClose={() => setIsPathFinderOpen(false)}
        onFindPath={handleFindPath}
      />

      {/* Cases History Drawer */}
      <CasesDrawer
        isOpen={isCasesDrawerOpen}
        onClose={() => setIsCasesDrawerOpen(false)}
        cases={cases}
        onSelectCase={(c) => {
          setCurrentReport(c.report);
          setCurrentQuery(c.target);
        }}
      />

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-container">
          <div className="font-medium text-slate-400 text-xs">
            ScamTrace — FalkorDB Graph Hacks (Track 01)
          </div>
          <div className="flex items-center gap-3 text-slate-500 font-mono text-[11px]">
            <span>FalkorDB Cypher Engine</span>
            <span>•</span>
            <span>LangGraph Agent</span>
            <span>•</span>
            <span>Gemini 3.8 Flash</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
