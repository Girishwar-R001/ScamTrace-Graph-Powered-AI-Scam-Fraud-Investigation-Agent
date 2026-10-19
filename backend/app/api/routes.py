"""
ScamTrace FastAPI Routes.
Exposes endpoints for agent investigations, graph traversal, scenario loading,
FalkorDB health checks, and human action approval.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, Query

from app.api.models import InvestigateRequest, PathQueryRequest, ActionApprovalRequest, ActionApprovalResponse
from app.agent.graph_agent import investigation_agent
from app.database.falkor_client import FalkorDBManager
from app.database.queries import GraphQueries
from app.database.seed_data import SCENARIO_DEFINITIONS

router = APIRouter()
db = FalkorDBManager.get_instance()
queries = GraphQueries(db)

# In-memory case registry for local demo persistence
LOCAL_INVESTIGATION_CASES: Dict[str, Dict[str, Any]] = {}


@router.get("/health")
def get_health() -> Dict[str, Any]:
    """Provides transparency into FalkorDB engine mode and statistics."""
    return db.health_check()


@router.get("/scenarios")
def get_scenarios() -> List[Dict[str, Any]]:
    """Returns the 3 prepared hackathon investigation scenarios."""
    return SCENARIO_DEFINITIONS


@router.get("/graph")
def get_full_graph() -> Dict[str, Any]:
    """Exports full FalkorDB graph for initial visualization."""
    return db.get_graph_export()


@router.post("/investigate")
def run_investigation(req: InvestigateRequest) -> Dict[str, Any]:
    """
    Submits an entity to the LangGraph agent for multi-hop graph investigation.
    Returns grounded report, relationship paths, evidence, and tool logs.
    """
    target = req.target_identifier.strip()
    if not target:
        raise HTTPException(status_code=400, detail="Target identifier cannot be empty.")
    
    report = investigation_agent.run_investigation(target)
    
    # Generate and store a case reference if completed
    if report and report.get("status") == "completed":
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        report["case_id"] = case_id
        LOCAL_INVESTIGATION_CASES[case_id] = {
            "case_id": case_id,
            "target": target,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "evidence_strength": report.get("evidence_strength"),
            "recommended_action": report.get("recommended_action"),
            "action_status": "PENDING_HUMAN_APPROVAL",
            "report": report
        }

    return report


@router.post("/path")
def query_path_between(req: PathQueryRequest) -> Dict[str, Any]:
    """Finds direct or indirect relationship path connecting two entities in FalkorDB."""
    res = queries.find_path_between(req.source_entity, req.target_entity)
    if res is None:
        raise HTTPException(status_code=404, detail="One or both entities not found in graph.")
    return res


@router.get("/cases")
def list_cases() -> List[Dict[str, Any]]:
    """Returns list of prepared investigation cases."""
    return list(LOCAL_INVESTIGATION_CASES.values())


@router.post("/action/confirm", response_model=ActionApprovalResponse)
def confirm_action(req: ActionApprovalRequest) -> ActionApprovalResponse:
    """
    Requires explicit human approval before executing any recommended case action.
    Local and non-destructive for hackathon demo safety.
    """
    if not req.confirmed_by_user:
        raise HTTPException(status_code=400, detail="Action was rejected: human confirmation flag is false.")

    case = LOCAL_INVESTIGATION_CASES.get(req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case ID '{req.case_id}' not found.")

    case["action_status"] = "APPROVED_AND_EXECUTED"
    case["executed_at"] = datetime.now(timezone.utc).isoformat()
    case["reviewer_notes"] = req.reviewer_notes

    return ActionApprovalResponse(
        case_id=req.case_id,
        action_type=req.action_type,
        status="EXECUTED_LOCALLY",
        message=f"Action '{req.action_type}' was approved and committed locally. Entity flagged in internal case registry.",
        executed_at=case["executed_at"],
        executed_by="Human Investigator (You)"
    )
