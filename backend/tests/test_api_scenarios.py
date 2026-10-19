"""
End-to-End API and Scenario Integration Tests.
Validates all FastAPI routes, prepared scenarios, and human action approvals.
"""

import sys
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_health():
    print("\n--- 1. Testing GET /api/health ---")
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    print("Health response:", data)
    assert data["status"] == "healthy"
    assert data["total_nodes"] > 0
    print("PASS: Health endpoint verified.")


def test_api_scenarios():
    print("\n--- 2. Testing GET /api/scenarios ---")
    resp = client.get("/api/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert len(scenarios) == 3
    print(f"Loaded {len(scenarios)} hackathon scenarios:")
    for s in scenarios:
        print(f" - {s['title']} (target: {s['query_identifier']})")
    print("PASS: Scenarios loaded successfully.")


def test_api_investigation_scenario_1():
    print("\n--- 3. Testing POST /api/investigate (Scenario 1) ---")
    resp = client.post("/api/investigate", json={"target_identifier": "+1-800-555-0199", "max_depth": 4})
    assert resp.status_code == 200
    report = resp.json()
    assert report["status"] == "completed"
    assert report["evidence_strength"] == "HIGH_CONFIDENCE_MALICIOUS"
    assert "case_id" in report
    print(f"Investigation Case ID: {report['case_id']}")
    print(f"Evidence Strength: {report['evidence_strength']}")
    print(f"Connected Entities: {len(report['key_connected_entities'])}")
    print(f"Graph Edges: {len(report['investigation_graph']['edges'])}")
    print("PASS: Scenario 1 investigation API completed.")
    return report["case_id"]


def test_api_path_query_scenario_2():
    print("\n--- 4. Testing POST /api/path (Scenario 2: False connection test) ---")
    resp = client.post("/api/path", json={
        "source_entity": "+1-800-555-0144",
        "target_entity": "+1-800-555-0145"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is False
    print("Path result:", data["message"])
    print("PASS: Path query correctly verifies no connection.")


def test_api_human_action_confirmation(case_id: str):
    print("\n--- 5. Testing POST /api/action/confirm (Human Approval Flow) ---")
    # First attempt: rejection if not confirmed
    reject_resp = client.post("/api/action/confirm", json={
        "case_id": case_id,
        "action_type": "ESCALATE_AND_FLAG",
        "confirmed_by_user": False,
        "reviewer_notes": "Attempting unconfirmed execution"
    })
    assert reject_resp.status_code == 400
    print("Correctly rejected unconfirmed action.")

    # Second attempt: explicit approval
    approve_resp = client.post("/api/action/confirm", json={
        "case_id": case_id,
        "action_type": "ESCALATE_AND_FLAG",
        "confirmed_by_user": True,
        "reviewer_notes": "Reviewed graph multi-hop proof. Phishing ring verified."
    })
    assert approve_resp.status_code == 200
    action_data = approve_resp.json()
    assert action_data["status"] == "EXECUTED_LOCALLY"
    print("Approved Action Response:", action_data["message"])
    print("PASS: Human action confirmation loop verified.")


if __name__ == "__main__":
    test_api_health()
    test_api_scenarios()
    cid = test_api_investigation_scenario_1()
    test_api_path_query_scenario_2()
    test_api_human_action_confirmation(cid)
    print("\n==========================================")
    print("ALL API INTEGRATION TESTS PASSED CLEANLY!")
    print("==========================================")
