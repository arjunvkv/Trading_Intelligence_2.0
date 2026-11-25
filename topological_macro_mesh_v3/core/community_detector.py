"""
ORGANIC COMMUNITY DETECTION ENGINE
Discovers emergent macro communities using modularity optimization (Louvain/Greedy).
Dynamically names each community based on its top central tokens. Zero hardcoded boxes.
"""

from typing import Dict, List, Tuple, Any, Set, Union
import networkx as nx

class CommunityDetector:
    def __init__(self, resolution: float = 1.0):
        self.resolution = resolution

    def detect_communities(
        self,
        graph_or_nodes: Union[nx.Graph, Dict[str, Dict[str, Any]]],
        edges: Dict[Tuple[str, str], Any] = None
    ) -> Tuple[Dict[str, int], Dict[int, str]]:
        """
        Runs modularity optimization on the active topological graph.
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
            # High-performance Louvain community detection
            detected = nx.community.louvain_communities(G_undir, weight="weight", resolution=self.resolution, seed=42)
        except Exception:
            try:
                detected = nx.community.greedy_modularity_communities(G_undir, weight="weight")
            except Exception:
                detected = [set(c) for c in nx.connected_components(G_undir)]

        node_partition: Dict[str, int] = {}
        community_names: Dict[int, str] = {}

        for c_idx, member_set in enumerate(detected):
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
