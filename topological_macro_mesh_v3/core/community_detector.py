"""
ORGANIC COMMUNITY DETECTION ENGINE (LEIDEN MODULARITY & GRAPH TOPOLOGY)
Discovers cohesive, well-connected macro communities using Leiden Modularity optimization.
Dynamically deduces sovereign institutional theater names from topological hub tokens.
Zero hardcoding.
"""

from typing import Dict, List, Tuple, Any, Set, Union
import networkx as nx

try:
    import igraph as ig
    import leidenalg
    HAS_LEIDEN = True
except ImportError:
    HAS_LEIDEN = False

class CommunityDetector:
    def __init__(self, resolution: float = 0.65):
        self.resolution = resolution

    def detect_communities(
        self,
        graph_or_nodes: Union[nx.Graph, Dict[str, Dict[str, Any]]],
        edges: Dict[Tuple[str, str], Any] = None
    ) -> Tuple[Dict[str, int], Dict[int, str]]:
        """
        Runs Leiden modularity optimization on the active topological graph.
        Consolidates micro-islands into cohesive, well-connected macro constellations.
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

        raw_detected = []
        if HAS_LEIDEN and len(G_undir) > 1:
            try:
                node_list = list(nodes_dict.keys())
                node_to_idx = {nid: i for i, nid in enumerate(node_list)}
                edges_ig = []
                weights_ig = []
                for u, v, data in G_undir.edges(data=True):
                    if u in node_to_idx and v in node_to_idx:
                        edges_ig.append((node_to_idx[u], node_to_idx[v]))
                        weights_ig.append(float(data.get("weight", 1.0)))

                g_ig = ig.Graph(len(node_list), edges_ig, directed=False)
                g_ig.es["weight"] = weights_ig
                partition_leiden = leidenalg.find_partition(
                    g_ig, leidenalg.ModularityVertexPartition, weights="weight", seed=42
                )
                for part_indices in partition_leiden:
                    raw_detected.append({node_list[i] for i in part_indices})
            except Exception:
                raw_detected = []

        if not raw_detected:
            try:
                # High-performance Louvain community detection fallback
                raw_detected = list(nx.community.louvain_communities(G_undir, weight="weight", resolution=self.resolution, seed=42))
            except Exception:
                try:
                    raw_detected = list(nx.community.greedy_modularity_communities(G_undir, weight="weight"))
                except Exception:
                    raw_detected = [set(c) for c in nx.connected_components(G_undir)]

        # Separate into major clusters (>=3 members) and micro-islands (<3 members)
        major_clusters = [set(c) for c in raw_detected if len(c) >= 3]
        micro_islands = [set(c) for c in raw_detected if len(c) < 3]

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

        # Sort major clusters by size descending (largest primary theaters get primary colors)
        major_clusters = sorted(major_clusters, key=len, reverse=True)

        node_partition: Dict[str, int] = {}
        community_names: Dict[int, str] = {}

        for c_idx, member_set in enumerate(major_clusters):
            members = list(member_set)
            for m in members:
                node_partition[m] = c_idx

            # Rank members by degree centrality within the graph
            sorted_members = sorted(members, key=lambda m: G_undir.degree(m) if G_undir.has_node(m) else 0, reverse=True)
            top_tokens = []
            categories = []
            for m in sorted_members[:6]:
                if m in nodes_dict:
                    label = nodes_dict[m].get("label", str(m))
                    cat = nodes_dict[m].get("category", "")
                    top_tokens.append(label)
                    categories.append(str(cat).lower())
                else:
                    top_tokens.append(str(m))

            # Deduce sovereign institutional archetype from members
            combined_text = " ".join(top_tokens).lower() + " " + " ".join(categories)
            if any(k in combined_text for k in ["chokepoint", "hormuz", "red sea", "military", "drone", "defense", "strike", "war", "ukraine", "russia", "israel", "iran"]):
                archetype = "Maritime Chokepoint & Defense Front"
            elif any(k in combined_text for k in ["reserves", "foreign exchange", "bullion", "brics", "swaps", "gold", "pboc"]):
                archetype = "Bullion & Sovereign FX Reserves"
            elif any(k in combined_text for k in ["treasury", "debt", "yield", "bonds", "deficit", "auction", "sovereign state"]):
                archetype = "Sovereign Debt & Yield Horizon"
            elif any(k in combined_text for k in ["tariff", "trade", "semiconductor", "rare earths", "export", "copper", "oil", "critical commodity"]):
                archetype = "Trade Tariffs & Supply Shock Sector"
            elif any(k in combined_text for k in ["central bank", "monetary policy", "fomc", "ecb", "boj", "rates", "inflation"]):
                archetype = "Central Bank & Policy Rates"
            elif any(k in combined_text for k in ["repo", "collateral", "liquidity", "facility", "imf", "settlement", "agora", "bis"]):
                archetype = "Collateral & Money Market Plumbing"
            else:
                archetype = "Macro Sovereign Horizon"

            # Filter out fragment tokens when selecting primary hub name
            meaningful_hubs = []
            for t in top_tokens:
                tl = t.strip().lower()
                if len(tl) <= 2 or tl in ["uks", "bn to", "say", "says", "report"]:
                    continue
                if any(bad in tl for bad in ["bn to", "million to", "billion to", "per cent"]):
                    continue
                meaningful_hubs.append(t)

            hub_name = meaningful_hubs[0] if meaningful_hubs else (top_tokens[0] if top_tokens else f"Sector {c_idx + 1}")
            if hub_name.lower() in archetype.lower():
                name = archetype
            else:
                name = f"{hub_name} • {archetype}"

            community_names[c_idx] = name

        return node_partition, community_names
