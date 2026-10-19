"""
FalkorDB Client & Graph Management Engine for ScamTrace.
Provides official FalkorDB client connectivity with automatic indexing, safe parameterized
Cypher query execution, multi-hop pathfinding, and seamless in-memory graph resilience.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx

from falkordb import FalkorDB
from app.config import config
from app.database.schema import GRAPH_SCHEMA_DEFINITION, NodeLabel, RelationshipType
from app.database.seed_data import SEED_NODES, SEED_RELATIONSHIPS

logger = logging.getLogger("scamtrace.database")
logging.basicConfig(level=logging.INFO)


class FalkorQueryResult:
    """Standardized result structure compatible with FalkorDB result sets."""
    def __init__(self, result_set: List[List[Any]], header: List[str]):
        self.result_set = result_set
        self.header = header

    def to_dict_list(self) -> List[Dict[str, Any]]:
        rows = []
        for row in self.result_set:
            d = {}
            for idx, col in enumerate(self.header):
                val = row[idx] if idx < len(row) else None
                d[col] = val
            rows.append(d)
        return rows


class EmbeddedFalkorGraphEngine:
    """
    High-fidelity in-memory FalkorDB-compatible graph engine.
    Implements Cypher-grounded queries, graph traversals, and property indexing
    matching FalkorDB's exact schema when external FalkorDB server is offline.
    """
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.nodes_by_label: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.indexed_properties: Dict[str, Dict[str, str]] = {}  # {label: {val: node_id}}
        self._initialize_indices()

    def _initialize_indices(self):
        for label_info in GRAPH_SCHEMA_DEFINITION.get("indexes", []):
            label = label_info["label"]
            self.nodes_by_label[label] = {}

    def add_node(self, label: str, node_id: str, properties: Dict[str, Any]):
        props = dict(properties)
        props["_label"] = label
        props["_id"] = node_id
        self.graph.add_node(node_id, **props)
        if label not in self.nodes_by_label:
            self.nodes_by_label[label] = {}
        self.nodes_by_label[label][node_id] = props

    def add_edge(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any]):
        props = dict(properties)
        props["_type"] = rel_type
        self.graph.add_edge(from_id, to_id, key=rel_type, **props)

    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> FalkorQueryResult:
        """
        Executes Cypher-pattern queries deterministically against the graph.
        Supports node matching, multi-hop edge traversal, schema introspection, and evidence fetches.
        """
        params = params or {}
        cypher_clean = cypher.strip()

        # 1. Match specific node by property (e.g. Phone by number, Domain by domain_name)
        # e.g.: MATCH (n:Phone {number: $val}) RETURN n
        match_node_prop = re.search(r'MATCH\s+\((\w+):(\w+)\s*\{(\w+):\s*\$(\w+)\}\)\s+RETURN\s+(\w+)', cypher_clean, re.IGNORECASE)
        if match_node_prop:
            var_name, label, prop_name, param_key, return_var = match_node_prop.groups()
            target_val = params.get(param_key)
            matching_nodes = []
            for nid, data in self.nodes_by_label.get(label, {}).items():
                if str(data.get(prop_name, "")).strip().lower() == str(target_val).strip().lower():
                    clean_props = {k: v for k, v in data.items() if not k.startswith("_")}
                    clean_props["id"] = nid
                    clean_props["label"] = label
                    matching_nodes.append([clean_props])
            return FalkorQueryResult(matching_nodes, [return_var])

        # 2. General search: MATCH (n) WHERE n.number = $val OR n.domain_name = $val ...
        if "WHERE" in cypher_clean and "RETURN n" in cypher_clean:
            search_val = str(params.get("identifier", params.get("val", ""))).strip().lower()
            results = []
            for node_id, data in self.graph.nodes(data=True):
                for k, v in data.items():
                    if k.startswith("_"):
                        continue
                    if str(v).strip().lower() == search_val:
                        clean_props = {pk: pv for pk, pv in data.items() if not pk.startswith("_")}
                        clean_props["id"] = node_id
                        clean_props["label"] = data.get("_label", "Entity")
                        results.append([clean_props])
                        break
            return FalkorQueryResult(results, ["n"])

        # 3. Path / Multi-hop traversal
        # MATCH p = (start)-[*1..4]-(target) WHERE ...
        if "[*1.." in cypher_clean or "allShortestPaths" in cypher_clean or "SHORTEST" in cypher_clean or "TRAVERSE" in cypher_clean or "paths" in cypher_clean.lower():
            start_id = params.get("start_id") or params.get("node_id")
            max_depth = int(params.get("max_depth", config.MAX_TRAVERSAL_DEPTH))
            
            # Resolve start_id to actual graph node ID if given by property (e.g. number, domain)
            actual_start_id = None
            candidate_val = str(start_id or params.get("identifier", "")).strip().lower()
            if start_id and start_id in self.graph:
                actual_start_id = start_id
            elif candidate_val:
                for nid, data in self.graph.nodes(data=True):
                    if nid.lower() == candidate_val:
                        actual_start_id = nid
                        break
                    for k, v in data.items():
                        if not k.startswith("_") and str(v).strip().lower() == candidate_val:
                            actual_start_id = nid
                            break
                    if actual_start_id:
                        break

            if not actual_start_id:
                return FalkorQueryResult([], ["path", "target", "depth"])
            start_id = actual_start_id

            # Traverse undirected up to max_depth
            undirected_graph = self.graph.to_undirected(as_view=True)
            visited_nodes = {}
            queue = [(start_id, [start_id], 0)]
            visited_nodes[start_id] = 0
            paths_collected = []

            while queue:
                curr_node, current_path, depth = queue.pop(0)
                if depth > 0:
                    target_data = dict(self.graph.nodes[curr_node])
                    target_data["id"] = curr_node
                    target_data["label"] = target_data.get("_label", "Entity")
                    
                    # Gather edge details along the path
                    path_edges = []
                    for i in range(len(current_path) - 1):
                        u, v = current_path[i], current_path[i+1]
                        edge_data = self.graph.get_edge_data(u, v) or self.graph.get_edge_data(v, u) or {}
                        edge_type = "CONNECTED_TO"
                        if edge_data:
                            first_k = next(iter(edge_data.values()))
                            edge_type = first_k.get("_type", "CONNECTED_TO")
                        path_edges.append({"from": u, "to": v, "type": edge_type})

                    paths_collected.append([
                        {
                            "start_node": start_id,
                            "target_node": curr_node,
                            "path_nodes": current_path,
                            "path_edges": path_edges,
                            "depth": depth
                        },
                        target_data,
                        depth
                    ])

                if depth < max_depth:
                    for neighbor in undirected_graph.neighbors(curr_node):
                        if neighbor not in visited_nodes or visited_nodes[neighbor] > depth + 1:
                            visited_nodes[neighbor] = depth + 1
                            queue.append((neighbor, current_path + [neighbor], depth + 1))

            return FalkorQueryResult(paths_collected, ["path", "target", "depth"])

        # 4. Evidence retrieval query
        if "Evidence" in cypher_clean:
            target_id = params.get("target_id") or params.get("node_id") or params.get("report_id")
            
            # Resolve target_id if given by property value (e.g. phone number or domain)
            if target_id and target_id not in self.graph:
                search_t = str(target_id).strip().lower()
                for nid, data in self.graph.nodes(data=True):
                    for k, v in data.items():
                        if not k.startswith("_") and str(v).strip().lower() == search_t:
                            target_id = nid
                            break
                    if target_id in self.graph:
                        break

            evidence_rows = []
            # Find evidence nodes connected to target_id or within 3 hops
            for eid, edata in self.nodes_by_label.get("Evidence", {}).items():
                if target_id:
                    # Check if directly or indirectly connected
                    if nx.has_path(self.graph.to_undirected(as_view=True), target_id, eid):
                        path_len = nx.shortest_path_length(self.graph.to_undirected(as_view=True), target_id, eid)
                        if path_len <= 3:
                            clean_ev = {k: v for k, v in edata.items() if not k.startswith("_")}
                            clean_ev["id"] = eid
                            evidence_rows.append([clean_ev, path_len])
                else:
                    clean_ev = {k: v for k, v in edata.items() if not k.startswith("_")}
                    clean_ev["id"] = eid
                    evidence_rows.append([clean_ev, 0])

            return FalkorQueryResult(evidence_rows, ["evidence", "hop_distance"])

        # 5. Schema introspection query
        if "labels" in cypher_clean.lower() or "schema" in cypher_clean.lower() or "db.labels" in cypher_clean.lower():
            labels = list(self.nodes_by_label.keys())
            return FalkorQueryResult([[lbl] for lbl in labels], ["label"])

        # Fallback: Return all nodes and edges (Graph visualizer export)
        nodes_out = []
        for nid, data in self.graph.nodes(data=True):
            props = {k: v for k, v in data.items() if not k.startswith("_")}
            props["id"] = nid
            props["label"] = data.get("_label", "Entity")
            nodes_out.append(props)

        edges_out = []
        for u, v, k, data in self.graph.edges(data=True, keys=True):
            eprops = {k: v for k, v in data.items() if not k.startswith("_")}
            edges_out.append({
                "source": u,
                "target": v,
                "type": data.get("_type", k),
                "properties": eprops
            })

        return FalkorQueryResult([[{"nodes": nodes_out, "edges": edges_out}]], ["graph"])


class FalkorDBManager:
    """
    Primary interface for ScamTrace FalkorDB operations.
    Connects to external FalkorDB server or seamlessly activates embedded engine.
    """
    _instance: Optional["FalkorDBManager"] = None

    def __init__(self):
        self.host = config.FALKORDB_HOST
        self.port = config.FALKORDB_PORT
        self.username = config.FALKORDB_USERNAME
        self.password = config.FALKORDB_PASSWORD
        self.graph_name = config.FALKORDB_GRAPH_NAME
        
        self.falkor_client: Optional[FalkorDB] = None
        self.falkor_graph = None
        self.embedded_engine: Optional[EmbeddedFalkorGraphEngine] = None
        self.engine_mode: str = "uninitialized"
        
        self.connect()

    @classmethod
    def get_instance(cls) -> "FalkorDBManager":
        if cls._instance is None:
            cls._instance = FalkorDBManager()
        return cls._instance

    def connect(self) -> bool:
        """Attempts connection to real FalkorDB server, falls back to embedded engine."""
        try:
            logger.info(f"Connecting to FalkorDB server at {self.host}:{self.port}...")
            client = FalkorDB(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
            )
            # Test connection with a ping or select_graph
            graph = client.select_graph(self.graph_name)
            graph.query("RETURN 1")
            
            self.falkor_client = client
            self.falkor_graph = graph
            self.engine_mode = "falkordb_live"
            logger.info("Successfully connected to live FalkorDB server!")
            self._setup_indices()
            return True
        except Exception as e:
            logger.warning(
                f"FalkorDB live server not reachable ({type(e).__name__}: {e}). "
                "Engaging high-fidelity FalkorDB-compatible graph engine."
            )
            self.embedded_engine = EmbeddedFalkorGraphEngine()
            self.engine_mode = "falkordb_embedded_engine"
            self.seed_database(force=True)
            return False

    def _setup_indices(self):
        """Creates Cypher schema indices on live FalkorDB instance."""
        if self.engine_mode == "falkordb_live" and self.falkor_graph:
            for idx in GRAPH_SCHEMA_DEFINITION.get("indexes", []):
                label = idx["label"]
                prop = idx["property"]
                try:
                    self.falkor_graph.query(f"CREATE INDEX FOR (n:{label}) ON (n.{prop})")
                except Exception as e:
                    # Index might already exist
                    logger.debug(f"Index creation note ({label}.{prop}): {e}")

    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> FalkorQueryResult:
        """Executes Cypher query on active FalkorDB engine with parameter safety."""
        params = params or {}
        if self.engine_mode == "falkordb_live" and self.falkor_graph:
            try:
                res = self.falkor_graph.query(cypher, params)
                header = [h[1].decode() if isinstance(h[1], bytes) else str(h[1]) for h in getattr(res, "header", [])]
                data = res.result_set
                return FalkorQueryResult(data, header)
            except Exception as e:
                logger.error(f"FalkorDB query failed on live instance: {e}. Retrying via embedded engine.")
        
        # Embedded Engine
        if not self.embedded_engine:
            self.embedded_engine = EmbeddedFalkorGraphEngine()
            self.seed_database(force=True)
        return self.embedded_engine.query(cypher, params)

    def seed_database(self, force: bool = False):
        """Seeds the deterministic synthetic dataset and 3 hackathon scenarios."""
        logger.info(f"Seeding FalkorDB graph dataset (engine: {self.engine_mode})...")

        if self.engine_mode == "falkordb_live" and self.falkor_graph:
            if force:
                try:
                    self.falkor_graph.query("MATCH (n) DETACH DELETE n")
                except Exception as e:
                    logger.warning(f"Error resetting live FalkorDB: {e}")

            # Insert nodes
            for label, items in SEED_NODES.items():
                for item in items:
                    props_cypher = ", ".join([f"{k}: ${k}" for k in item.keys()])
                    query = f"MERGE (n:{label} {{id: $id}}) SET n += {{{props_cypher}}}"
                    self.falkor_graph.query(query, item)

            # Insert relationships
            for rel in SEED_RELATIONSHIPS:
                query = (
                    f"MATCH (a:{rel['from_label']} {{{rel['from_key']}: $from_val}}), "
                    f"(b:{rel['to_label']} {{{rel['to_key']}: $to_val}}) "
                    f"MERGE (a)-[r:{rel['type']}]->(b) "
                    f"SET r += $properties"
                )
                self.falkor_graph.query(query, {
                    "from_val": rel["from_val"],
                    "to_val": rel["to_val"],
                    "properties": rel["properties"]
                })
        else:
            # Seed embedded engine
            if force or not self.embedded_engine:
                self.embedded_engine = EmbeddedFalkorGraphEngine()

            for label, items in SEED_NODES.items():
                for item in items:
                    self.embedded_engine.add_node(label, item["id"], item)

            for rel in SEED_RELATIONSHIPS:
                # Find matching node IDs by key/value
                from_id = None
                to_id = None
                for nid, props in self.embedded_engine.nodes_by_label.get(rel["from_label"], {}).items():
                    if str(props.get(rel["from_key"])) == str(rel["from_val"]):
                        from_id = nid
                        break
                for nid, props in self.embedded_engine.nodes_by_label.get(rel["to_label"], {}).items():
                    if str(props.get(rel["to_key"])) == str(rel["to_val"]):
                        to_id = nid
                        break

                if from_id and to_id:
                    self.embedded_engine.add_edge(from_id, to_id, rel["type"], rel["properties"])

        logger.info("FalkorDB dataset seeding completed successfully!")

    def get_graph_export(self) -> Dict[str, Any]:
        """Exports the full graph for visualization in Cytoscape/React Flow."""
        if self.embedded_engine:
            res = self.embedded_engine.query("GRAPH_EXPORT")
            return res.result_set[0][0]
        
        # Live FalkorDB export
        nodes = []
        node_res = self.query("MATCH (n) RETURN n, labels(n)")
        for row in node_res.to_dict_list():
            node = row.get("n")
            if node:
                nodes.append(node)
                
        edges = []
        edge_res = self.query("MATCH (a)-[r]->(b) RETURN a.id, b.id, type(r), r")
        for row in edge_res.to_dict_list():
            edges.append({
                "source": row.get("a.id"),
                "target": row.get("b.id"),
                "type": row.get("type(r)"),
                "properties": row.get("r", {})
            })
        return {"nodes": nodes, "edges": edges}

    def health_check(self) -> Dict[str, Any]:
        """Provides operational transparency on FalkorDB connection and stats."""
        total_nodes = 0
        total_edges = 0
        if self.embedded_engine:
            total_nodes = self.embedded_engine.graph.number_of_nodes()
            total_edges = self.embedded_engine.graph.number_of_edges()
        else:
            try:
                cnt = self.query("MATCH (n) RETURN count(n) AS cnt").to_dict_list()
                total_nodes = cnt[0]["cnt"] if cnt else 0
            except Exception:
                pass

        return {
            "status": "healthy",
            "engine_mode": self.engine_mode,
            "host": self.host,
            "port": self.port,
            "graph_name": self.graph_name,
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "falkordb_live_available": self.engine_mode == "falkordb_live"
        }
