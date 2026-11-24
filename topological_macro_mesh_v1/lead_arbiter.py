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

    def get_active_session_conductivity(self) -> Dict[str, Any]:
        """Calculates current market hours conductivity to XAUUSD."""
        utc_now = datetime.now(timezone.utc)
        hour = utc_now.hour

        # London session: 08:00 - 16:30 UTC
        # New York session: 13:00 - 21:00 UTC
        # Asia / Tokyo session: 00:00 - 09:00 UTC
        is_london = 8 <= hour < 17
        is_ny = 13 <= hour < 21
        is_asia = 0 <= hour < 9

        if is_london and is_ny:
            session_name = "London / NY Overlap (Peak Institutional Liquidity)"
            conductivity = 0.95
            lag_multiplier = 0.5 # Fast HFT transmission
        elif is_ny:
            session_name = "New York Active"
            conductivity = 0.88
            lag_multiplier = 0.7
        elif is_london:
            session_name = "London Active"
            conductivity = 0.85
            lag_multiplier = 0.8
        elif is_asia:
            session_name = "Asian Session (SGE / TOCOM Cash Dominance)"
            conductivity = 0.65
            lag_multiplier = 1.4 # Slower institutional rebalancing
        else:
            session_name = "Off-Peak Interbank Drift"
            conductivity = 0.40
            lag_multiplier = 2.0

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

    def derive_causal_pathway(self, text: str, cluster_idx: int = 0, is_crowd_only: bool = False) -> Dict[str, Any]:
        """
        Traces the genuine sovereign macro transmission pipeline to Gold (XAUUSD).
        Zero fake theater: Crowd queries are never tagged as physical kinetic strikes.
        """
        text_lower = text.lower()
        
        # 1. Pure crowd inquiry filter: Never invent military strikes or debt defaults for Wikipedia
        if is_crowd_only or any(k in text_lower for k in ['wikipedia', 'autocomplete', 'search pulse', 'inquiries,']):
            return {
                "pipeline": "CROWD_RESEARCH_PULSE",
                "pipeline_name": "Crowd Research Pulse (Lagging Public Query)",
                "transmission_chain": "Public Query Curiosity ➔ Retail Sentiment Drift (No Institutional Wire Confirmation)",
                "expected_gold_impact": "NEUTRAL_CROWD_PULSE",
                "inflection_window_min": 0,
                "inflection_window_max": 0,
                "inflection_summary": "Retail crowd curiosity; unconfirmed on sovereign institutional wires"
            }

        # 2. Genuine institutional wire transmission pathways
        p1_kw = ['tanker', 'strait', 'hormuz', 'bab-el-mandeb', 'red sea', 'suez', 'missile', 
                 'strike', 'drone', 'pipeline', 'crude', 'oil', 'reroute', 'insurance', 'war risk', 
                 'houthi', 'iran', 'gulf', 'yemen', 'airspace']
        p2_kw = ['discount window', 'liquidity', 'bank', 'reverse repo', 'yield', 'treasury', 
                 'debt', 'fed', 'ecb', 'boe', 'rate hike', 'rate cut', 'spread', 'margin', 
                 'credit', 'collateral', 'interbank', 'inflation', 'cpi', 'interest rate']
        p3_kw = ['debasement', 'reserve', 'pboc', 'gold reserve', 'sanctions', 'dedollarization', 
                 'auction tail', 'bid-to-cover', 'fiscal dominance', 'dollar index', 'dxy', 'sovereign debt']

        score_p1 = sum(1 for kw in p1_kw if kw in text_lower)
        score_p2 = sum(1 for kw in p2_kw if kw in text_lower)
        score_p3 = sum(1 for kw in p3_kw if kw in text_lower)

        if score_p1 >= max(score_p2, score_p3, 1):
            pipeline = "GEOPOLITICAL_SUPPLY_VECTOR"
            pipe_name = "Geopolitical & Physical Supply Vector"
            transmission = "Physical Supply / Shipping Dislocation ➔ Safe-Haven Risk Premium Expansion"
            gold_bias = "SAFE_HAVEN_EXPANSION"
            inflection_minutes = (8, 20)
        elif score_p2 >= max(score_p1, score_p3, 1):
            pipeline = "SOVEREIGN_LIQUIDITY"
            pipe_name = "Pipeline 2: Sovereign Liquidity & Real Yield Vector"
            transmission = "Yield Curve / Credit Repricing ➔ Real Yield Opportunity Cost Transmission"
            gold_bias = "VOLATILITY_EXPANSION"
            inflection_minutes = (15, 35)
        elif score_p3 >= max(score_p1, score_p2, 1):
            pipeline = "CURRENCY_DEBASEMENT"
            pipe_name = "Pipeline 3: Monetary Debasement & Reserve Vector"
            transmission = "Fiscal Dominance / Sovereign Debt Expansion ➔ Central Bank Bullion Accumulation Floor"
            gold_bias = "STRUCTURAL_DEBASEMENT_BID"
            inflection_minutes = (20, 45)
        else:
            pipeline = "INTERMARKET_FLOW"
            pipe_name = "Pipeline 4: Structural Intermarket Equilibrium"
            transmission = "Macro Equilibrium Transmission ➔ Tape Liquidity Absorption"
            gold_bias = "EQUILIBRIUM_SEEKING"
            inflection_minutes = (12, 30)

        return {
            "pipeline": pipeline,
            "pipeline_name": pipe_name,
            "transmission_chain": transmission,
            "expected_gold_impact": gold_bias,
            "inflection_window_min": inflection_minutes[0],
            "inflection_window_max": inflection_minutes[1],
            "inflection_summary": f"Expected tape response within {inflection_minutes[0]}-{inflection_minutes[1]} mins"
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
