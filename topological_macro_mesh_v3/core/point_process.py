"""
POINT PROCESS ENGINE (HAWKES SELF-EXCITING & POISSON BURST DYNAMICS)
Quantifies information arrival acceleration, branching ignition ratios,
and Shannon information surprisal without heuristics.
"""

import math
import time
from typing import List, Dict, Any, Tuple

class PointProcessEngine:
    def __init__(self, baseline_rate: float = 0.05, decay_beta: float = 0.0035):
        """
        decay_beta: ~0.0035 corresponds to an ~3.3 minute half-life for self-excitation shocks.
        """
        self.baseline_rate = baseline_rate
        self.decay_beta = decay_beta

    def compute_poisson_z_score(self, current_count: int, expected_rate: float) -> float:
        """
        Calculates the Poisson arrival velocity Z-score:
        Z = (k - lambda) / sqrt(lambda)
        """
        lam = max(0.1, expected_rate)
        z = (current_count - lam) / math.sqrt(lam)
        return round(float(z), 2)

    def compute_shannon_surprisal(self, mention_count: int, total_docs: int) -> float:
        """
        Calculates Shannon Information Surprisal:
        I(E) = -log2(P(E))
        Higher surprisal indicates high-rarity, high-information news.
        """
        total = max(10, total_docs)
        p = (mention_count + 1) / (total + 2)
        surprisal = max(0.5, -math.log2(p))
        return round(float(surprisal), 2)

    def compute_icf(self, doc_freq: int, total_corpus_docs: int) -> float:
        """
        Calculates Inverse Corpus Frequency (ICF):
        ICF = ln(1 + (N / df))
        """
        total = max(20, total_corpus_docs)
        df = max(1, doc_freq)
        icf = math.log(1.0 + (total / df))
        return round(float(icf), 2)

    def compute_hawkes_ignition(
        self,
        event_timestamps: List[float],
        publishers: List[str],
        now: float = None
    ) -> Dict[str, Any]:
        """
        Continuous-Time Hawkes Self-Exciting Intensity Estimation:
        lambda(t) = mu + sum_{t_i < t} alpha * exp(-beta * (t - t_i))
        
        Branching ratio: eta = alpha / beta
        eta >= 1.0 indicates super-critical information cascading (viral/breaking ignition).
        """
        now = now or time.time()
        if not event_timestamps:
            return {
                "intensity": self.baseline_rate,
                "excitation_ratio": 1.0,
                "state": "EQUILIBRIUM",
                "is_ignition": False,
                "active_shocks": 0,
                "badge": "EQUILIBRIUM"
            }

        # Count active shocks in the last 45 minutes
        window_sec = 2700.0
        recent_ts = [ts for ts in event_timestamps if (now - ts) <= window_sec]
        shock_count = len(recent_ts)

        # Calculate kernel summation
        kernel_sum = sum(math.exp(-self.decay_beta * max(0.0, now - ts)) for ts in recent_ts)
        
        # Adaptive alpha: increases with distinct independent publisher corroboration
        distinct_pubs = len(set(publishers))
        alpha = min(0.0032, 0.0008 + (distinct_pubs * 0.0006))
        
        excitation = alpha * kernel_sum
        total_intensity = self.baseline_rate + excitation
        excitation_ratio = round(total_intensity / max(1e-4, self.baseline_rate), 2)

        # Ignition threshold: excitation ratio >= 2.0 with >= 2 distinct publishers
        is_ignition = (excitation_ratio >= 2.0 and distinct_pubs >= 2)
        
        if excitation_ratio >= 4.0 and distinct_pubs >= 3:
            state = "SUPERCRITICAL_CASCADE"
            badge = "SUPERCRITICAL CASCADE (Runaway Wire Explosion)"
        elif is_ignition:
            state = "IGNITION_POINT"
            badge = "IGNITION POINT (Self-Exciting Acceleration)"
        elif shock_count >= 2:
            state = "PRE_IGNITION_ACCUMULATION"
            badge = "PRE-IGNITION ACCUMULATION"
        else:
            state = "EQUILIBRIUM"
            badge = "EQUILIBRIUM"

        return {
            "intensity": round(total_intensity, 4),
            "excitation_ratio": excitation_ratio,
            "state": state,
            "is_ignition": is_ignition,
            "active_shocks": shock_count,
            "distinct_publishers": distinct_pubs,
            "badge": badge
        }


class HawkesProcessEstimator:
    """Wrapper for entity-level Hawkes intensity and branching ratio estimation."""
    def __init__(self, baseline_rate: float = 0.05, decay_beta: float = 0.0035):
        self.engine = PointProcessEngine(baseline_rate=baseline_rate, decay_beta=decay_beta)

    def estimate(self, timestamps: List[float], t_eval: float = None) -> Dict[str, Any]:
        res = self.engine.compute_hawkes_ignition(timestamps, publishers=["manifold"], now=t_eval)
        branching_ratio = round(min(1.5, (res["excitation_ratio"] - 1.0) / 2.0), 3) if res["excitation_ratio"] > 1.0 else 0.0
        return {
            "lambda_t": res["intensity"],
            "excitation_ratio": res["excitation_ratio"],
            "branching_ratio": max(0.0, branching_ratio),
            "is_excited": res["is_ignition"] or res["excitation_ratio"] >= 1.5,
            "state": res["state"]
        }


class SurprisalCalculator:
    """Calculates corpus-wide Shannon surprisal and Inverse Corpus Frequency."""
    def __init__(self):
        self.entity_counts: Dict[str, int] = {}
        self.total_docs: int = 0
        self.engine = PointProcessEngine()

    def register_entity(self, name: str):
        self.entity_counts[name] = self.entity_counts.get(name, 0) + 1
        self.total_docs += 1

    def calculate_surprisal(self, name: str) -> float:
        count = self.entity_counts.get(name, 1)
        return self.engine.compute_shannon_surprisal(count, self.total_docs)

    def calculate_icf(self, name: str) -> float:
        count = self.entity_counts.get(name, 1)
        return self.engine.compute_icf(count, self.total_docs)

