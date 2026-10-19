"""
ScamTrace FalkorDB Graph Schema Definitions
Defines node labels, relationship types, indices, and property specifications.
"""

from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class NodeLabel(str, Enum):
    PHONE = "Phone"
    DOMAIN = "Domain"
    ACCOUNT = "Account"
    SCAM_CAMPAIGN = "ScamCampaign"
    REPORT = "Report"
    EVIDENCE = "Evidence"

class RelationshipType(str, Enum):
    REPORTED_IN = "REPORTED_IN"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    SHARES_DOMAIN = "SHARES_DOMAIN"
    LINKED_TO_CAMPAIGN = "LINKED_TO_CAMPAIGN"
    SUPPORTED_BY = "SUPPORTED_BY"
    REFERENCES = "REFERENCES"

# Schema metadata for agent inspection
GRAPH_SCHEMA_DEFINITION = {
    "node_labels": {
        NodeLabel.PHONE.value: {
            "description": "Telephony identifiers such as caller IDs, SMS senders, and callback numbers.",
            "primary_key": "number",
            "properties": ["id", "number", "carrier", "country", "line_type", "risk_score", "label"]
        },
        NodeLabel.DOMAIN.value: {
            "description": "Internet domains, phishing URLs, hostnames, and landing pages.",
            "primary_key": "domain_name",
            "properties": ["id", "domain_name", "registrar", "creation_date", "ip_address", "risk_score"]
        },
        NodeLabel.ACCOUNT.value: {
            "description": "Financial, social media, crypto wallet, or messaging accounts.",
            "primary_key": "account_id",
            "properties": ["id", "account_id", "platform", "account_type", "status", "risk_score"]
        },
        NodeLabel.SCAM_CAMPAIGN.value: {
            "description": "Known or clustered coordinated fraud campaigns and threat operations.",
            "primary_key": "campaign_id",
            "properties": ["id", "campaign_id", "name", "theme", "first_detected", "severity", "status"]
        },
        NodeLabel.REPORT.value: {
            "description": "Victim reports, community flags, and law enforcement incident submissions.",
            "primary_key": "report_id",
            "properties": ["id", "report_id", "source", "reported_date", "claim", "verified", "confidence"]
        },
        NodeLabel.EVIDENCE.value: {
            "description": "Forensic artifacts: SMS transcripts, server logs, payment hashes, and DNS records.",
            "primary_key": "evidence_id",
            "properties": ["id", "evidence_id", "type", "description", "timestamp", "hash_signature", "raw_payload"]
        }
    },
    "relationship_types": {
        RelationshipType.REPORTED_IN.value: {
            "description": "Indicates an entity was explicitly reported in a victim or incident report.",
            "from_labels": ["Phone", "Domain", "Account"],
            "to_labels": ["Report"],
            "properties": ["reported_date", "reported_role", "confidence"]
        },
        RelationshipType.ASSOCIATED_WITH.value: {
            "description": "Observed direct connection between two infrastructure or communication entities.",
            "from_labels": ["Phone", "Domain", "Account", "ScamCampaign"],
            "to_labels": ["Domain", "Account", "Phone", "ScamCampaign"],
            "properties": ["association_type", "weight", "observed_date"]
        },
        RelationshipType.SHARES_DOMAIN.value: {
            "description": "Indicates an account or service shares authoritative DNS or hosting domain.",
            "from_labels": ["Account", "Phone"],
            "to_labels": ["Domain"],
            "properties": ["first_seen", "last_seen", "hosting_type"]
        },
        RelationshipType.LINKED_TO_CAMPAIGN.value: {
            "description": "Connects an entity, domain, account, or report to an overarching scam campaign.",
            "from_labels": ["Phone", "Domain", "Account", "Report"],
            "to_labels": ["ScamCampaign"],
            "properties": ["attribution_confidence", "attribution_rule", "linked_date"]
        },
        RelationshipType.SUPPORTED_BY.value: {
            "description": "Connects a claim or report directly to verified forensic evidence artifacts.",
            "from_labels": ["Report", "ScamCampaign", "Account"],
            "to_labels": ["Evidence"],
            "properties": ["evidence_strength", "validation_status"]
        },
        RelationshipType.REFERENCES.value: {
            "description": "Informational citation or indirect cross-reference between reports or campaigns.",
            "from_labels": ["Report", "Evidence"],
            "to_labels": ["Report", "ScamCampaign", "Phone", "Domain"],
            "properties": ["reference_type", "relevance"]
        }
    },
    "indexes": [
        {"label": "Phone", "property": "number"},
        {"label": "Domain", "property": "domain_name"},
        {"label": "Account", "property": "account_id"},
        {"label": "ScamCampaign", "property": "campaign_id"},
        {"label": "Report", "property": "report_id"},
        {"label": "Evidence", "property": "evidence_id"}
    ]
}
