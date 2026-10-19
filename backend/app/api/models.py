"""
Pydantic data models for ScamTrace FastAPI REST endpoints.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class InvestigateRequest(BaseModel):
    target_identifier: str = Field(..., description="Phone number, domain name, account ID, or campaign ID")
    max_depth: int = Field(default=4, ge=1, le=4, description="Maximum traversal depth (1 to 4)")


class PathQueryRequest(BaseModel):
    source_entity: str = Field(..., description="First entity identifier")
    target_entity: str = Field(..., description="Second entity identifier")


class ActionApprovalRequest(BaseModel):
    case_id: str = Field(..., description="Unique case identifier")
    action_type: str = Field(..., description="Action type (e.g. ESCALATE_AND_FLAG, LOG_AND_MONITOR)")
    confirmed_by_user: bool = Field(..., description="Explicit human confirmation flag")
    reviewer_notes: Optional[str] = Field(default="", description="Investigator notes")


class ActionApprovalResponse(BaseModel):
    case_id: str
    action_type: str
    status: str
    message: str
    executed_at: str
    executed_by: str
