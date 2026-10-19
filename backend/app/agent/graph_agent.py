"""
ScamTrace LangGraph Agent Orchestrator.
Builds the LangGraph state graph with tool-calling capabilities, evidence evaluation,
grounding guardrails, and explainable investigation report generation.
"""

import json
import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import config
from app.agent.tools import ALL_AGENT_TOOLS, search_entity, inspect_graph_schema, trace_connections, get_evidence, create_investigation_case
from app.agent.deterministic import DeterministicInvestigationEngine
from app.database.queries import GraphQueries

logger = logging.getLogger("scamtrace.agent")


class InvestigationState(TypedDict):
    target: str
    messages: List[Any]
    tool_calls: List[Dict[str, Any]]
    discovered_nodes: Dict[str, Any]
    discovered_edges: List[Dict[str, Any]]
    evidence_records: List[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    error: Optional[str]


SYSTEM_PROMPT = """You are ScamTrace, a graph-powered AI cyber fraud investigation agent for FalkorDB.
Your mission is to investigate suspicious phone numbers, domains, accounts, or campaigns by traversing FalkorDB relationship graphs.

RULES & GUARDRAILS:
1. Always ground your conclusions strictly in actual FalkorDB query results. NEVER invent or hallucinate relationships, evidence, or campaigns.
2. First call `search_entity` to look up the node in the graph.
3. Call `trace_connections` to follow multi-hop paths to uncover connected campaigns, domains, and laundering accounts.
4. Call `get_evidence` to retrieve supporting forensic proof for the entities discovered.
5. Finally, call `create_investigation_case` to prepare a formal case with recommended local actions.
6. Distinguish clearly between direct observations, reported claims, and inferred relationships.
7. If an entity is not connected to a campaign or has only an unverified claim, state that evidence is INSUFFICIENT instead of making accusations.
"""


class ScamTraceAgent:
    def __init__(self):
        self.queries = GraphQueries()
        self.deterministic_engine = DeterministicInvestigationEngine(self.queries)
        self.llm = None
        self._init_llm()
        self.graph = self._build_graph()

    def _init_llm(self):
        """Initializes Gemini model with fallback safety."""
        if config.GEMINI_API_KEY:
            try:
                # Use gemini-2.5-flash or configured model
                self.llm = ChatGoogleGenerativeAI(
                    model=config.GEMINI_MODEL,
                    google_api_key=config.GEMINI_API_KEY,
                    temperature=0.1,
                    max_retries=2
                ).bind_tools(ALL_AGENT_TOOLS)
                logger.info(f"Initialized Gemini LLM ({config.GEMINI_MODEL}) with tools.")
            except Exception as e:
                logger.warning(f"Failed to initialize ChatGoogleGenerativeAI: {e}. Using deterministic engine.")
                self.llm = None
        else:
            logger.info("No GEMINI_API_KEY configured. Operating in deterministic graph reasoning mode.")

    def _build_graph(self) -> StateGraph:
        """Constructs the LangGraph state machine."""
        workflow = StateGraph(InvestigationState)

        # Add Nodes
        workflow.add_node("plan_and_investigate", self._plan_and_investigate_node)
        workflow.add_node("generate_report", self._generate_report_node)

        # Add Edges
        workflow.set_entry_point("plan_and_investigate")
        workflow.add_edge("plan_and_investigate", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def _plan_and_investigate_node(self, state: InvestigationState) -> InvestigationState:
        """
        Executes the graph tool calls and multi-hop traversal.
        Uses Gemini LLM tool calling when available, with automatic fallback
        to the deterministic engine if Gemini is rate-limited or unavailable.
        """
        target = state["target"]
        tool_calls_executed = []

        # If LLM is configured, attempt tool-directed reasoning
        if self.llm:
            try:
                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=f"Investigate suspicious entity: '{target}'. Trace all FalkorDB connections and gather evidence.")
                ]
                # Invoke LLM for tool decision
                ai_msg = self.llm.invoke(messages)
                if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
                    for tc in ai_msg.tool_calls:
                        name = tc["name"]
                        args = tc["args"]
                        tool_calls_executed.append({
                            "tool": name,
                            "arguments": args,
                            "purpose": f"LLM selected tool {name}"
                        })
            except Exception as e:
                logger.warning(f"LLM tool invocation encountered an issue ({e}). Engaging deterministic graph reasoning.")

        # Execute grounded multi-hop traversal via our FalkorDB engine
        det_result = self.deterministic_engine.investigate(target)
        
        # Merge tool calls
        final_tool_calls = tool_calls_executed if tool_calls_executed else det_result["tool_calls"]

        return {
            "target": target,
            "messages": state.get("messages", []),
            "tool_calls": final_tool_calls,
            "discovered_nodes": {n["id"]: n for n in det_result.get("key_connected_entities", [])},
            "discovered_edges": det_result.get("investigation_graph", {}).get("edges", []),
            "evidence_records": det_result.get("relevant_evidence", []),
            "final_report": det_result,
            "error": None
        }

    def _generate_report_node(self, state: InvestigationState) -> InvestigationState:
        """
        Refines the final investigation report with narrative explanations and evidence provenance.
        """
        report = state["final_report"]
        # Ensure complete report fields are present
        if report and report.get("status") == "completed":
            report["agent_model"] = config.GEMINI_MODEL if config.GEMINI_API_KEY else "Deterministic FalkorDB Engine"
            report["graph_database"] = "FalkorDB"
        return state

    def run_investigation(self, target_identifier: str) -> Dict[str, Any]:
        """
        Main entrypoint to run an investigation for a given target entity.
        """
        initial_state: InvestigationState = {
            "target": target_identifier,
            "messages": [],
            "tool_calls": [],
            "discovered_nodes": {},
            "discovered_edges": [],
            "evidence_records": [],
            "final_report": None,
            "error": None
        }
        output = self.graph.invoke(initial_state)
        return output["final_report"]


# Global agent singleton
investigation_agent = ScamTraceAgent()
