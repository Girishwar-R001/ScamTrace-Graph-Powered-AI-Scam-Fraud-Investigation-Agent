"""
ScamTrace FalkorDB Agent Tools.
Tools for LangGraph agent to inspect schema, search entities, trace multi-hop connections,
fetch source evidence, and prepare investigation cases.
"""

import json
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from app.database.queries import GraphQueries
from app.database.schema import GRAPH_SCHEMA_DEFINITION

queries = GraphQueries()


@tool
def search_entity(identifier: str) -> str:
    """
    Finds an entity node in FalkorDB by identifier or attributes (phone number, domain name,
    account ID, campaign ID, or node ID).
    Returns grounded database records or a clear not-found message.
    """
    clean_id = str(identifier).strip()
    results = queries.search_entity(clean_id)
    if not results:
        return json.dumps({
            "status": "not_found",
            "searched_identifier": clean_id,
            "message": f"No entity matching '{clean_id}' was found in FalkorDB."
        })
    return json.dumps({
        "status": "found",
        "count": len(results),
        "entities": results
    }, default=str)


@tool
def inspect_graph_schema() -> str:
    """
    Introspects the FalkorDB graph schema to understand available node labels,
    primary keys, properties, and relationship types before querying.
    """
    info = queries.inspect_schema()
    return json.dumps(info, default=str)


@tool
def trace_connections(entity_id: str, max_depth: int = 3) -> str:
    """
    Traverses relationships up to max_depth (max 4) from a starting node in FalkorDB.
    Uncovers multi-hop indirect connections to campaigns, domains, accounts, and reports.
    """
    depth = min(max(1, int(max_depth)), 4)
    paths = queries.trace_connections(str(entity_id).strip(), max_depth=depth)
    if not paths:
        return json.dumps({
            "status": "isolated",
            "start_entity": entity_id,
            "paths_found": 0,
            "message": f"Entity '{entity_id}' has no connected relationships up to depth {depth}."
        })
    return json.dumps({
        "status": "connections_found",
        "start_entity": entity_id,
        "depth_searched": depth,
        "paths_count": len(paths),
        "paths": paths
    }, default=str)


@tool
def get_evidence(target_id: str) -> str:
    """
    Retrieves source forensic evidence records and victim reports supporting a finding.
    Returns cryptographic hashes, SMS dumps, server logs, or blockchain transaction records.
    """
    evidence = queries.get_evidence(str(target_id).strip())
    if not evidence:
        return json.dumps({
            "status": "no_evidence",
            "target_id": target_id,
            "message": f"No direct or indirect forensic evidence records found for '{target_id}'."
        })
    return json.dumps({
        "status": "evidence_found",
        "target_id": target_id,
        "evidence_count": len(evidence),
        "records": evidence
    }, default=str)


@tool
def create_investigation_case(
    title: str,
    target_entity: str,
    findings: str,
    evidence_ids: List[str],
    recommended_action: str,
    confidence_level: str
) -> str:
    """
    Prepares a formal investigation case containing discovered findings and supporting evidence.
    Prepares local actions (e.g. Flag for Human Review, Escalate Report) pending user confirmation.
    """
    case_payload = {
        "status": "case_prepared",
        "title": title,
        "target_entity": target_entity,
        "findings": findings,
        "evidence_ids": evidence_ids,
        "recommended_action": recommended_action,
        "confidence_level": confidence_level,
        "requires_human_approval": True
    }
    return json.dumps(case_payload)


ALL_AGENT_TOOLS = [
    search_entity,
    inspect_graph_schema,
    trace_connections,
    get_evidence,
    create_investigation_case
]
