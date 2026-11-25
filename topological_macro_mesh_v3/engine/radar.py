"""
SOVEREIGN RADAR ENGINE
Precursor Clue Tracking & Maturation Staging Engine.
Stages emerging macro anomalies across three lifecycle phases:
[WHISPER] -> [FORMING] -> [BREAKOUT] with strict 30-minute invalidation off-ramps.
"""

import time
import urllib.parse
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
                    "participating_nodes": [title],
                    "publishers": ["Crowd Attention Telemetry"]
                }
            else:
                self.active_clues[cid]["last_active"] = now

        # 2. Ingest Manifold Nodes with notable surprisal or Hawkes excitation
        for name, node in nodes.items():
            surprisal = node.get("surprisal", 0.0)
            branching_ratio = node.get("branching_ratio", 0.0)
            is_excited = node.get("hawkes_excited", False)
            category = node.get("category", "DEFAULT")
            trigger_text = node.get("trigger_text", name)
            trigger_source = node.get("trigger_source", "Sovereign Wire")

            # High surprisal whisper condition (Shannon surprisal >= 1.5)
            if surprisal >= 1.5:
                cid = f"node_{name}"
                if cid not in self.active_clues:
                    self.active_clues[cid] = {
                        "id": cid,
                        "title": f"Precursor Signal: {name}",
                        "stage": "WHISPER",
                        "origin_source": category,
                        "surprisal": round(surprisal, 2),
                        "branching_ratio": round(branching_ratio, 2),
                        "first_seen": now,
                        "last_active": now,
                        "description": trigger_text,
                        "participating_nodes": [name],
                        "publishers": [trigger_source]
                    }
                else:
                    clue = self.active_clues[cid]
                    clue["last_active"] = now
                    clue["surprisal"] = round(surprisal, 2)
                    clue["branching_ratio"] = round(branching_ratio, 2)

            # Stage Promotion: FORMING (Hawkes self-excitation or branching ratio >= 0.3)
            cid = f"node_{name}"
            if cid in self.active_clues:
                clue = self.active_clues[cid]
                if clue["stage"] == "WHISPER" and (branching_ratio >= 0.30 or is_excited):
                    clue["stage"] = "FORMING"
                    clue["title"] = f"Forming Macro Pulse: {name}"
                    clue["description"] = f"Entity '{name}' accelerated. Hawkes branching ratio: {branching_ratio:.2f}."

        # 3. Stage Promotion: BREAKOUT (Entities active in multi-hop Transfer Entropy cascades)
        for path in cascades:
            if len(path) >= 2:
                primary = path[0]
                cid = f"cascade_{primary}"
                self.active_clues[cid] = {
                    "id": cid,
                    "title": f"Breakout Cascade: {' -> '.join(path[:3])}",
                    "stage": "BREAKOUT",
                    "origin_source": "CAUSAL_CASCADE",
                    "surprisal": 3.8,
                    "branching_ratio": 0.85,
                    "first_seen": self.active_clues.get(cid, {}).get("first_seen", now),
                    "last_active": now,
                    "description": f"Active multi-hop Transfer Entropy cascade: {' -> '.join(path)}",
                    "participating_nodes": path,
                    "publishers": ["Institutional Transmission Grid"]
                }

        # 4. Clean Invalidation Off-Ramp: 30-minute stale clue pruning
        stale_cids = []
        for cid, clue in self.active_clues.items():
            inactive_duration = now - clue["last_active"]
            if inactive_duration > self.invalidation_window_sec:
                stale_cids.append(cid)

        for cid in stale_cids:
            self.active_clues.pop(cid, None)

        stage_rank = {"BREAKOUT": 3, "FORMING": 2, "WHISPER": 1}
        sorted_clues = sorted(
            self.active_clues.values(),
            key=lambda c: (stage_rank.get(c["stage"], 0), c["surprisal"]),
            reverse=True
        )
        return sorted_clues

    def get_ui_clues(self, manifold_publishers: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Formats active clues for the UI radar tray."""
        now = time.time()
        stage_rank = {"BREAKOUT": 3, "FORMING": 2, "WHISPER": 1}
        sorted_clues = sorted(
            self.active_clues.values(),
            key=lambda c: (stage_rank.get(c["stage"], 0), c["surprisal"]),
            reverse=True
        )

        ui_clues = []
        for c in sorted_clues[:12]:
            phrase = c.get("title", "")
            nodes = c.get("participating_nodes", [])
            primary = nodes[0] if nodes else phrase
            
            stage = c.get("stage", "WHISPER")
            stage_str = f"STAGE 3: BREAKOUT TRANSMISSION" if stage == "BREAKOUT" else (f"STAGE 2: CLUSTER FORMING" if stage == "FORMING" else "STAGE 1: GROUND WHISPER")
            hawkes_badge = "IGNITION POINT (Self-Exciting)" if stage in ["FORMING", "BREAKOUT"] else "EQUILIBRIUM"
            lead_badge = "ASYMMETRIC LEAD (Alpha Front-Run)" if stage == "BREAKOUT" else "ASYMMETRIC LEAD"
            
            pubs = c.get("publishers", ["Sovereign Wire"])
            if manifold_publishers and primary in manifold_publishers:
                extra = list(manifold_publishers[primary])
                if extra:
                    pubs = extra

            mat_min = max(1, int((now - c.get("first_seen", now)) / 60.0))

            ui_clues.append({
                "phrase": primary,
                "title": phrase,
                "stage": stage_str,
                "hawkes_badge": hawkes_badge,
                "lead_badge": lead_badge,
                "maturation_minutes": mat_min,
                "publisher_count": len(pubs),
                "publishers": pubs,
                "primary_publisher": pubs[0] if pubs else "Sovereign Wire",
                "sample_headline": c.get("description", phrase),
                "z_score": 2.8 if stage == "BREAKOUT" else (1.8 if stage == "FORMING" else 1.2),
                "google_url": f"https://www.google.com/search?q={urllib.parse.quote(phrase)}"
            })

        return ui_clues

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
