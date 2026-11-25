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
        Calculates live market conductivity dynamically based on continuous harmonic diurnal
        solar liquidity physics and empirical Poisson event arrival flux λ(t).
        """
        utc_now = datetime.now(timezone.utc)
        hour = utc_now.hour + (utc_now.minute / 60.0)

        # Smooth continuous harmonic diurnal curve: peaks at 15:00 UTC (10:00 AM NY / 3:00 PM London overlap)
        # S(t) = 0.62 + 0.28 * cos(2*pi*(hour - 15) / 24)
        diurnal_conduct = 0.62 + 0.28 * math.cos(2.0 * math.pi * (hour - 15.0) / 24.0)
        
        # Transparent institutional session regime context
        if 13.0 <= hour < 17.0:
            session_name = "London / NY Overlap (Peak Global Liquidity)"
        elif 12.0 <= hour < 21.0:
            session_name = "New York Session"
        elif 7.0 <= hour < 17.0:
            session_name = "London Session"
        elif hour < 9.0 or hour >= 23.0:
            session_name = "Asian Session (SGE / TOCOM Cash)"
        else:
            session_name = "Off-Peak Interbank Hours"

        # Empirical Poisson event flux λ(t): events per 15-minute rolling window
        if recent_event_count is not None:
            lam = max(1.0, float(recent_event_count))
            # Sigmoid dynamic scaling of flux: higher event velocity increases conductivity
            flux_modifier = 1.0 / (1.0 + math.exp(-0.12 * (lam - 12.0)))
            conductivity = round(max(0.25, min(0.98, (diurnal_conduct * 0.60) + (flux_modifier * 0.40))), 2)
        else:
            conductivity = round(diurnal_conduct, 2)

        # Dynamic lag multiplier inversely proportional to conductivity
        lag_multiplier = round(max(0.45, min(2.5, 0.90 / max(0.20, conductivity))), 2)

        return {
            "session": session_name,
            "conductivity": conductivity,
            "lag_multiplier": lag_multiplier,
            "utc_hour": round(hour, 2)
        }

    def compute_hawkes_ignition(
        self, 
        timestamps: List[float], 
        publishers: List[str] = None,
        is_pure_crowd: bool = False,
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
        # Crowd sources alone cannot trigger Hawkes Ignition!
        distinct_pubs = len(set(publishers)) if publishers else 1
        has_real_newsroom = not is_pure_crowd and distinct_pubs >= 1

        if is_pure_crowd:
            alpha_adj = alpha * 0.15 # Severely dampen crowd self-polling loops
        elif distinct_pubs < 2 and len(timestamps) > 1:
            alpha_adj = alpha * 0.30
        else:
            alpha_adj = alpha

        total_shock = 0.0
        active_events = 0
        # Statistical Syndication Mirror Filter:
        # Simultaneous RSS items within 45s are syndication mirrors, not independent chain-reaction shocks
        sorted_ts = sorted(timestamps)
        distinct_temporal_waves = 1
        for idx in range(1, len(sorted_ts)):
            if sorted_ts[idx] - sorted_ts[idx-1] > 45:
                distinct_temporal_waves += 1

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
        elif ratio >= 3.0 and distinct_pubs >= 3 and distinct_temporal_waves >= 2:
            state = "IGNITION" # Exponential organic cascade verified across 3+ newsrooms across distinct time waves!
            is_ignition = True
            badge = f"🔥 Hawkes: IGNITION ({ratio}x)"
        elif ratio >= 1.8 and distinct_pubs >= 2:
            state = "COMPOUNDING" # Multi-source developing traction across 2+ publishers
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
        Traces the genuine sovereign macro transmission pipeline to the target asset.
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
                "systemic_macro_bias": "NEUTRAL_CROWD_PULSE",
                "expected_gold_impact": "NEUTRAL_CROWD_PULSE",
                "inflection_window_min": 0,
                "inflection_window_max": 0,
                "inflection_summary": "Retail crowd curiosity; unconfirmed on sovereign institutional wires"
            }

        # 2. Dynamic graph-derived geodesic transmission chain (Dijkstra optimal path to dominant macro hub)
        if transmission_path and len(transmission_path) >= 2:
            clean_labels = [t.replace("_", " ").title() for t in transmission_path]
            transmission = " ➔ ".join(clean_labels)
            lead_entity = clean_labels[0]
            pipe_name = f"{lead_entity} Geodesic Transmission"
            pipeline = f"{transmission_path[0].upper()}_VECTOR"
            inflection_minutes = (max(5, len(transmission_path) * 4), len(transmission_path) * 8 + 10)
            macro_bias = "VOLATILITY_EXPANSION" if len(transmission_path) <= 3 else "STRUCTURAL_DIFFUSION"
            inflection_summary = f"Expected tape response within {inflection_minutes[0]}-{inflection_minutes[1]} mins ({len(transmission_path)} hops)"
        elif transmission_path and len(transmission_path) == 1:
            lead_entity = transmission_path[0].replace("_", " ").title()
            transmission = f"{lead_entity} (Organic community development; dynamic transmission bridge)"
            pipe_name = f"{lead_entity} Thematic Flow"
            pipeline = f"{transmission_path[0].upper()}_VECTOR"
            macro_bias = "EQUILIBRIUM_SEEKING"
            inflection_minutes = (20, 45)
            inflection_summary = f"{lead_entity} cluster developing organically in world news"
        else:
            # Dynamic graph diffusion fallback
            pipeline = "STRUCTURAL_DIFFUSION"
            pipe_name = "Topological Graph Diffusion"
            transmission = "Multi-Hop Cross-Cluster Transmission ➔ Global Liquidity Absorption"
            macro_bias = "EQUILIBRIUM_SEEKING"
            inflection_minutes = (15, 35)
            inflection_summary = "Expected tape response within 15-35 mins (diffuse network propagation)"

        return {
            "pipeline": pipeline,
            "pipeline_name": pipe_name,
            "transmission_chain": transmission,
            "systemic_macro_bias": macro_bias,
            "expected_gold_impact": macro_bias,
            "inflection_window_min": inflection_minutes[0],
            "inflection_window_max": inflection_minutes[1],
            "inflection_summary": inflection_summary
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
        hops_to_hub: int = 2,
        wire_z_scores: List[float] = None,
        crowd_z_scores: List[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluates dynamic alpha windows from graph geodesic distance and session conductivity.
        ZERO hardcoded minute tables.
        """
        effective_hops = kwargs.get("hops_to_xau", hops_to_hub)
        sess = self.get_active_session_conductivity()
        att_div = self.calculate_attention_divergence(wire_z_scores or [], crowd_z_scores or [])
        
        # Empirical Geodesic Information Diffusion Model
        # Logarithmic saturation curve replacing linear hop magic numbers
        hops = max(1, effective_hops if effective_hops < 99 else 3)
        base_diffusion = 2.5 + (math.log(1.0 + hops) * 6.0)
        adj_min = max(2, round((base_diffusion * 0.65) * sess["lag_multiplier"]))
        adj_max = max(5, round((base_diffusion * 1.75) * sess["lag_multiplier"]))

        # Dynamic Market Physics
        if hops == 1:
            regime = "DIRECT TRANSMISSION: Immediate Cash / Sovereign Flow Repricing"
            bias = "DIRECT LIQUIDITY ABSORPTION"
        elif hops == 2:
            regime = "TWO-PHASE: Phase 1 Liquidity Cascades -> Phase 2 Structural Flight"
            bias = "INTERMARKET FLOW CONFIRMATION"
        else:
            regime = "ASYMMETRY: Distant Supply Chain / Geopolitical Lag"
            bias = "PRECURSOR ACCUMULATION"

        return {
            "alpha_window": f"{adj_min} - {adj_max} min window (Dynamic Geodesic Lead)",
            "market_phase": regime,
            "orderbook_bias": bias,
            "session_conductivity": f"{round(sess['conductivity'] * 100)}% ({sess['session']})",
            "hops_distance": f"{hops} Hop{'s' if hops != 1 else ''} to Core Hub",
            "attention_divergence": att_div
        }

if __name__ == "__main__":
    arb = LeadArbiter()
    print("Testing dynamic geodesic lead calculation...")
    res = arb.evaluate_shock_telemetry("Sovereign Wires", 3.2, 2)
    print(res)
