"""
INTERMARKET FLOWS COLLECTOR
Monitors sovereign bond yields, currency indices, inflation break-evens,
and critical commodity pressures to generate macro transmission pulses.
"""

import time
from typing import List, Dict, Any, Optional
import yfinance as yf

class IntermarketFlowsCollector:
    ASSET_MAP = {
        "^TNX": {"name": "US 10-Year Treasury Yield", "category": "SOVEREIGN_YIELD", "unit": "%"},
        "DX-Y.NYB": {"name": "US Dollar Index", "category": "CURRENCY_RESERVE", "unit": "pts"},
        "TIP": {"name": "TIPS Real Yield ETF", "category": "REAL_RATE_PROXY", "unit": "$"},
        "CL=F": {"name": "WTI Crude Oil", "category": "ENERGY_FLOW", "unit": "$/bbl"},
        "HG=F": {"name": "Copper Futures", "category": "INDUSTRIAL_DEMAND", "unit": "$/lb"},
        "^VIX": {"name": "CBOE Volatility Index", "category": "VOLATILITY_LIQUIDITY", "unit": "pts"},
        "EURUSD=X": {"name": "EUR/USD Currency Cross", "category": "SOVEREIGN_FX", "unit": "rate"}
    }

    def __init__(self, cooldown_sec: float = 60.0):
        self.cooldown_sec = cooldown_sec
        self.last_fetch: float = 0.0
        self.prev_prices: Dict[str, float] = {}
        self.cached_telemetry: Dict[str, Any] = {}

    def fetch_flows(self) -> List[Dict[str, Any]]:
        """
        Fetches latest quotes, checks for notable percentage shifts,
        and generates sovereign macro flow pulse events.
        """
        now = time.time()
        if now - self.last_fetch < self.cooldown_sec and self.cached_telemetry:
            return []

        events = []
        telemetry = {}

        try:
            tickers = list(self.ASSET_MAP.keys())
            data = yf.download(tickers=tickers, period="5d", interval="1d", progress=False)
            
            if not data.empty and "Close" in data:
                close_df = data["Close"]
                for ticker, meta in self.ASSET_MAP.items():
                    if ticker not in close_df:
                        continue
                    series = close_df[ticker].dropna()
                    if series.empty:
                        continue
                    
                    curr_price = float(series.iloc[-1])
                    prev_close = float(series.iloc[-2]) if len(series) >= 2 else curr_price
                    pct_change = ((curr_price - prev_close) / prev_close) * 100.0 if prev_close > 0 else 0.0

                    telemetry[meta["name"]] = {
                        "ticker": ticker,
                        "price": round(curr_price, 4),
                        "prev_close": round(prev_close, 4),
                        "pct_change": round(pct_change, 2),
                        "unit": meta["unit"],
                        "category": meta["category"],
                        "timestamp": now
                    }

                    # Detect macro shock or regime pulse
                    abs_change = abs(pct_change)
                    direction = "expansion" if pct_change > 0 else "contraction"
                    if abs_change >= 0.35: # Meaningful macro move
                        title = f"{meta['name']} {direction} ({pct_change:+.2f}%) at {curr_price:.2f} {meta['unit']}"
                        summary = f"Sovereign intermarket flow detected: {meta['name']} shifted {pct_change:+.2f}% to {curr_price:.4f} {meta['unit']}."
                        events.append({
                            "title": title,
                            "summary": summary,
                            "publisher": "Sovereign Market Telemetry",
                            "source_type": meta["category"],
                            "link": f"https://finance.yahoo.com/quote/{ticker}",
                            "published": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(now)),
                            "timestamp": now
                        })

            self.cached_telemetry = telemetry
            self.last_fetch = now
        except Exception:
            pass

        return events

    def get_latest_telemetry(self) -> Dict[str, Any]:
        """Returns the latest snapshot of intermarket telemetry."""
        return self.cached_telemetry
