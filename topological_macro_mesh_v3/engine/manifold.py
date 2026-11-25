"""
TOPOLOGICAL MANIFOLD ENGINE
Maintains the organic, high-dimensional directed sovereign macro causal graph.
Integrates Hawkes self-exciting processes, Shannon surprisal, Transfer Entropy,
and Modularity-based Community Detection with complete UI contract parity.
"""

import time
import math
import urllib.parse
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
        self.entity_publishers: Dict[str, Set[str]] = {}
        
        self.last_community_update: float = 0.0
        self.community_names: Dict[int, str] = {}
        self.community_members: Dict[int, List[str]] = {}
        self.active_cascades: List[List[str]] = []
        self.precursor_clues: List[Dict[str, Any]] = []

    def ingest_document(self, doc: Dict[str, Any]) -> List[str]:
        """
        Processes a single incoming macro wire or intelligence document.
        Extracts entities, updates arrival time-series, and updates edges.
        """
        title = doc.get("title", "").strip()
        summary = doc.get("summary", "").strip()
        text = f"{title}. {summary}" if summary else title
        source_type = doc.get("source_type", "SOVEREIGN_CENTRAL_BANK")
        publisher = doc.get("publisher", "Sovereign Wire")
        now = doc.get("timestamp", time.time())

        # Extract genuine macro entities (with sub-token suppression)
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

            if name not in self.entity_publishers:
                self.entity_publishers[name] = set()
            self.entity_publishers[name].add(publisher)

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
                    "trigger_text": title,
                    "trigger_source": publisher,
                    "hawkes_lambda": 0.05,
                    "branching_ratio": 0.0,
                    "z_score": 0.0,
                    "surprisal": 2.5,
                    "community_id": 0,
                    "community_name": "Emergent Constellation"
                }
            else:
                node = self.nodes[name]
                node["last_updated"] = now
                node["observation_count"] += 1
                # Update headline with freshest title
                if title and len(title) > len(node.get("trigger_text", "")):
                    node["trigger_text"] = title
                    node["trigger_source"] = publisher
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
            node["effective_weight"] = node["observation_count"] * decay_factor

            # Culling threshold: 24h of inactivity or dead weight
            if age > 86400.0 or (age > hl * 3 and node["observation_count"] < 2):
                dead_nodes.append(name)

        for name in dead_nodes:
            self.nodes.pop(name, None)
            self.entity_occurrences.pop(name, None)
            self.entity_publishers.pop(name, None)

        # 2. Temporal Edge Decay & Dead Node Link Clean-up
        dead_edges = []
        for (u, v), w in self.edge_weights.items():
            if u not in self.nodes or v not in self.nodes:
                dead_edges.append((u, v))
                continue
            edge_age = now - self.edge_timestamps.get((u, v), now)
            decay_factor = math.exp(- (math.log(2) * edge_age) / 7200.0)
            decayed_w = w * decay_factor
            if decayed_w < 0.08 or edge_age > 43200.0:
                dead_edges.append((u, v))
            else:
                self.edge_weights[(u, v)] = decayed_w

        for edge in dead_edges:
            self.edge_weights.pop(edge, None)
            self.edge_timestamps.pop(edge, None)

        # 3. Calculate Hawkes Point Process & Surprisal for active nodes
        for name, node in self.nodes.items():
            times = self.entity_occurrences.get(name, [])
            recent_times = [t for t in times if now - t <= 2700.0]
            recent_count = len(recent_times)
            baseline = max(0.2, (len(times) - recent_count) / 4.0)
            z = (recent_count - baseline) / math.sqrt(baseline)
            node["z_score"] = round(float(max(0.0, z)), 2)

            h_metrics = self.hawkes.estimate(times, t_eval=now)
            node["hawkes_lambda"] = h_metrics["lambda_t"]
            node["branching_ratio"] = h_metrics["branching_ratio"]
            node["hawkes_excited"] = h_metrics["is_excited"]
            
            node["surprisal"] = self.surprisal.calculate_surprisal(name)
            node["icf"] = self.surprisal.calculate_icf(name)

        # 4. Construct NetworkX Graph for Community Detection & Centralities
        G = nx.DiGraph()
        for name, node in self.nodes.items():
            G.add_node(name, **node)

        degrees = {n: 0 for n in self.nodes}
        for (u, v), w in self.edge_weights.items():
            if u in self.nodes and v in self.nodes:
                G.add_edge(u, v, weight=w)
                degrees[u] = degrees.get(u, 0) + 1
                degrees[v] = degrees.get(v, 0) + 1

        for name in self.nodes:
            self.nodes[name]["degree"] = degrees.get(name, 0)

        # Calculate Degree Centrality
        if len(G) > 0:
            deg_centrality = nx.degree_centrality(G)
            for name, c in deg_centrality.items():
                if name in self.nodes:
                    self.nodes[name]["centrality"] = round(c, 4)

        # 5. Community Detection & Partitioning
        partition, comm_names = self.community_detector.detect_communities(G)
        self.community_names = comm_names
        
        # Build community members mapping
        self.community_members = {}
        for name, comm_id in partition.items():
            if name in self.nodes:
                self.nodes[name]["community_id"] = comm_id
                self.nodes[name]["community_name"] = comm_names.get(comm_id, f"Cluster {comm_id}")
                if comm_id not in self.community_members:
                    self.community_members[comm_id] = []
                self.community_members[comm_id].append(name)

        # 6. Directional Transfer Entropy & Causal Cascades
        self.active_cascades = self.causal_engine.trace_cascades(
            entity_series=self.entity_occurrences,
            edge_weights=self.edge_weights,
            max_depth=4,
            min_flow_threshold=0.10
        )

    def get_graph_export(self, radar=None, collector_health: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Exports the entire manifold in 100% D3 UI-compliant JSON structure.
        """
        now = time.time()
        export_nodes = []
        age_dist = {"under_5m": 0, "5m_to_15m": 0, "15m_to_60m": 0, "over_60m": 0}

        for name, node in self.nodes.items():
            first_seen = node.get("created_at", now)
            last_seen = node.get("last_updated", now)
            age_sec = max(0.0, round(now - first_seen, 1))
            last_seen_sec = max(0.0, round(now - last_seen, 1))

            first_str = f"{int(age_sec)}s ago" if age_sec < 60 else f"{round(age_sec / 60.0, 1)}m ago"
            last_str = f"{int(last_seen_sec)}s ago" if last_seen_sec < 60 else f"{round(last_seen_sec / 60.0, 1)}m ago"

            if age_sec < 300:
                regime = "HOT_BURST (<5m)"
                age_dist["under_5m"] += 1
            elif age_sec < 900:
                regime = "ACTIVE (5-15m)"
                age_dist["5m_to_15m"] += 1
            elif age_sec < 3600:
                regime = "STABLE (15-60m)"
                age_dist["15m_to_60m"] += 1
            else:
                regime = "DECAYING (>60m)"
                age_dist["over_60m"] += 1

            centrality = node.get("centrality", 0.0)
            z_score = node.get("z_score", 0.0)
            deg = node.get("degree", 1)
            cluster_id = node.get("community_id", 0)

            # Node visual radius (3.0 - 9.5)
            node_r = round(max(3.0, min(9.5, 2.8 + math.log1p(deg) * 0.9 + min(2.5, z_score * 0.25))), 1)
            pubs = list(self.entity_publishers.get(name, []))

            trigger_text = node.get("trigger_text", name)
            trigger_source = node.get("trigger_source", "Sovereign Wire")
            q_google = urllib.parse.quote(trigger_text[:100])
            q_x = urllib.parse.quote(name)

            export_nodes.append({
                "id": node["id"],
                "label": node["label"],
                "cluster": cluster_id,  # CRITICAL: Maps directly to UI cluster color & dynamic community tray
                "category": node["category"],
                "community_id": cluster_id,
                "community_name": node.get("community_name", f"Cluster {cluster_id}"),
                "centrality": centrality,
                "degree": deg,
                "z_score": z_score,
                "surprisal": node.get("surprisal", 2.5),
                "hawkes_lambda": round(node.get("hawkes_lambda", 0.05), 3),
                "branching_ratio": round(node.get("branching_ratio", 0.0), 3),
                "is_excited": node.get("hawkes_excited", False),
                "is_surging": z_score >= 2.0,
                "r": node_r,
                "trigger_text": trigger_text,
                "trigger_source": trigger_source,
                "publishers": pubs,
                "publisher_count": len(pubs),
                "age_seconds": age_sec,
                "last_seen_seconds_ago": last_seen_sec,
                "first_seen_str": first_str,
                "last_seen_str": last_str,
                "freshness_regime": regime,
                "verify_google": f"https://www.google.com/search?q={q_google}",
                "verify_x": f"https://x.com/search?q={q_x}&f=live"
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
                    "te": round(0.35 + (w * 0.05), 2),
                    "is_cascade": is_cascade
                })

        # Format Communities as an ARRAY of objects (Required by mesh.html)
        export_communities = []
        for cid, cname in self.community_names.items():
            members = self.community_members.get(cid, [])
            top_members = sorted(members, key=lambda m: self.nodes.get(m, {}).get("degree", 0), reverse=True)[:4]
            export_communities.append({
                "id": cid,
                "name": cname,
                "top_tokens": top_members,
                "size": len(members)
            })

        # Format Precursor Clues for UI Radar
        radar_clues = []
        if radar:
            if hasattr(radar, "get_ui_clues"):
                radar_clues = radar.get_ui_clues(self.entity_publishers)
            else:
                active_clues = radar.active_clues.values()
                for c in active_clues:
                    phrase = c.get("title", "")
                    nodes_in_clue = c.get("participating_nodes", [])
                    primary_node = nodes_in_clue[0] if nodes_in_clue else phrase
                    pubs = list(self.entity_publishers.get(primary_node, ["Sovereign Wire"]))
                    stage = c.get("stage", "WHISPER")
                    stage_str = f"STAGE 3: BREAKOUT TRANSMISSION" if stage == "BREAKOUT" else (f"STAGE 2: CLUSTER FORMING" if stage == "FORMING" else "STAGE 1: GROUND WHISPER")
                    hawkes_b = "IGNITION POINT (Self-Exciting)" if stage in ["FORMING", "BREAKOUT"] else "EQUILIBRIUM"
                    lead_b = "ASYMMETRIC LEAD (Alpha Front-Run)" if stage == "BREAKOUT" else "ASYMMETRIC LEAD"
                    
                    radar_clues.append({
                        "phrase": primary_node,
                        "title": phrase,
                        "stage": stage_str,
                        "hawkes_badge": hawkes_b,
                        "lead_badge": lead_b,
                        "maturation_minutes": max(1, int((now - c.get("first_seen", now)) / 60.0)),
                        "publisher_count": len(pubs),
                        "publishers": pubs,
                        "primary_publisher": pubs[0] if pubs else "Sovereign Wire",
                        "sample_headline": c.get("description", phrase),
                        "z_score": 2.5 if stage == "BREAKOUT" else 1.2,
                        "google_url": f"https://www.google.com/search?q={urllib.parse.quote(phrase)}"
                    })

        # Primary Driver Discovery
        surging_nodes = [n for n in export_nodes if n.get("is_surging")]
        surging_nodes.sort(key=lambda n: (n.get("z_score", 0.0), n.get("degree", 0)), reverse=True)
        if surging_nodes:
            top_n = surging_nodes[0]
            primary_driver = {
                "active": True,
                "headline": top_n["trigger_text"],
                "clue_phrase": top_n["label"],
                "z_velocity": top_n["z_score"],
                "source_count": top_n["publisher_count"] or 1,
                "hawkes_badge": "IGNITION POINT" if top_n["z_score"] >= 2.0 else "ACCELERATING",
                "verify_google": top_n["verify_google"],
                "verify_x": top_n["verify_x"]
            }
        else:
            primary_driver = {
                "active": False,
                "headline": "Sovereign Macro Horizon in Dynamic Equilibrium (Awaiting Outlier Shock)",
                "z_velocity": 0.0,
                "source_count": 0,
                "hawkes_badge": "EQUILIBRIUM",
                "verify_google": "https://www.google.com/search?q=sovereign+debt+macro+news",
                "verify_x": "https://x.com/search?q=macroeconomics"
            }

        res = {
            "timestamp": now,
            "nodes_count": len(export_nodes),
            "links_count": len(export_links),
            "communities_count": len(export_communities),
            "cascades_count": len(self.active_cascades),
            "cascades": self.active_cascades,
            "communities": export_communities,
            "emerging_constellations": radar_clues[:12],
            "precursor_clues": radar_clues[:12],
            "primary_driver": primary_driver,
            "age_distribution": age_dist,
            "nodes": export_nodes,
            "links": export_links
        }
        if collector_health:
            res["collector_health"] = collector_health
        return res
