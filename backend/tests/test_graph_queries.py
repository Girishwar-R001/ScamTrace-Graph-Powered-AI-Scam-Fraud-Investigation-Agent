import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.falkor_client import FalkorDBManager
from app.database.queries import GraphQueries
from app.database.seed_data import SCENARIO_DEFINITIONS


def test_database_initialization():
    print("\n--- 1. Testing FalkorDB Database Initialization & Seeding ---")
    db = FalkorDBManager.get_instance()
    db.seed_database(force=True)
    health = db.health_check()
    print("Health check response:", health)
    assert health["total_nodes"] > 0, "Graph has no nodes seeded!"
    assert health["total_edges"] > 0, "Graph has no edges seeded!"
    print("PASS: Database seeded with nodes and relationships.")


def test_entity_search():
    print("\n--- 2. Testing Entity Search Query ---")
    queries = GraphQueries()
    phone_res = queries.search_entity("+1-800-555-0199")
    assert len(phone_res) > 0, "Could not find target phone number!"
    print(f"Found entity: {phone_res[0].get('number')} (risk: {phone_res[0].get('risk_score')})")

    dom_res = queries.search_entity("secure-login-chase-auth.com")
    assert len(dom_res) > 0, "Could not find target domain!"
    print(f"Found domain: {dom_res[0].get('domain_name')}")
    print("PASS: Entity search returns expected records.")


def test_scenario_1_multihop():
    print("\n--- 3. Testing Scenario 1: Multi-Hop Traversal ---")
    queries = GraphQueries()
    paths = queries.trace_connections("+1-800-555-0199", max_depth=4)
    print(f"Discovered {len(paths)} connected paths within 4 hops.")
    
    found_campaign = False
    found_account = False
    for item in paths:
        target = item.get("target", {})
        if target.get("label") == "ScamCampaign" or "campaign_id" in target:
            found_campaign = True
        if target.get("label") == "Account" or "account_id" in target:
            found_account = True

    assert found_campaign, "Multi-hop traversal failed to discover ScamCampaign!"
    assert found_account, "Multi-hop traversal failed to reach crypto laundering Account!"
    print("PASS: Multi-hop graph traversal successfully uncovered campaign and crypto mule account.")


def test_scenario_2_non_connection():
    print("\n--- 4. Testing Scenario 2: Unconnected Similar Entities ---")
    queries = GraphQueries()
    res = queries.find_path_between("+1-800-555-0144", "+1-800-555-0145")
    assert res is not None, "Result was None"
    assert res.get("connected") is False, "Entities should NOT be connected in the graph!"
    print(f"Path query response: {res.get('message')}")
    print("PASS: Verified that sequential phone numbers are legitimately disconnected in graph.")


def test_evidence_retrieval():
    print("\n--- 5. Testing Evidence Retrieval ---")
    queries = GraphQueries()
    evidence = queries.get_evidence("phone_01")
    print(f"Retrieved {len(evidence)} forensic evidence items linked to phone_01.")
    assert len(evidence) > 0, "No evidence records retrieved for target!"
    for ev in evidence:
        print(f" - [{ev.get('type')}]: {ev.get('description')[:60]}...")
    print("PASS: Evidence retrieval returns forensically grounded records.")


def test_schema_inspection():
    print("\n--- 6. Testing Schema Introspection ---")
    queries = GraphQueries()
    schema_info = queries.inspect_schema()
    labels = schema_info["schema"]["node_labels"]
    assert "Phone" in labels and "Domain" in labels and "Account" in labels
    print(f"Schema labels validated: {list(labels.keys())}")
    print("PASS: Schema introspection functional.")


if __name__ == "__main__":
    test_database_initialization()
    test_entity_search()
    test_scenario_1_multihop()
    test_scenario_2_non_connection()
    test_evidence_retrieval()
    test_schema_inspection()
    print("\n==========================================")
    print("ALL PHASE 1 GRAPH TESTS PASSED CLEANLY!")
    print("==========================================")
