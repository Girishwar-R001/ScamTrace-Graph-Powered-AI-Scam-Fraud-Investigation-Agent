export interface GraphNode {
  id: string;
  label: string;
  risk_score?: number;
  number?: string;
  domain_name?: string;
  account_id?: string;
  campaign_id?: string;
  report_id?: string;
  evidence_id?: string;
  type?: string;
  description?: string;
  name?: string;
  carrier?: string;
  status?: string;
  [key: string]: any;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  highlight?: boolean;
  properties?: Record<string, any>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ToolCallItem {
  tool: string;
  arguments: Record<string, any>;
  purpose: string;
  result_summary?: string;
}

export interface ConnectionExplanation {
  connection: string;
  importance: string;
  provenance: string;
}

export interface InvestigationReport {
  status: 'completed' | 'not_found' | 'error';
  entity_investigated: GraphNode;
  key_connected_entities: GraphNode[];
  connected_campaigns?: GraphNode[];
  source_report_ids: string[];
  relevant_evidence: GraphNode[];
  evidence_strength: 'HIGH_CONFIDENCE_MALICIOUS' | 'MEDIUM_SUSPICIOUS' | 'BENIGN_INDEPENDENT' | 'INSUFFICIENT_EVIDENCE' | 'NO_RECORD_FOUND';
  evidence_strength_rationale: string;
  why_each_connection_matters: ConnectionExplanation[];
  missing_information_and_alternatives: string;
  recommended_action: string;
  action_details: string;
  case_id?: string;
  tool_calls: ToolCallItem[];
  investigation_graph: GraphData;
  agent_model?: string;
  graph_database?: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  entity_type: string;
  query_identifier: string;
  compare_identifier?: string;
  description: string;
  expected_hops: number;
  expected_campaign?: string | null;
  expected_evidence_count: number;
  expected_confidence: string;
  why_it_matters: string;
}

export interface FalkorHealth {
  status: string;
  engine_mode: string;
  host: string;
  port: number;
  graph_name: string;
  total_nodes: number;
  total_edges: number;
  falkordb_live_available: boolean;
}

export interface CaseRecord {
  case_id: string;
  target: string;
  created_at: string;
  evidence_strength: string;
  recommended_action: string;
  action_status: string;
  executed_at?: string;
  reviewer_notes?: string;
  report: InvestigationReport;
}
