"""
ScamTrace FalkorDB Model Context Protocol (MCP) Server.
Implements the standard MCP JSON-RPC 2.0 protocol over STDIO to expose FalkorDB
graph investigation tools to any external MCP host (Claude, Cursor, Antigravity, etc.).
"""

import sys
import json
import logging
from typing import Dict, Any, List

from app.database.queries import GraphQueries
from app.database.schema import GRAPH_SCHEMA_DEFINITION

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("scamtrace.mcp")

queries = GraphQueries()

MCP_TOOLS_MANIFEST = [
    {
        "name": "falkordb_search_entity",
        "description": "Search FalkorDB for a phone number, domain, account, or campaign node.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "identifier": {"type": "string", "description": "Entity identifier (e.g. '+1-800-555-0199', domain name, or account ID)"}
            },
            "required": ["identifier"]
        }
    },
    {
        "name": "falkordb_inspect_schema",
        "description": "Introspect FalkorDB graph schema, node labels, properties, and relationship types.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "falkordb_trace_connections",
        "description": "Traverse relationships in FalkorDB up to max_depth (1 to 4 hops) from an entity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Starting node ID or identifier"},
                "max_depth": {"type": "integer", "description": "Max relationship hops (1-4)", "default": 3}
            },
            "required": ["entity_id"]
        }
    },
    {
        "name": "falkordb_get_evidence",
        "description": "Retrieve forensic evidence records supporting an entity, report, or campaign in FalkorDB.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_id": {"type": "string", "description": "Node ID, report ID, or campaign ID"}
            },
            "required": ["target_id"]
        }
    },
    {
        "name": "falkordb_create_case",
        "description": "Assemble a formal local investigation case with evidence IDs and proposed action.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "target_entity": {"type": "string"},
                "findings": {"type": "string"},
                "evidence_ids": {"type": "array", "items": {"type": "string"}},
                "recommended_action": {"type": "string"}
            },
            "required": ["title", "target_entity", "findings", "recommended_action"]
        }
    }
]


def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches tool calls to FalkorDB queries."""
    if tool_name == "falkordb_search_entity":
        ident = arguments.get("identifier", "")
        res = queries.search_entity(ident)
        return {"entities": res, "count": len(res)}
    
    elif tool_name == "falkordb_inspect_schema":
        return queries.inspect_schema()

    elif tool_name == "falkordb_trace_connections":
        eid = arguments.get("entity_id", "")
        depth = int(arguments.get("max_depth", 3))
        paths = queries.trace_connections(eid, max_depth=depth)
        return {"paths": paths, "count": len(paths)}

    elif tool_name == "falkordb_get_evidence":
        tid = arguments.get("target_id", "")
        ev = queries.get_evidence(tid)
        return {"evidence": ev, "count": len(ev)}

    elif tool_name == "falkordb_create_case":
        return {
            "status": "case_created",
            "title": arguments.get("title"),
            "target": arguments.get("target_entity"),
            "requires_human_approval": True
        }
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def run_stdio_server():
    """Main loop reading JSON-RPC 2.0 messages from stdin and replying to stdout."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": MCP_TOOLS_MANIFEST}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                tool_res = handle_tool_call(tool_name, args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(tool_res, default=str)}]
                    }
                }
            elif method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "scamtrace-falkordb-mcp", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not implemented."}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
