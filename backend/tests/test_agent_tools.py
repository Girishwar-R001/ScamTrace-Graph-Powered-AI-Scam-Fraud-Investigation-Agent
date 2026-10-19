"""
Unit tests for ScamTrace LangGraph Agent and Tools.
Validates Phase 2 completion conditions.
"""

import sys
import json
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.agent.tools import search_entity, inspect_graph_schema, trace_connections, get_evidence, create_investigation_case
from app.agent.graph_agent import investigation_agent
from app.agent.deterministic import DeterministicInvestigationEngine


def test_agent_tools_directly():
    print("\n--- 1. Testing Agent Tools Directly ---")
    
    # 1. Search entity tool
    res_search = json.loads(search_entity.invoke({"identifier": "+1-800-555-0199"}))
    assert res_search.get("status") == "found"
    print(f"Tool search_entity output: Found {res_search.get('count')} entity.")

    # 2. Schema inspection tool
    res_schema = json.loads(inspect_graph_schema.invoke({}))
    assert "schema" in res_schema
    print(f"Tool inspect_graph_schema output: {len(res_schema['schema']['node_labels'])} labels available.")

    # 3. Trace connections tool
    res_trace = json.loads(trace_connections.invoke({"entity_id": "+1-800-555-0199", "max_depth": 4}))
    assert res_trace.get("status") == "connections_found"
    print(f"Tool trace_connections output: {res_trace.get('paths_count')} paths uncovered.")

    # 4. Get evidence tool
    res_ev = json.loads(get_evidence.invoke({"target_id": "phone_01"}))
    assert res_ev.get("status") == "evidence_found"
    print(f"Tool get_evidence output: {res_ev.get('evidence_count')} forensic records.")

    # 5. Create case tool
    res_case = json.loads(create_investigation_case.invoke({
        "title": "Phishing Test Case",
        "target_entity": "+1-800-555-0199",
        "findings": "Connected to scam campaign",
        "evidence_ids": ["evid_01"],
        "recommended_action": "FLAG_FOR_REVIEW",
        "confidence_level": "HIGH"
    }))
    assert res_case.get("status") == "case_prepared"
    assert res_case.get("requires_human_approval") is True
    print("PASS: All 5 agent tools executed with structured outputs.")


def test_scenario_1_investigation():
    print("\n--- 2. Testing Full Investigation: Scenario 1 (Syndicate) ---")
    report = investigation_agent.run_investigation("+1-800-555-0199")
    assert report is not None
    assert report["status"] == "completed"
    assert report["evidence_strength"] == "HIGH_CONFIDENCE_MALICIOUS"
    assert len(report["connected_campaigns"]) > 0
    assert len(report["relevant_evidence"]) > 0
    print(f"Scenario 1 Outcome: {report['evidence_strength']}")
    print(f"Campaigns detected: {[c.get('name') for c in report['connected_campaigns']]}")
    print(f"Evidence artifacts: {len(report['relevant_evidence'])}")
    print("PASS: Scenario 1 investigation cleanly grounded in FalkorDB.")


def test_scenario_2_investigation():
    print("\n--- 3. Testing Full Investigation: Scenario 2 (Benign Clinic) ---")
    report = investigation_agent.run_investigation("+1-800-555-0144")
    assert report is not None
    assert report["evidence_strength"] == "BENIGN_INDEPENDENT"
    assert len(report["connected_campaigns"]) == 0
    print(f"Scenario 2 Outcome: {report['evidence_strength']}")
    print(f"Rationale: {report['evidence_strength_rationale']}")
    print("PASS: Scenario 2 correctly classified as benign independent.")


def test_scenario_3_investigation():
    print("\n--- 4. Testing Full Investigation: Scenario 3 (Insufficient Evidence) ---")
    report = investigation_agent.run_investigation("+1-800-555-0720")
    assert report is not None
    assert report["evidence_strength"] == "INSUFFICIENT_EVIDENCE"
    assert report["recommended_action"] == "LOG_AND_MONITOR"
    print(f"Scenario 3 Outcome: {report['evidence_strength']}")
    print(f"Recommended Action: {report['recommended_action']}")
    print("PASS: Scenario 3 safely identifies insufficient evidence without hallucinations.")


def test_missing_entity_investigation():
    print("\n--- 5. Testing Investigation of Non-Existent Entity ---")
    report = investigation_agent.run_investigation("+1-999-000-0000")
    assert report is not None
    assert report["status"] == "not_found"
    assert report["evidence_strength"] == "NO_RECORD_FOUND"
    print("PASS: Non-existent entity handled gracefully with clear not-found state.")


if __name__ == "__main__":
    test_agent_tools_directly()
    test_scenario_1_investigation()
    test_scenario_2_investigation()
    test_scenario_3_investigation()
    test_missing_entity_investigation()
    print("\n==========================================")
    print("ALL PHASE 2 AGENT TESTS PASSED CLEANLY!")
    print("==========================================")
