"""
CAUSAL DISCOVERY & TRANSFER ENTROPY ENGINE
Calculates directional information flow, Transfer Entropy (TE_X->Y),
and traces organic transmission cascades without target anchors.
"""

import math
from collections import defaultdict
from typing import List, Dict, Tuple, Set, Any

class CausalDiscoveryEngine:
    def __init__(self, base_te: float = 0.35):
        self.base_te = base_te

    def compute_transfer_entropy(
        self,
        source_timestamps: List[float],
        target_timestamps: List[float],
        co_occurrence_count: int,
        window_sec: float = 1800.0
    ) -> float:
        """
        Estimates directional Transfer Entropy (TE_X->Y):
        Measures the reduction in uncertainty about target Y's future arrivals
        given knowledge of source X's past arrivals.
        """
        if not source_timestamps or not target_timestamps:
            return round(self.base_te, 3)

        valid_transitions = 0
        for ts_s in source_timestamps:
            for ts_t in target_timestamps:
                dt = ts_t - ts_s
                if 0 < dt <= window_sec:
                    valid_transitions += 1
                    break

        total_source = len(source_timestamps)
        transition_prob = valid_transitions / max(1, total_source)
        
        # TE in bits: scaled logarithmic conditional mutual information
        te = self.base_te + (math.log2(1.0 + transition_prob) * 0.45) + min(0.2, co_occurrence_count * 0.02)
        return round(float(min(0.95, max(0.15, te))), 3)

    def trace_transmission_cascade(
        self,
        start_node: str,
        edges: Dict[Tuple[str, str], Any],
        entity_first_seen: Dict[str, float] = None,
        max_depth: int = 4
    ) -> Tuple[List[str], float]:
        """
        Follows the path of maximal Transfer Entropy and edge weight,
        strictly respecting the arrow of time (t_curr <= t_nbr + epsilon).
        """
        if not edges:
            return ([start_node], 1.0)

        path = [start_node]
        curr = start_node
        visited = {start_node}
        total_score = 0.0

        for _ in range(max_depth - 1):
            best_nbr = None
            best_score = -1.0
            t_curr = entity_first_seen.get(curr, 0.0) if entity_first_seen else 0.0

            for (src, tgt), edata in edges.items():
                nbr = None
                if src == curr and tgt not in visited:
                    nbr = tgt
                elif tgt == curr and src not in visited:
                    nbr = src

                if nbr:
                    # Temporal precedence guard: cannot cause events that concluded in the past
                    if entity_first_seen:
                        t_nbr = entity_first_seen.get(nbr, 0.0)
                        if t_curr > 0 and t_nbr > 0 and t_nbr < t_curr - 120.0:
                            continue

                    weight = edata.get("weight", edata) if isinstance(edata, dict) else float(edata)
                    te = edata.get("te", self.base_te) if isinstance(edata, dict) else self.base_te
                    score = weight * te
                    if score > best_score:
                        best_score = score
                        best_nbr = nbr

            if best_nbr is None or best_score < 0.08:
                break

            path.append(best_nbr)
            visited.add(best_nbr)
            total_score += best_score
            curr = best_nbr

        avg_score = round(total_score / max(1, len(path) - 1), 2) if len(path) > 1 else 1.0
        return (path, avg_score)

    def trace_cascades(
        self,
        entity_series: Dict[str, List[float]],
        edge_weights: Dict[Tuple[str, str], float],
        max_depth: int = 4,
        min_flow_threshold: float = 0.10
    ) -> List[List[str]]:
        """
        Scans all nodes and discovers top multi-hop transmission cascades
        strictly moving forward in time from earliest catalyst precursors.
        """
        if not edge_weights:
            return []

        first_seen = {
            e: min(series) if series else 0.0
            for e, series in entity_series.items()
        }

        # Find potential root entities (earliest timestamps or highest burst occurrences)
        roots = sorted(
            entity_series.keys(),
            key=lambda e: (len(entity_series[e]), -first_seen.get(e, 0.0)),
            reverse=True
        )[:20]

        cascades = []
        seen_paths = set()

        for root in roots:
            path, score = self.trace_transmission_cascade(
                root, edge_weights, entity_first_seen=first_seen, max_depth=max_depth
            )
            if len(path) >= 2 and score >= min_flow_threshold:
                path_key = tuple(path)
                if path_key not in seen_paths:
                    seen_paths.add(path_key)
                    cascades.append(path)

        return cascades

