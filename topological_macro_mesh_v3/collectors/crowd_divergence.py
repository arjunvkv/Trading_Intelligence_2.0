"""
CROWD DIVERGENCE COLLECTOR
Monitors Wikipedia pageview velocity across critical sovereign macroeconomic
and financial stability concepts to detect crowd panic or quiet accumulation
divergence before mainstream headlines erupt.
"""

import time
import json
import urllib.request
import ssl
from datetime import datetime, timedelta
from typing import List, Dict, Any

class CrowdDivergenceCollector:
    TRACKED_TOPICS = [
        "De-dollarization",
        "Hyperinflation",
        "Recession",
        "Sovereign_debt",
        "Central_bank",
        "Quantitative_easing",
        "Bank_run",
        "Stagflation",
        "BRICS",
        "Sanctions",
        "Foreign-exchange_reserves",
        "Liquidity_crisis",
        "Government_debt",
        "Default_(finance)"
    ]

    def __init__(self, cooldown_sec: float = 300.0, request_timeout: float = 5.0):
        self.cooldown_sec = cooldown_sec
        self.request_timeout = request_timeout
        self.last_fetch: float = 0.0
        self.cached_divergences: List[Dict[str, Any]] = []
        self.ssl_context = ssl._create_unverified_context()

    def fetch_crowd_divergences(self) -> List[Dict[str, Any]]:
        """
        Calculates day-over-day search velocity for sovereign topics.
        Generates precursor whisper signals if velocity surges >= 25%.
        """
        now = time.time()
        if now - self.last_fetch < self.cooldown_sec and self.cached_divergences:
            return self.cached_divergences

        divergences = []
        # Calculate recent date strings (UTC)
        # Note: Wikimedia pageviews usually trail by 1-2 days
        ref_dt = datetime.utcnow() - timedelta(days=2)
        end_str = ref_dt.strftime("%Y%m%d00")
        start_dt = ref_dt - timedelta(days=4)
        start_str = start_dt.strftime("%Y%m%d00")

        headers = {
            "User-Agent": "SovereignMacro/3.0 (academic macro telemetry; contact@intel.org)"
        }

        for topic in self.TRACKED_TOPICS:
            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{topic}/daily/{start_str}/{end_str}"
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=self.request_timeout) as resp:
                    raw = resp.read()
                data = json.loads(raw)
                items = data.get("items", [])
                if len(items) >= 2:
                    v_prev = float(items[-2]["views"])
                    v_curr = float(items[-1]["views"])
                    if v_prev > 100: # Exclude tiny baselines
                        velocity = ((v_curr - v_prev) / v_prev) * 100.0
                        if velocity >= 25.0: # Significant crowd attention surge
                            topic_clean = topic.replace("_", " ")
                            title = f"Crowd Divergence Surge: '{topic_clean}' attention jumped +{velocity:.1f}% DoD"
                            summary = f"Precursor public attention shift detected on '{topic_clean}'. Daily pageviews surged from {int(v_prev):,} to {int(v_curr):,} (+{velocity:.1f}%)."
                            divergences.append({
                                "title": title,
                                "summary": summary,
                                "publisher": "Crowd Attention Telemetry",
                                "source_type": "CROWD_DIVERGENCE",
                                "link": f"https://en.wikipedia.org/wiki/{topic}",
                                "published": items[-1].get("timestamp", ""),
                                "velocity_pct": velocity,
                                "timestamp": now
                            })
            except Exception:
                continue

        self.cached_divergences = divergences
        self.last_fetch = now
        return divergences
