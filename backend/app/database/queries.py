"""
ScamTrace Parameterized Cypher Queries.
Provides standardized, injection-safe Cypher queries for the LangGraph agent and API.
"""

from typing import Dict, List, Any, Optional
from app.database.falkor_client import FalkorDBManager, FalkorQueryResult


class GraphQueries:
    def __init__(self, db_manager: Optional[FalkorDBManager] = None):
        self.db = db_manager or FalkorDBManager.get_instance()

    def search_entity(self, identifier: str) -> List[Dict[str, Any]]:
        """
        Searches for an entity by phone number, domain name, account ID, or campaign ID.
        """
        cypher = """
        MATCH (n)
        WHERE n.number = $val 
           OR n.domain_name = $val 
           OR n.account_id = $val 
           OR n.campaign_id = $val 
           OR n.id = $val
        RETURN n
        """
        res = self.db.query(cypher, {"val": identifier})
        nodes = []
        for row in res.to_dict_list():
            node = row.get("n")
            if node:
                nodes.append(node)
        return nodes

    def trace_connections(self, entity_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Traverses relationships up to max_depth from a starting node.
        Returns paths, intermediate edges, connected entities, and hop distances.
        """
        cypher = f"""
        MATCH p = (start)-[*1..{max_depth}]-(target)
        WHERE start.id = $start_id OR start.number = $start_id
        RETURN p AS path, target, length(p) AS depth
        """
        res = self.db.query(cypher, {"start_id": entity_id, "max_depth": max_depth})
        paths = []
        for row in res.to_dict_list():
            paths.append(row)
        return paths

    def get_evidence(self, target_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all evidence records supporting or linked to an entity, report, or campaign.
        """
        cypher = """
        MATCH (target)-[:SUPPORTED_BY]->(e:Evidence)
        WHERE target.id = $target_id OR target.report_id = $target_id OR target.campaign_id = $target_id
        RETURN e AS evidence, 1 AS hop_distance
        """
        res = self.db.query(cypher, {"target_id": target_id})
        evidence_items = []
        for row in res.to_dict_list():
            ev = row.get("evidence")
            if ev:
                ev["hop_distance"] = row.get("hop_distance", 1)
                evidence_items.append(ev)
        return evidence_items

    def inspect_schema(self) -> Dict[str, Any]:
        """
        Introspects available node labels, properties, and relationship types.
        """
        from app.database.schema import GRAPH_SCHEMA_DEFINITION
        health = self.db.health_check()
        return {
            "schema": GRAPH_SCHEMA_DEFINITION,
            "database_stats": health
        }

    def find_path_between(self, source_val: str, target_val: str) -> Optional[Dict[str, Any]]:
        """
        Finds the shortest relationship path between two entities if one exists.
        """
        # Search for both entities
        src_nodes = self.search_entity(source_val)
        tgt_nodes = self.search_entity(target_val)
        
        if not src_nodes or not tgt_nodes:
            return None

        src_id = src_nodes[0]["id"]
        tgt_id = tgt_nodes[0]["id"]

        if self.db.embedded_engine:
            import networkx as nx
            undir = self.db.embedded_engine.graph.to_undirected(as_view=True)
            if nx.has_path(undir, src_id, tgt_id):
                path = nx.shortest_path(undir, src_id, tgt_id)
                edges = []
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    edata = self.db.embedded_engine.graph.get_edge_data(u, v) or self.db.embedded_engine.graph.get_edge_data(v, u) or {}
                    etype = "CONNECTED_TO"
                    if edata:
                        etype = next(iter(edata.values())).get("_type", "CONNECTED_TO")
                    edges.append({"from": u, "to": v, "type": etype})
                return {
                    "connected": True,
                    "path_nodes": path,
                    "path_edges": edges,
                    "hop_count": len(path) - 1
                }
            return {
                "connected": False,
                "path_nodes": [],
                "path_edges": [],
                "hop_count": 0,
                "message": f"No relationship path connects '{source_val}' and '{target_val}' in the graph."
            }

        # Live FalkorDB shortest path query
        cypher = """
        MATCH (a {id: $src}), (b {id: $tgt}),
              p = shortestPath((a)-[*]-(b))
        RETURN p
        """
        res = self.db.query(cypher, {"src": src_id, "tgt": tgt_id})
        rows = res.to_dict_list()
        if rows:
            return {"connected": True, "path": rows[0].get("p")}
        return {"connected": False, "message": "No connection found."}
