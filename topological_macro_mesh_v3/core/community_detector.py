"""
ORGANIC COMMUNITY DETECTION ENGINE
Discovers emergent macro communities using modularity optimization (Louvain/Greedy).
Dynamically names each community based on its top central tokens. Zero hardcoded boxes.
"""

from typing import Dict, List, Tuple, Any, Set, Union
import networkx as nx

class CommunityDetector:
    def __init__(self, resolution: float = 0.55):
        self.resolution = resolution

    def detect_communities(
        self,
        graph_or_nodes: Union[nx.Graph, Dict[str, Dict[str, Any]]],
        edges: Dict[Tuple[str, str], Any] = None
    ) -> Tuple[Dict[str, int], Dict[int, str]]:
        """
        Runs modularity optimization on the active topological graph.
        Consolidates micro-islands (|C| < 3) into strongest adjacent macro constellations.
        Returns:
            node_partition: {node_id: community_id}
            community_names: {community_id: community_name}
        """
        if isinstance(graph_or_nodes, (nx.Graph, nx.DiGraph)):
            G_undir = graph_or_nodes.to_undirected()
            nodes_dict = {n: graph_or_nodes.nodes[n] for n in graph_or_nodes.nodes}
        else:
            nodes_dict = graph_or_nodes
            G_undir = nx.Graph()
            for nid in nodes_dict.keys():
                G_undir.add_node(nid)
            if edges:
                for (src, tgt), ed in edges.items():
                    if src in nodes_dict and tgt in nodes_dict:
                        w = ed.get("weight", 0.5) if isinstance(ed, dict) else float(ed)
                        G_undir.add_edge(src, tgt, weight=w)

        if not nodes_dict or len(G_undir) == 0:
            return {}, {}

        # Disconnected components / empty graph fallback
        if G_undir.number_of_edges() == 0:
            node_partition = {nid: 0 for nid in nodes_dict.keys()}
            community_names = {0: "Emergent Macro Horizon"}
            return node_partition, community_names

        try:
            # High-performance Louvain community detection with macro resolution (0.55)
            raw_detected = list(nx.community.louvain_communities(G_undir, weight="weight", resolution=self.resolution, seed=42))
        except Exception:
            try:
                raw_detected = list(nx.community.greedy_modularity_communities(G_undir, weight="weight"))
            except Exception:
                raw_detected = [set(c) for c in nx.connected_components(G_undir)]

        # Separate into major clusters (>=3 members) and micro-islands (<3 members)
        major_clusters = [set(c) for c in raw_detected if len(c) >= 3]
        micro_islands = [set(c) for c in raw_detected if len(c) < 3]

        # If no major clusters exist, all are kept as is
        if not major_clusters:
            major_clusters = micro_islands
            micro_islands = []

        # Merge micro-islands into their strongest connected major cluster
        unconnected_islands = []
        for island in micro_islands:
            best_cluster_idx = -1
            best_weight = 0.0

            for m in island:
                if not G_undir.has_node(m):
                    continue
                for nbr in G_undir.neighbors(m):
                    edge_w = G_undir[m][nbr].get("weight", 1.0)
                    for c_idx, c_members in enumerate(major_clusters):
                        if nbr in c_members:
                            if edge_w > best_weight:
                                best_weight = edge_w
                                best_cluster_idx = c_idx

            if best_cluster_idx >= 0 and best_weight > 0:
                major_clusters[best_cluster_idx].update(island)
            else:
                unconnected_islands.append(island)

        # Merge remaining isolated singletons into a peripheral constellation if any
        if unconnected_islands:
            combined_periphery = set()
            for island in unconnected_islands:
                combined_periphery.update(island)
            if combined_periphery:
                major_clusters.append(combined_periphery)

        node_partition: Dict[str, int] = {}
        community_names: Dict[int, str] = {}

        for c_idx, member_set in enumerate(major_clusters):
            members = list(member_set)
            for m in members:
                node_partition[m] = c_idx

            # Rank members by degree centrality within the graph
            sorted_members = sorted(members, key=lambda m: G_undir.degree(m) if G_undir.has_node(m) else 0, reverse=True)
            top_tokens = []
            for m in sorted_members[:4]:
                if m in nodes_dict:
                    label = nodes_dict[m].get("label", str(m))
                    top_tokens.append(label)
                else:
                    top_tokens.append(str(m))

            if len(top_tokens) >= 2:
                name = f"{top_tokens[0]} & {top_tokens[1]} Constellation"
            elif top_tokens:
                name = f"{top_tokens[0]} Frontier"
            else:
                name = f"Macro Sector {c_idx + 1}"

            community_names[c_idx] = name

        return node_partition, community_names

