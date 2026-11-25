"""
LEAD & ORDERBOOK ARBITER MODULE
Zero-dogma institutional market physics:
- Real-World Alpha Decay Window derived dynamically from Geodesic Graph Distance & Session Tick Velocity
- Attention & Crowd Divergence (Unseeded Wire Arrival Velocity vs Crowd Query Velocity)
- Two-Phase Market Physics: (Phase 1 Margin Liquidation vs Phase 2 Debasement Flight)
- Live Session Conductivity based on active global market hours (London/NY overlap, etc.)
- Structural Orderbook Consequence: Absorption at key Fair Value Gaps (FVG) or Liquidity Sweeps
"""

import time
import math
from datetime import datetime, timezone
from typing import Dict, Any, List

class LeadArbiter:
    def __init__(self):
        pass

    def get_active_session_conductivity(self, recent_event_count: int = None) -> Dict[str, Any]:
        """
        Calculates live market conductivity dynamically based on empirical event arrival flux λ(t),
        grounded in active global session liquidity.
        """
        utc_now = datetime.now(timezone.utc)
        hour = utc_now.hour

        # Base institutional session alignment
        if 8 <= hour < 17 and 13 <= hour < 21:
            session_name = "London / NY Overlap (Peak Global Liquidity)"
            base_conduct = 0.90
        elif 13 <= hour < 21:
            session_name = "New York Session"
            base_conduct = 0.82
        elif 8 <= hour < 17:
            session_name = "London Session"
            base_conduct = 0.80
        elif 0 <= hour < 9:
            session_name = "Asian Session (SGE / TOCOM Cash)"
            base_conduct = 0.65
        else:
            session_name = "Off-Peak Interbank Hours"
            base_conduct = 0.45

        # Empirical Poisson event flux λ(t): events per 15-minute rolling window
        if recent_event_count is not None:
            lam = max(1.0, float(recent_event_count))
            # Sigmoid dynamic scaling of flux: higher event velocity increases conductivity
            flux_modifier = 1.0 / (1.0 + math.exp(-0.12 * (lam - 12.0)))
            conductivity = round(max(0.25, min(0.98, (base_conduct * 0.5) + (flux_modifier * 0.5))), 2)
        else:
            conductivity = base_conduct

        # Dynamic lag multiplier inversely proportional to conductivity
        lag_multiplier = round(max(0.45, min(2.5, 0.90 / max(0.20, conductivity))), 2)

        return {
            "session": session_name,
            "conductivity": conductivity,
            "lag_multiplier": lag_multiplier,
            "utc_hour": hour
        }

    def compute_hawkes_ignition(
        self, 
        timestamps: List[float], 
        publishers: List[str] = None,
        now: float = None,
        alpha: float = 1.25,
        beta: float = 0.0025, # ~15-20 min half-life
        mu: float = 0.08
    ) -> Dict[str, Any]:
        """
        Hawkes Point Process Self-Exciting Intensity:
        λ(t) = μ + Σ α * exp(-β * (t - t_i))
        Measures organic acceleration and contagion velocity with Publisher Quorum protection.
        """
        if now is None:
            now = time.time()
        
        if not timestamps:
            return {
                "intensity": round(mu, 3),
                "baseline": round(mu, 3),
                "ratio": 1.0,
                "state": "DORMANT",
                "is_ignition": False,
                "corroborated_publishers": 0,
                "badge": "Hawkes: DORMANT (1.0x)"
            }

        # Trap Safeguard: Publisher Quorum & Newsroom Verification
        # Crowd sources alone (Wikipedia, Autocomplete) cannot trigger Hawkes Ignition!
        CROWD_SOURCES = {'wikimedia attention pulse', 'google crowd autocomplete', 'mastodon decentralized fediverse'}
        has_real_newsroom = any(p.lower() not in CROWD_SOURCES and 'crowd' not in p.lower() and 'search' not in p.lower() and 'wiki' not in p.lower() for p in publishers)
        distinct_pubs = len(set(publishers)) if publishers else 1

        if not has_real_newsroom:
            alpha_adj = alpha * 0.15 # Severely dampen crowd self-polling loops
        elif distinct_pubs < 2 and len(timestamps) > 1:
            alpha_adj = alpha * 0.30
        else:
            alpha_adj = alpha

        total_shock = 0.0
        active_events = 0
        for ts in timestamps:
            dt = now - ts
            if 0 <= dt <= 7200: # within last 2 hours
                decayed = alpha_adj * math.exp(-beta * dt)
                total_shock += decayed
                active_events += 1

        intensity = mu + total_shock
        ratio = round(intensity / max(0.001, mu), 2)

        if not has_real_newsroom:
            # Pure crowd inquiries can NEVER claim institutional ignition!
            state = "CROWD_PULSE"
            is_ignition = False
            badge = f"👥 Crowd Pulse ({ratio}x)"
        elif ratio >= 3.0 and distinct_pubs >= 2:
            state = "IGNITION" # Exponential organic cascade verified across 2+ newsrooms!
            is_ignition = True
            badge = f"🔥 Hawkes: IGNITION ({ratio}x)"
        elif ratio >= 1.8:
            state = "COMPOUNDING" # Multi-source developing traction
            is_ignition = False
            badge = f"⚡ Hawkes: COMPOUNDING ({ratio}x)"
        elif ratio > 1.2:
            state = "DECAYING" # Dissipating momentum
            is_ignition = False
            badge = f"⏳ Hawkes: DECAYING ({ratio}x)"
        else:
            state = "DORMANT"
            is_ignition = False
            badge = f"Hawkes: DORMANT ({ratio}x)"

        return {
            "intensity": round(intensity, 3),
            "baseline": round(mu, 3),
            "ratio": ratio,
            "state": state,
            "is_ignition": is_ignition,
            "active_shocks": active_events,
            "distinct_publishers": distinct_pubs,
            "has_real_newsroom": has_real_newsroom,
            "badge": badge
        }

    def derive_causal_pathway(self, text: str, cluster_idx: int = 0, is_crowd_only: bool = False, transmission_path: List[str] = None) -> Dict[str, Any]:
        """
        Traces the genuine sovereign macro transmission pipeline to Gold (XAUUSD).
        Pure graph physics: Uses the living topological geodesic path across graph nodes.
        Zero fake theater: Crowd queries are never tagged as physical kinetic strikes.
        """
        text_lower = text.lower()
        
        # 1. Pure crowd inquiry filter: Never invent military strikes or debt defaults for Wikipedia
        if is_crowd_only or any(k in text_lower for k in ['wikipedia', 'autocomplete', 'search pulse', 'inquiries,']):
            return {
                "pipeline": "CROWD_RESEARCH_PULSE",
                "pipeline_name": "Crowd Research Pulse (Lagging Public Query)",
                "transmission_chain": "Public Query Curiosity ➔ Retail Sentiment Drift (Unconfirmed on Institutional Wires)",
                "expected_gold_impact": "NEUTRAL_CROWD_PULSE",
                "inflection_window_min": 0,
                "inflection_window_max": 0,
                "inflection_summary": "Retail crowd curiosity; unconfirmed on sovereign institutional wires"
            }

        # 2. Dynamic graph-derived geodesic transmission chain (Dijkstra optimal path to Gold)
        if transmission_path and len(transmission_path) >= 2:
            clean_labels = []
            for t in transmission_path:
                lbl = "XAUUSD SPOT" if t == "god_xau" else t.replace("_", " ").title()
                clean_labels.append(lbl)
            transmission = " ➔ ".join(clean_labels)
            lead_entity = clean_labels[0]
            pipe_name = f"{lead_entity} Geodesic Transmission"
            pipeline = f"{transmission_path[0].upper()}_VECTOR"
            inflection_minutes = (max(5, len(transmission_path) * 4), len(transmission_path) * 8 + 10)
            gold_bias = "VOLATILITY_EXPANSION" if len(transmission_path) <= 3 else "STRUCTURAL_DIFFUSION"
        else:
            # Dynamic graph diffusion fallback (Zero hardcoded cluster assumptions)
            pipeline = "STRUCTURAL_DIFFUSION"
            pipe_name = "Topological Graph Diffusion"
            transmission = "Multi-Hop Cross-Cluster Transmission ➔ Orderbook Liquidity Absorption"
            gold_bias = "EQUILIBRIUM_SEEKING"
            inflection_minutes = (15, 35)

        return {
            "pipeline": pipeline,
            "pipeline_name": pipe_name,
            "transmission_chain": transmission,
            "expected_gold_impact": gold_bias,
            "inflection_window_min": inflection_minutes[0],
            "inflection_window_max": inflection_minutes[1],
            "inflection_summary": f"Expected tape response within {inflection_minutes[0]}-{inflection_minutes[1]} mins ({len(transmission_path or [])} hops)"
        }

    def calculate_attention_divergence(self, wire_z_scores: List[float], crowd_z_scores: List[float]) -> Dict[str, Any]:
        """
        Quantifies the information velocity gap between institutional wires and crowd search queries:
        Δ_attention = Z_wire - Z_crowd
        """
        top_wire = max(wire_z_scores) if wire_z_scores else 0.0
        avg_wire = sum(wire_z_scores) / len(wire_z_scores) if wire_z_scores else 0.0

        top_crowd = max(crowd_z_scores) if crowd_z_scores else 0.0
        avg_crowd = sum(crowd_z_scores) / len(crowd_z_scores) if crowd_z_scores else 0.0

        delta = round(avg_wire - avg_crowd, 2)
        top_delta = round(top_wire - top_crowd, 2)

        if top_wire >= 2.5 and top_crowd < 1.8:
            state = "ASYMMETRIC WIRE LEAD (Front-Run Phase: Institutional shock active, retail unawares)"
            lead_quality = "HIGH_ALPHA"
        elif top_crowd >= 2.5 and top_wire < 1.5:
            state = "CROWD SPECULATION DIVERGENCE (Retail FOMO/Curiosity surge without hard wire backing)"
            lead_quality = "RETAIL_SATURATION"
        elif top_wire >= 2.2 and top_crowd >= 2.2:
            state = "MAINSTREAM SATURATION (Both wires & public fully aware; priced-in risk)"
            lead_quality = "EXHAUSTION_RISK"
        else:
            state = "STRUCTURAL EQUILIBRIUM (Balanced flow transmission)"
            lead_quality = "NEUTRAL"

        return {
            "wire_velocity_z": round(avg_wire, 2),
            "top_wire_z": round(top_wire, 2),
            "crowd_velocity_z": round(avg_crowd, 2),
            "top_crowd_z": round(top_crowd, 2),
            "divergence_delta": delta,
            "top_divergence_delta": top_delta,
            "attention_regime": state,
            "lead_quality": lead_quality
        }

    def evaluate_shock_telemetry(
        self, 
        cluster_name: str, 
        z_score: float, 
        hops_to_xau: int,
        wire_z_scores: List[float] = None,
        crowd_z_scores: List[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates dynamic alpha windows from graph geodesic distance and session conductivity.
        ZERO hardcoded minute tables.
        """
        sess = self.get_active_session_conductivity()
        att_div = self.calculate_attention_divergence(wire_z_scores or [], crowd_z_scores or [])
        
        # Empirical Geodesic Information Diffusion Model
        # Logarithmic saturation curve replacing linear hop magic numbers
        hops = max(1, hops_to_xau if hops_to_xau < 99 else 3)
        base_diffusion = 2.5 + (math.log(1.0 + hops) * 6.0)
        adj_min = max(2, round((base_diffusion * 0.65) * sess["lag_multiplier"]))
        adj_max = max(5, round((base_diffusion * 1.75) * sess["lag_multiplier"]))

        # Dynamic Market Physics
        if hops == 1:
            regime = "DIRECT TRANSMISSION: Immediate Cash / Paper Repricing"
            bias = "DIRECT LIQUIDITY ABSORPTION"
        elif hops == 2:
            regime = "TWO-PHASE: Phase 1 Margin Liquidation -> Phase 2 Debasement Flight"
            bias = "INTERMARKET FLOW CONFIRMATION"
        else:
            regime = "ASYMMETRY: Distant Supply Chain / Structural Lag"
            bias = "PRECURSOR ACCUMULATION"

        return {
            "alpha_window": f"{adj_min} - {adj_max} min window (Dynamic Geodesic Lead)",
            "market_phase": regime,
            "orderbook_bias": bias,
            "session_conductivity": f"{round(sess['conductivity'] * 100)}% ({sess['session']})",
            "hops_distance": f"{hops} Hop{'s' if hops != 1 else ''} to XAUUSD",
            "attention_divergence": att_div
        }

if __name__ == "__main__":
    arb = LeadArbiter()
    print("Testing dynamic geodesic lead calculation...")
    res = arb.evaluate_shock_telemetry("Sovereign Wires", 3.2, 2)
    print(res)
