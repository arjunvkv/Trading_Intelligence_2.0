"""
TOPOLOGICAL MANIFOLD ENGINE
Maintains the organic, high-dimensional directed sovereign macro causal graph.
Integrates Hawkes self-exciting processes, Shannon surprisal, Transfer Entropy,
and Community Detection without artificial anchors or asset hardcodes.
"""

import time
import math
from typing import Dict, List, Any, Tuple, Optional, Set
import networkx as nx

from ..core.point_process import HawkesProcessEstimator, SurprisalCalculator
from ..core.entity_extractor import MacroEntityExtractor
from ..core.causal_discovery import CausalDiscoveryEngine
from ..core.community_detector import CommunityDetector

class TopologicalManifold:
    HALF_LIVES = {
        "SOVEREIGN_CENTRAL_BANK": 28800.0, # 8 hours
        "GEOPOLITICAL_KINETIC": 14400.0,   # 4 hours
        "SOVEREIGN_YIELD": 7200.0,         # 2 hours
        "CURRENCY_RESERVE": 7200.0,        # 2 hours
        "ENERGY_FLOW": 7200.0,             # 2 hours
        "INDUSTRIAL_DEMAND": 7200.0,       # 2 hours
        "VOLATILITY_LIQUIDITY": 3600.0,    # 1 hour
        "CROWD_DIVERGENCE": 2700.0,        # 45 mins
        "DEFAULT": 7200.0                  # 2 hours
    }

    def __init__(self, max_nodes: int = 1200):
        self.max_nodes = max_nodes
        self.extractor = MacroEntityExtractor()
        self.hawkes = HawkesProcessEstimator()
        self.surprisal = SurprisalCalculator()
        self.causal_engine = CausalDiscoveryEngine()
        self.community_detector = CommunityDetector()

        # Topological State
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # Directed Edge weights: (u, v) -> weight
        self.edge_weights: Dict[Tuple[str, str], float] = {}
        self.edge_timestamps: Dict[Tuple[str, str], float] = {}
        
        # Temporal observation logs for causal discovery
        self.entity_occurrences: Dict[str, List[float]] = {}
        
        self.last_community_update: float = 0.0
        self.community_names: Dict[int, str] = {}
        self.active_cascades: List[List[str]] = []

    def ingest_document(self, doc: Dict[str, Any]) -> List[str]:
        """
        Processes a single incoming macro wire or intelligence document.
        Extracts entities, updates arrival time-series, and updates edges.
        """
        title = doc.get("title", "")
        summary = doc.get("summary", "")
        text = f"{title}. {summary}"
        source_type = doc.get("source_type", "SOVEREIGN_CENTRAL_BANK")
        now = doc.get("timestamp", time.time())

        # Extract macro entities
        entities = self.extractor.extract_entities(text)
        if not entities:
            return []

        entity_names = [e.get("name") or e.get("label") or e["id"] for e in entities]
        entity_category_map = {(e.get("name") or e.get("label") or e["id"]): e.get("category", source_type) for e in entities}

        # Update node representations
        for name in entity_names:
            category = entity_category_map.get(name, source_type)
            if name not in self.entity_occurrences:
                self.entity_occurrences[name] = []
            self.entity_occurrences[name].append(now)

            # Register with surprisal calculator
            self.surprisal.register_entity(name)

            if name not in self.nodes:
                self.nodes[name] = {
                    "id": name,
                    "label": name,
                    "category": category,
                    "created_at": now,
                    "last_updated": now,
                    "observation_count": 1,
                    "source_type": source_type,
                    "hawkes_lambda": 0.0,
                    "branching_ratio": 0.0,
                    "surprisal": 0.0,
                    "community_id": 0,
                    "community_name": "Emergent Cluster"
                }
            else:
                node = self.nodes[name]
                node["last_updated"] = now
                node["observation_count"] += 1
                if category != "UNKNOWN" and node["category"] in ["UNKNOWN", "DEFAULT"]:
                    node["category"] = category

        # Update edges (pairwise co-occurrence within the causal document horizon)
        n = len(entity_names)
        for i in range(n):
            for j in range(i + 1, n):
                u = entity_names[i]
                v = entity_names[j]
                if u == v:
                    continue
                # Symmetric initial co-occurrence, directionality assigned via Transfer Entropy
                pair1 = (u, v)
                pair2 = (v, u)
                self.edge_weights[pair1] = self.edge_weights.get(pair1, 0.0) + 1.0
                self.edge_weights[pair2] = self.edge_weights.get(pair2, 0.0) + 1.0
                self.edge_timestamps[pair1] = now
                self.edge_timestamps[pair2] = now

        return entity_names

    def update_topology(self, force_full: bool = False):
        """
        Executes temporal half-life decay, recalculates Hawkes intensities,
        surprisals, Transfer Entropy, and community partitions.
        """
        now = time.time()

        # 1. Temporal Half-Life Decay of Nodes & Pruning
        dead_nodes = []
        for name, node in self.nodes.items():
            stype = node.get("category", "DEFAULT")
            hl = self.HALF_LIVES.get(stype, self.HALF_LIVES["DEFAULT"])
            age = now - node["last_updated"]
            decay_factor = math.exp(- (math.log(2) * age) / hl)
            
            # Decay effective observation count
            node["effective_weight"] = node["observation_count"] * decay_factor

            # Culling threshold: 24h of inactivity or near-zero weight
            if age > 86400.0 or (age > hl * 3 and node["observation_count"] < 2):
                dead_nodes.append(name)

        for name in dead_nodes:
            self.nodes.pop(name, None)
            self.entity_occurrences.pop(name, None)

        # 2. Temporal Edge Decay & Dead Node Link Clean-up
        dead_edges = []
        for (u, v), w in self.edge_weights.items():
            if u not in self.nodes or v not in self.nodes:
                dead_edges.append((u, v))
                continue
            edge_age = now - self.edge_timestamps.get((u, v), now)
            decay_factor = math.exp(- (math.log(2) * edge_age) / 7200.0)
            decayed_w = w * decay_factor
            if decayed_w < 0.05 or edge_age > 43200.0:
                dead_edges.append((u, v))
            else:
                self.edge_weights[(u, v)] = decayed_w

        for edge in dead_edges:
            self.edge_weights.pop(edge, None)
            self.edge_timestamps.pop(edge, None)

        # 3. Calculate Hawkes Point Process & Surprisal for active nodes
        for name, node in self.nodes.items():
            times = self.entity_occurrences.get(name, [])
            # Hawkes intensity
            h_metrics = self.hawkes.estimate(times, t_eval=now)
            node["hawkes_lambda"] = h_metrics["lambda_t"]
            node["branching_ratio"] = h_metrics["branching_ratio"]
            node["hawkes_excited"] = h_metrics["is_excited"]
            
            # Shannon Surprisal & ICF
            node["surprisal"] = self.surprisal.calculate_surprisal(name)
            node["icf"] = self.surprisal.calculate_icf(name)

        # 4. Construct NetworkX Graph for Community Detection & Centralities
        G = nx.DiGraph()
        for name, node in self.nodes.items():
            G.add_node(name, **node)

        for (u, v), w in self.edge_weights.items():
            if u in self.nodes and v in self.nodes:
                G.add_edge(u, v, weight=w)

        # Calculate Degree Centrality
        if len(G) > 0:
            deg_centrality = nx.degree_centrality(G)
            for name, c in deg_centrality.items():
                if name in self.nodes:
                    self.nodes[name]["centrality"] = round(c, 4)

        # 5. Community Detection & Partitioning
        partition, comm_names = self.community_detector.detect_communities(G)
        self.community_names = comm_names
        for name, comm_id in partition.items():
            if name in self.nodes:
                self.nodes[name]["community_id"] = comm_id
                self.nodes[name]["community_name"] = comm_names.get(comm_id, f"Cluster {comm_id}")

        # 6. Directional Transfer Entropy & Causal Cascades
        self.active_cascades = self.causal_engine.trace_cascades(
            entity_series=self.entity_occurrences,
            edge_weights=self.edge_weights,
            max_depth=4,
            min_flow_threshold=0.10
        )

    def get_graph_export(self) -> Dict[str, Any]:
        """
        Exports the entire manifold in D3-compliant JSON structure.
        """
        export_nodes = []
        for name, node in self.nodes.items():
            # Composite visual radius: base (4) + centrality * 20 + log(lambda + 1) * 3
            centrality = node.get("centrality", 0.0)
            h_lambda = node.get("hawkes_lambda", 0.0)
            radius = round(4.0 + (centrality * 24.0) + (math.log1p(h_lambda) * 4.0), 2)
            export_nodes.append({
                "id": node["id"],
                "label": node["label"],
                "category": node["category"],
                "community_id": node.get("community_id", 0),
                "community_name": node.get("community_name", "Macro Cluster"),
                "centrality": centrality,
                "surprisal": node.get("surprisal", 0.0),
                "hawkes_lambda": round(h_lambda, 3),
                "branching_ratio": round(node.get("branching_ratio", 0.0), 3),
                "is_excited": node.get("hawkes_excited", False),
                "radius": radius,
                "last_updated": node["last_updated"]
            })

        # Mark edges participating in active cascades
        cascade_edges = set()
        for path in self.active_cascades:
            for k in range(len(path) - 1):
                cascade_edges.add((path[k], path[k+1]))

        export_links = []
        for (u, v), w in self.edge_weights.items():
            if u in self.nodes and v in self.nodes and w >= 0.15:
                is_cascade = (u, v) in cascade_edges
                export_links.append({
                    "source": u,
                    "target": v,
                    "weight": round(w, 2),
                    "is_cascade": is_cascade
                })

        return {
            "timestamp": time.time(),
            "nodes_count": len(export_nodes),
            "links_count": len(export_links),
            "communities_count": len(self.community_names),
            "cascades_count": len(self.active_cascades),
            "cascades": self.active_cascades,
            "communities": self.community_names,
            "nodes": export_nodes,
            "links": export_links
        }
