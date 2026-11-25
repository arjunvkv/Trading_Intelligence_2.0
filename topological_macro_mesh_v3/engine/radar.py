"""
SOVEREIGN RADAR ENGINE
Precursor Clue Tracking & Maturation Staging Engine.
Stages emerging macro anomalies across three lifecycle phases:
[WHISPER] -> [FORMING] -> [BREAKOUT] with strict 30-minute invalidation off-ramps.
"""

import time
from typing import Dict, List, Any, Optional

class SovereignRadar:
    def __init__(self, invalidation_window_sec: float = 1800.0):
        # 1800 sec = 30 minutes invalidation off-ramp
        self.invalidation_window_sec = invalidation_window_sec
        self.active_clues: Dict[str, Dict[str, Any]] = {}

    def scan_manifold(
        self,
        nodes: Dict[str, Dict[str, Any]],
        cascades: List[List[str]],
        crowd_divergences: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluates active manifold nodes and precursor crowd signals to stage clues.
        """
        now = time.time()
        
        # 1. Ingest Crowd Divergences as initial WHISPERS
        for div in crowd_divergences:
            title = div.get("title", "")
            topic = div.get("publisher", "Crowd Attention")
            cid = f"crowd_{div.get('published', '')}_{title[:30]}"
            if cid not in self.active_clues:
                self.active_clues[cid] = {
                    "id": cid,
                    "title": title,
                    "stage": "WHISPER",
                    "origin_source": "CROWD_DIVERGENCE",
                    "surprisal": 3.5,
                    "branching_ratio": 0.3,
                    "first_seen": now,
                    "last_active": now,
                    "description": div.get("summary", ""),
                    "participating_nodes": [title]
                }
            else:
                self.active_clues[cid]["last_active"] = now

        # 2. Ingest Manifold Nodes with high surprisal or Hawkes excitation
        for name, node in nodes.items():
            surprisal = node.get("surprisal", 0.0)
            branching_ratio = node.get("branching_ratio", 0.0)
            is_excited = node.get("hawkes_excited", False)
            centrality = node.get("centrality", 0.0)
            category = node.get("category", "DEFAULT")

            # High surprisal whisper condition: peripheral entity with high Shannon surprisal
            if surprisal >= 2.5 and centrality < 0.15:
                cid = f"node_{name}"
                if cid not in self.active_clues:
                    self.active_clues[cid] = {
                        "id": cid,
                        "title": f"Sovereign Whisper: Anomalous activity in {name}",
                        "stage": "WHISPER",
                        "origin_source": category,
                        "surprisal": round(surprisal, 2),
                        "branching_ratio": round(branching_ratio, 2),
                        "first_seen": now,
                        "last_active": now,
                        "description": f"Peripheral node '{name}' exhibited high Shannon surprisal ({surprisal:.2f} bits) with nascent clustering.",
                        "participating_nodes": [name]
                    }
                else:
                    clue = self.active_clues[cid]
                    clue["last_active"] = now
                    clue["surprisal"] = round(surprisal, 2)
                    clue["branching_ratio"] = round(branching_ratio, 2)

            # Stage Promotion: FORMING (Hawkes self-excitation or branching ratio >= 0.5)
            cid = f"node_{name}"
            if cid in self.active_clues:
                clue = self.active_clues[cid]
                if clue["stage"] == "WHISPER" and (branching_ratio >= 0.45 or is_excited):
                    clue["stage"] = "FORMING"
                    clue["title"] = f"Forming Macro Vector: Self-exciting pulse in {name}"
                    clue["description"] = f"Entity '{name}' transitioned from whisper to forming. Hawkes branching ratio accelerated to {branching_ratio:.2f}."

        # 3. Stage Promotion: BREAKOUT (Entities active in multi-hop Transfer Entropy cascades)
        for path in cascades:
            if len(path) >= 2:
                primary = path[0]
                cid = f"node_{primary}"
                if cid in self.active_clues:
                    clue = self.active_clues[cid]
                    clue["stage"] = "BREAKOUT"
                    clue["last_active"] = now
                    clue["title"] = f"Breakout Transmission Cascade: {path[0]} -> {path[-1]}"
                    clue["description"] = f"Active multi-hop Transfer Entropy causal cascade propagating: {' -> '.join(path[:4])}."
                    clue["participating_nodes"] = path

        # 4. Clean Invalidation Off-Ramp: 30-minute stale clue pruning
        stale_cids = []
        for cid, clue in self.active_clues.items():
            inactive_duration = now - clue["last_active"]
            if inactive_duration > self.invalidation_window_sec:
                stale_cids.append(cid)

        for cid in stale_cids:
            self.active_clues.pop(cid, None)

        # Return sorted active clues by stage severity (BREAKOUT > FORMING > WHISPER)
        stage_rank = {"BREAKOUT": 3, "FORMING": 2, "WHISPER": 1}
        sorted_clues = sorted(
            self.active_clues.values(),
            key=lambda c: (stage_rank.get(c["stage"], 0), c["surprisal"]),
            reverse=True
        )
        return sorted_clues

    def get_summary_telemetry(self) -> Dict[str, Any]:
        """Provides quick aggregated clue metrics."""
        counts = {"WHISPER": 0, "FORMING": 0, "BREAKOUT": 0}
        for clue in self.active_clues.values():
            s = clue.get("stage", "WHISPER")
            if s in counts:
                counts[s] += 1
        return {
            "total_active_clues": len(self.active_clues),
            "clues_by_stage": counts
        }
