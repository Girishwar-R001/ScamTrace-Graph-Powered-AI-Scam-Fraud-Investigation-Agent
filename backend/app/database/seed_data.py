"""
Deterministic synthetic dataset for FalkorDB ScamTrace.
Provides 3 curated hackathon investigation scenarios:
- Scenario 1: Multi-Hop Phishing Syndicate (Deep investigation)
- Scenario 2: Sequential Similarity Non-Connection (Coincidental phone numbers)
- Scenario 3: Ambiguous / Insufficient Evidence (Isolated single unverified report)
- Plus benign control entities
"""

from typing import Dict, List, Any

SEED_NODES = {
    "Phone": [
        # Scenario 1 Target: Suspicious SMS Sender
        {
            "id": "phone_01",
            "number": "+1-800-555-0199",
            "carrier": "TelcoVoIP Ltd",
            "country": "US",
            "line_type": "VoIP",
            "risk_score": 0.88,
            "label": "Suspicious SMS Gateway"
        },
        # Scenario 2 Target A: Legitimate Clinic reminder
        {
            "id": "phone_02",
            "number": "+1-800-555-0144",
            "carrier": "Bell State Telecom",
            "country": "US",
            "line_type": "Landline",
            "risk_score": 0.05,
            "label": "Acme Community Health SMS"
        },
        # Scenario 2 Target B: Unlinked minor cold call complaint
        {
            "id": "phone_03",
            "number": "+1-800-555-0145",
            "carrier": "Horizon Wireless",
            "country": "US",
            "line_type": "Mobile",
            "risk_score": 0.20,
            "label": "Direct Marketing Line"
        },
        # Scenario 3 Target: Ambiguous / Insufficient Evidence lead
        {
            "id": "phone_04",
            "number": "+1-800-555-0720",
            "carrier": "CloudVoice Services",
            "country": "US",
            "line_type": "Virtual",
            "risk_score": 0.35,
            "label": "Unclassified Caller"
        },
        # Benign control entity
        {
            "id": "phone_05",
            "number": "+1-800-555-0100",
            "carrier": "AT&T Business",
            "country": "US",
            "line_type": "TollFree",
            "risk_score": 0.01,
            "label": "Official Bank Customer Support"
        }
    ],
    "Domain": [
        # Domain linked to Scenario 1
        {
            "id": "dom_01",
            "domain_name": "secure-login-chase-auth.com",
            "registrar": "NameCheap Inc",
            "creation_date": "2026-09-12",
            "ip_address": "198.51.100.44",
            "risk_score": 0.95
        },
        # Second domain in campaign network
        {
            "id": "dom_02",
            "domain_name": "verify-account-portal-net.org",
            "registrar": "Tucows Domains",
            "creation_date": "2026-09-15",
            "ip_address": "198.51.100.45",
            "risk_score": 0.92
        },
        # Legitimate domain for control entity
        {
            "id": "dom_03",
            "domain_name": "acmehealthclinic.org",
            "registrar": "GoDaddy LLC",
            "creation_date": "2018-03-20",
            "ip_address": "104.22.15.8",
            "risk_score": 0.02
        }
    ],
    "Account": [
        # Laundering Crypto Wallet for Scenario 1
        {
            "id": "acc_01",
            "account_id": "ACC-CRYPTO-MULE-8831",
            "platform": "Tether USDT Tron",
            "account_type": "Crypto Wallet",
            "status": "Flagged For Laundering",
            "risk_score": 0.97
        },
        # Telegram Bot Account used for credential delivery
        {
            "id": "acc_02",
            "account_id": "ACC-TG-PHISH-DROP-99",
            "platform": "Telegram",
            "account_type": "Bot Controller",
            "status": "Active Threat",
            "risk_score": 0.94
        },
        # Clinic scheduling account (Scenario 2)
        {
            "id": "acc_03",
            "account_id": "ACC-CLINIC-APPT-SYS",
            "platform": "Twilio SMS",
            "account_type": "Healthcare Notification",
            "status": "Verified Good",
            "risk_score": 0.01
        }
    ],
    "ScamCampaign": [
        # Scenario 1 Campaign
        {
            "id": "camp_01",
            "campaign_id": "CAMP-CHASE-PHISH",
            "name": "Global Bank Phish & Drain Syndicate",
            "theme": "Urgent SMS Bank Account Suspension",
            "first_detected": "2026-09-10",
            "severity": "CRITICAL",
            "status": "Active"
        },
        # Ancillary investment scam campaign
        {
            "id": "camp_02",
            "campaign_id": "CAMP-PIG-BUTCHERING-ALPHA",
            "name": "Fake Liquidity Mining Ring",
            "theme": "High Yield Crypto Staking",
            "first_detected": "2026-08-01",
            "severity": "HIGH",
            "status": "Dormant"
        }
    ],
    "Report": [
        # Victim report linking Phone +1-800-555-0199
        {
            "id": "rep_01",
            "report_id": "REP-10492",
            "source": "US Consumer Fraud Incident Portal",
            "reported_date": "2026-10-01",
            "claim": "Received urgent SMS from +1-800-555-0199 warning debit card was locked, directing to secure-login-chase-auth.com",
            "verified": True,
            "confidence": 0.92
        },
        # Second corroborating report
        {
            "id": "rep_02",
            "report_id": "REP-10515",
            "source": "State Attorney Cyber Complaint Center",
            "reported_date": "2026-10-04",
            "claim": "Credential harvesting attack originating from verify-account-portal-net.org with victim funds funneled into crypto address ACC-CRYPTO-MULE-8831",
            "verified": True,
            "confidence": 0.96
        },
        # Scenario 2 Target B minor report (Isolated marketing complaint)
        {
            "id": "rep_03",
            "report_id": "REP-08812",
            "source": "Public Do-Not-Call Registry",
            "reported_date": "2026-08-14",
            "claim": "Repeated telemarketing offers for solar panels from +1-800-555-0145 without consent",
            "verified": False,
            "confidence": 0.35
        },
        # Scenario 3 Single unverified anonymous report
        {
            "id": "rep_04",
            "report_id": "REP-11001",
            "source": "Anonymous Forum Tip",
            "reported_date": "2026-10-12",
            "claim": "Caller from +1-800-555-0720 hung up after 2 rings, suspect scam test ping",
            "verified": False,
            "confidence": 0.25
        }
    ],
    "Evidence": [
        # Evidence 1: Raw Phishing SMS payload
        {
            "id": "evid_01",
            "evidence_id": "EVID-SMS-RAW-01",
            "type": "Telephony Metadata & Text Dump",
            "description": "Captured SMS: '[ALERT] Chase Account Alert: Unauthorized withdrawal attempt of $480.00. Secure session immediately: https://secure-login-chase-auth.com'",
            "timestamp": "2026-10-01T14:22:10Z",
            "hash_signature": "sha256:4a8c91d4e73b...9f",
            "raw_payload": "{'originating_smsc': '198.51.100.12', 'sender': '+1-800-555-0199', 'shortcode': False}"
        },
        # Evidence 2: DNS & Hosting Forensics
        {
            "id": "evid_02",
            "evidence_id": "EVID-DNS-INFRA-44",
            "type": "DNS & SSL Certificate Telemetry",
            "description": "Certificate Common Name matches 'secure-login-chase-auth.com' hosted on reverse-proxy bulletproof server sharing IP 198.51.100.44 with verify-account-portal-net.org",
            "timestamp": "2026-10-02T08:15:00Z",
            "hash_signature": "sha256:7b1e22f8a1...10",
            "raw_payload": "{'ip': '198.51.100.44', 'asn': 'AS48920 Bulletproof', 'cert_serial': '9827341'}"
        },
        # Evidence 3: On-Chain Blockchain Trace
        {
            "id": "evid_03",
            "evidence_id": "EVID-BLOCKCHAIN-TRACE",
            "type": "Cryptocurrency Transaction Ledger",
            "description": "Funds totaling $24,500 transferred from victim accounts within 18 minutes of credential entry on phishing domain into Tron address ACC-CRYPTO-MULE-8831",
            "timestamp": "2026-10-04T18:40:22Z",
            "hash_signature": "sha256:cc99881122...ee",
            "raw_payload": "{'tx_hash': '0x88f4bc920199...e2', 'amount_usdt': 24500, 'destination': 'ACC-CRYPTO-MULE-8831'}"
        }
    ]
}

# Explicit relationships connecting entities
SEED_RELATIONSHIPS = [
    # --- Scenario 1: Deep Multi-Hop Scam Syndicate ---
    # Phone(+1-800-555-0199) -> REPORTED_IN -> Report(REP-10492)
    {
        "from_label": "Phone", "from_key": "number", "from_val": "+1-800-555-0199",
        "type": "REPORTED_IN",
        "to_label": "Report", "to_key": "report_id", "to_val": "REP-10492",
        "properties": {"reported_date": "2026-10-01", "reported_role": "SMS Sender", "confidence": 0.95}
    },
    # Report(REP-10492) -> LINKED_TO_CAMPAIGN -> ScamCampaign(CAMP-CHASE-PHISH)
    {
        "from_label": "Report", "from_key": "report_id", "from_val": "REP-10492",
        "type": "LINKED_TO_CAMPAIGN",
        "to_label": "ScamCampaign", "to_key": "campaign_id", "to_val": "CAMP-CHASE-PHISH",
        "properties": {"attribution_confidence": 0.94, "attribution_rule": "Matching Phishing Kit Fingerprint", "linked_date": "2026-10-02"}
    },
    # ScamCampaign(CAMP-CHASE-PHISH) -> ASSOCIATED_WITH -> Domain(secure-login-chase-auth.com)
    {
        "from_label": "ScamCampaign", "from_key": "campaign_id", "from_val": "CAMP-CHASE-PHISH",
        "type": "ASSOCIATED_WITH",
        "to_label": "Domain", "to_key": "domain_name", "to_val": "secure-login-chase-auth.com",
        "properties": {"association_type": "Harvesting Domain", "weight": 0.98, "observed_date": "2026-09-12"}
    },
    # Domain(secure-login-chase-auth.com) -> SHARES_DOMAIN -> Domain(verify-account-portal-net.org)
    {
        "from_label": "Domain", "from_key": "domain_name", "from_val": "secure-login-chase-auth.com",
        "type": "ASSOCIATED_WITH",
        "to_label": "Domain", "to_key": "domain_name", "to_val": "verify-account-portal-net.org",
        "properties": {"association_type": "Co-hosted on Bulletproof IP 198.51.100.44", "weight": 0.95, "observed_date": "2026-09-15"}
    },
    # Domain(verify-account-portal-net.org) -> REPORTED_IN -> Report(REP-10515)
    {
        "from_label": "Domain", "from_key": "domain_name", "from_val": "verify-account-portal-net.org",
        "type": "REPORTED_IN",
        "to_label": "Report", "to_key": "report_id", "to_val": "REP-10515",
        "properties": {"reported_date": "2026-10-04", "reported_role": "Phishing Gateway", "confidence": 0.96}
    },
    # Report(REP-10515) -> REFERENCES -> Account(ACC-CRYPTO-MULE-8831)
    {
        "from_label": "Report", "from_key": "report_id", "from_val": "REP-10515",
        "type": "REFERENCES",
        "to_label": "Account", "to_key": "account_id", "to_val": "ACC-CRYPTO-MULE-8831",
        "properties": {"reference_type": "Extracted Drain Wallet", "relevance": 0.98}
    },
    # ScamCampaign(CAMP-CHASE-PHISH) -> ASSOCIATED_WITH -> Account(ACC-TG-PHISH-DROP-99)
    {
        "from_label": "ScamCampaign", "from_key": "campaign_id", "from_val": "CAMP-CHASE-PHISH",
        "type": "ASSOCIATED_WITH",
        "to_label": "Account", "to_key": "account_id", "to_val": "ACC-TG-PHISH-DROP-99",
        "properties": {"association_type": "Exfiltration Channel", "weight": 0.90, "observed_date": "2026-09-20"}
    },
    # Supporting Evidence for Reports and Campaigns:
    # Report(REP-10492) -> SUPPORTED_BY -> Evidence(EVID-SMS-RAW-01)
    {
        "from_label": "Report", "from_key": "report_id", "from_val": "REP-10492",
        "type": "SUPPORTED_BY",
        "to_label": "Evidence", "to_key": "evidence_id", "to_val": "EVID-SMS-RAW-01",
        "properties": {"evidence_strength": "High", "validation_status": "Forensically Verified"}
    },
    # ScamCampaign(CAMP-CHASE-PHISH) -> SUPPORTED_BY -> Evidence(EVID-DNS-INFRA-44)
    {
        "from_label": "ScamCampaign", "from_key": "campaign_id", "from_val": "CAMP-CHASE-PHISH",
        "type": "SUPPORTED_BY",
        "to_label": "Evidence", "to_key": "evidence_id", "to_val": "EVID-DNS-INFRA-44",
        "properties": {"evidence_strength": "High", "validation_status": "Network Telemetry Verified"}
    },
    # Account(ACC-CRYPTO-MULE-8831) -> SUPPORTED_BY -> Evidence(EVID-BLOCKCHAIN-TRACE)
    {
        "from_label": "Account", "from_key": "account_id", "from_val": "ACC-CRYPTO-MULE-8831",
        "type": "SUPPORTED_BY",
        "to_label": "Evidence", "to_key": "evidence_id", "to_val": "EVID-BLOCKCHAIN-TRACE",
        "properties": {"evidence_strength": "Critical", "validation_status": "Cryptographic Proof"}
    },

    # --- Scenario 2: Benign / Unlinked Entities ---
    # Phone(+1-800-555-0144) -> ASSOCIATED_WITH -> Domain(acmehealthclinic.org)
    {
        "from_label": "Phone", "from_key": "number", "from_val": "+1-800-555-0144",
        "type": "ASSOCIATED_WITH",
        "to_label": "Domain", "to_key": "domain_name", "to_val": "acmehealthclinic.org",
        "properties": {"association_type": "Verified Healthcare Organization", "weight": 0.99, "observed_date": "2026-01-10"}
    },
    # Phone(+1-800-555-0144) -> ASSOCIATED_WITH -> Account(ACC-CLINIC-APPT-SYS)
    {
        "from_label": "Phone", "from_key": "number", "from_val": "+1-800-555-0144",
        "type": "ASSOCIATED_WITH",
        "to_label": "Account", "to_key": "account_id", "to_val": "ACC-CLINIC-APPT-SYS",
        "properties": {"association_type": "Automated Appointment System", "weight": 0.98, "observed_date": "2026-01-10"}
    },
    # Target B has only one minor report (NO connection to Target A, NO scam campaigns)
    # Phone(+1-800-555-0145) -> REPORTED_IN -> Report(REP-08812)
    {
        "from_label": "Phone", "from_key": "number", "from_val": "+1-800-555-0145",
        "type": "REPORTED_IN",
        "to_label": "Report", "to_key": "report_id", "to_val": "REP-08812",
        "properties": {"reported_date": "2026-08-14", "reported_role": "Caller", "confidence": 0.35}
    },

    # --- Scenario 3: Ambiguous / Insufficient Evidence ---
    # Phone(+1-800-555-0720) -> REPORTED_IN -> Report(REP-11001)
    {
        "from_label": "Phone", "from_key": "number", "from_val": "+1-800-555-0720",
        "type": "REPORTED_IN",
        "to_label": "Report", "to_key": "report_id", "to_val": "REP-11001",
        "properties": {"reported_date": "2026-10-12", "reported_role": "Unverified Caller", "confidence": 0.25}
    }
]

# Scenario Definitions for UI Demo & Automated Tests
SCENARIO_DEFINITIONS = [
    {
        "id": "scenario_1",
        "title": "Scenario 1: Coordinated Phishing Syndicate (Multi-Hop)",
        "entity_type": "Phone",
        "query_identifier": "+1-800-555-0199",
        "description": "A suspicious SMS sender leads across 4 relationship hops through a victim report, an active bank phishing campaign, bulletproof hosting domains, and an on-chain crypto laundering wallet.",
        "expected_hops": 4,
        "expected_campaign": "CAMP-CHASE-PHISH",
        "expected_evidence_count": 3,
        "expected_confidence": "HIGH_CONFIDENCE_MALICIOUS",
        "why_it_matters": "Demonstrates graph intelligence: on its own, a VoIP phone number looks like basic spam. Traversed through the FalkorDB graph, it exposes the multi-tier infrastructure of an organized financial fraud ring."
    },
    {
        "id": "scenario_2",
        "title": "Scenario 2: Sequential Similarity Non-Connection (Coincidental Numbers)",
        "entity_type": "Phone",
        "query_identifier": "+1-800-555-0144",
        "compare_identifier": "+1-800-555-0145",
        "description": "Two phone numbers with sequential digits (+1-800-555-0144 and +1-800-555-0145) are evaluated. The agent verifies that they belong to completely separate entities with 0 graph relationships and 0 shared threat campaigns.",
        "expected_hops": 0,
        "expected_campaign": None,
        "expected_evidence_count": 0,
        "expected_confidence": "BENIGN_INDEPENDENT",
        "why_it_matters": "Demonstrates precision: prevents false positives by confirming that superficial string similarity does not imply criminal conspiracy without graph evidence."
    },
    {
        "id": "scenario_3",
        "title": "Scenario 3: Insufficient Evidence / Ambiguous Lead",
        "entity_type": "Phone",
        "query_identifier": "+1-800-555-0720",
        "description": "An isolated phone number with only a single unverified complaint and no corroborating domains, accounts, or campaigns in the graph.",
        "expected_hops": 1,
        "expected_campaign": None,
        "expected_evidence_count": 0,
        "expected_confidence": "INSUFFICIENT_EVIDENCE",
        "why_it_matters": "Demonstrates calibrated reasoning: the agent resists hallucinating maliciousness, clearly flags missing evidence, and suggests monitoring rather than premature escalation."
    }
]
