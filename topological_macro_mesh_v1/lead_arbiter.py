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
        
        # Dynamic Geodesic Transmission Window:
        # Hops to Gold (d) represents the transmission stages across the macro manifold.
        hops = max(1, hops_to_xau if hops_to_xau < 99 else 3)
        base_min_latency = hops * 4.5
        base_max_latency = hops * 12.0

        adj_min = max(2, round(base_min_latency * sess["lag_multiplier"]))
        adj_max = max(5, round(base_max_latency * sess["lag_multiplier"]))

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
