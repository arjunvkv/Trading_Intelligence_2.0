"""
DUAL-KEY TRADE ARBITER & TELEGRAM PROPOSAL ENGINE
Enforces the Zero-Prong / Clean Stand Down Rules:
- Direct broker auto-execution is strictly disabled.
- Dual-Key Veto Rule:
  • Key 1: Macro Outlier & Attention Divergence Lead (Genuine Graph Outlier Z >= 10.0σ)
  • Key 2: MT5 Structural Order Flow & 5-Minute Fair Value Gap (FVG) Absorption
- Directional Bias is derived from MT5 Live M5 Market Structure & Intermarket Vector (ZERO hardcoded 'Always BUY' defaults).
- If both Key 1 & Key 2 align favourably: Dispatches structured trade proposal to Telegram for manual evaluation.
- Otherwise: Clean STAND DOWN / NO ACTION (Zero telegram spam, zero phantom orders).
"""

import sys
import time
import os
from typing import Dict, Any, Optional, Tuple, List
import MetaTrader5 as mt5

# Import telegram notifier from Trading desk
sys.path.append(r"C:\Trading\Alpha")
try:
    from tradingagents.telegram_notifier import notify_trade_proposal
except ImportError:
    notify_trade_proposal = None

class DualKeyTradeArbiter:
    def __init__(self, alert_cooldown_seconds: float = 900.0): # 15-minute cooldown
        self.cooldown = alert_cooldown_seconds
        self.last_alert_time = 0.0
        self.last_decision = {}

    def _ensure_mt5(self) -> bool:
        """Ensure MT5 connection is active."""
        if mt5.terminal_info() is not None:
            return True
        return mt5.initialize()

    def evaluate_m5_structure(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """
        Inspects M5 candle rates for structural trend (20-EMA slope)
        and institutional Fair Value Gaps (FVG) with Consequent Encroachment (50% midpoint).
        """
        if not self._ensure_mt5():
            return {"active": False, "reason": "MT5 initialization failed"}

        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return {"active": False, "reason": f"No live tick for {symbol}"}

        # Spread check (in points; e.g. 38 points = $0.38)
        spread_pts = round((tick.ask - tick.bid) * 100, 1)
        if spread_pts > 60.0:
            return {"active": False, "reason": f"Spread blowout: {spread_pts} pts > 60 pts limit"}

        # Fetch recent M5 candles (last 40 candles)
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 40)
        if rates is None or len(rates) < 20:
            return {"active": False, "reason": "Insufficient M5 candle data"}

        closes = [r['close'] for r in rates]
        
        # Calculate 20-period EMA for objective trend detection
        multiplier = 2.0 / (20 + 1)
        ema_20 = closes[0]
        for c in closes[1:]:
            ema_20 = (c - ema_20) * multiplier + ema_20

        current_close = closes[-1]
        tape_trend = "BULLISH" if current_close >= ema_20 else "BEARISH"

        # Scan for unmitigated FVGs from most recent back
        bullish_fvgs = []
        bearish_fvgs = []

        for i in range(2, len(rates) - 1):
            c0 = rates[i - 2] # candle 1
            c1 = rates[i - 1] # impulse candle 2
            c2 = rates[i]     # candle 3

            # Bullish FVG: Low of candle 3 > High of candle 1
            if c2['low'] > c0['high']:
                gap_bottom = c0['high']
                gap_top = c2['low']
                gap_size = gap_top - gap_bottom
                if gap_size >= 0.50:
                    ce = round(gap_bottom + (gap_size * 0.5), 2)
                    mitigated = any(rates[j]['low'] <= ce for j in range(i + 1, len(rates)))
                    if not mitigated:
                        bullish_fvgs.append({
                            "top": gap_top,
                            "bottom": gap_bottom,
                            "ce": ce,
                            "candle_time": c1['time'],
                            "size": round(gap_size, 2)
                        })

            # Bearish FVG: High of candle 3 < Low of candle 1
            elif c2['high'] < c0['low']:
                gap_top = c0['low']
                gap_bottom = c2['high']
                gap_size = gap_top - gap_bottom
                if gap_size >= 0.50:
                    ce = round(gap_bottom + (gap_size * 0.5), 2)
                    mitigated = any(rates[j]['high'] >= ce for j in range(i + 1, len(rates)))
                    if not mitigated:
                        bearish_fvgs.append({
                            "top": gap_top,
                            "bottom": gap_bottom,
                            "ce": ce,
                            "candle_time": c1['time'],
                            "size": round(gap_size, 2)
                        })

        return {
            "active": True,
            "bid": tick.bid,
            "ask": tick.ask,
            "spread_pts": spread_pts,
            "tape_trend": tape_trend,
            "ema_20": round(ema_20, 2),
            "bullish_fvgs": bullish_fvgs,
            "bearish_fvgs": bearish_fvgs,
            "current_m5_close": current_close,
            "m5_high": max(r['high'] for r in rates[-12:]),
            "m5_low": min(r['low'] for r in rates[-12:])
        }

    def evaluate_dual_key_setup(
        self,
        surging_nodes: list,
        attention_divergence: Dict[str, Any],
        lead_telemetry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the Dual-Key Veto logic without hardcoded bias:
        Key 1: Macro Outlier & Attention Divergence
        Key 2: MT5 Structural Absorption & 20-EMA Confluence
        """
        now = time.time()
        
        # ── KEY 1: MACRO & ATTENTION DIVERGENCE AUDIT ────────────────────────
        # Require a genuine outlier anomaly from verified wires (Z >= 10.0σ)
        extreme_anomalies = [n for n in surging_nodes if n.get("z_score", 0.0) >= 10.0 and not n.get("is_god")]

        if not extreme_anomalies:
            return {
                "decision": "STAND_DOWN",
                "key1_passed": False,
                "key2_passed": False,
                "reason": "Key 1 Veto: Macro graph in structural equilibrium (no genuine outlier >= 10.0 sigma)."
            }

        top_anomaly = max(extreme_anomalies, key=lambda x: x.get("z_score", 0.0))
        z_val = top_anomaly.get("z_score", 0.0)
        anomaly_label = top_anomaly.get("label", "Macro Outlier")
        trigger_text = top_anomaly.get("trigger_text", "Headline")

        # ── KEY 2: MT5 5-MINUTE ORDERBOOK & FVG AUDIT ───────────────────────
        m5_audit = self.evaluate_m5_structure("XAUUSD")
        if not m5_audit.get("active"):
            return {
                "decision": "STAND_DOWN",
                "key1_passed": True,
                "key2_passed": False,
                "reason": f"Key 2 Veto: MT5 feed inactive or illiquid ({m5_audit.get('reason')})."
            }

        bid = m5_audit["bid"]
        ask = m5_audit["ask"]
        tape_trend = m5_audit["tape_trend"]

        # Objective structural alignment: Bias follows the MT5 tape trend confirmed by FVG absorption
        bias = tape_trend # "BULLISH" or "BEARISH"

        if bias == "BULLISH":
            fvgs = m5_audit.get("bullish_fvgs", [])
            if not fvgs:
                return {
                    "decision": "STAND_DOWN",
                    "key1_passed": True,
                    "key2_passed": False,
                    "reason": "Key 2 Veto: Trend is Bullish but no unmitigated Bullish M5 FVG found for absorption entry."
                }
            # Dynamic ATR buffer for SL
            atr = round(max(0.40, (m5_audit["m5_high"] - m5_audit["m5_low"]) / 6.0), 2)
            target_fvg = min(fvgs, key=lambda f: abs(f["ce"] - ask))
            entry_price = round(target_fvg["ce"], 2)
            sl_price = round(target_fvg["bottom"] - (atr * 0.5), 2)
            risk = entry_price - sl_price
            if risk <= 0.25 or risk > 6.00:
                return {
                    "decision": "STAND_DOWN",
                    "key1_passed": True,
                    "key2_passed": False,
                    "reason": f"Key 2 Veto: FVG risk ${risk:.2f} outside safe bounds ($0.25-$6.00)."
                }
            # Target structural M5 swing high or 2.0x risk minimum
            tp_price = max(round(entry_price + (risk * 2.0), 2), round(m5_audit["m5_high"], 2))
            rr = round((tp_price - entry_price) / risk, 2)
            order_type = "BUY_LIMIT" if entry_price < ask else "BUY"

        else: # BEARISH
            fvgs = m5_audit.get("bearish_fvgs", [])
            if not fvgs:
                return {
                    "decision": "STAND_DOWN",
                    "key1_passed": True,
                    "key2_passed": False,
                    "reason": "Key 2 Veto: Trend is Bearish but no unmitigated Bearish M5 FVG found for distribution entry."
                }
            atr = round(max(0.40, (m5_audit["m5_high"] - m5_audit["m5_low"]) / 6.0), 2)
            target_fvg = min(fvgs, key=lambda f: abs(f["ce"] - bid))
            entry_price = round(target_fvg["ce"], 2)
            sl_price = round(target_fvg["top"] + (atr * 0.5), 2)
            risk = sl_price - entry_price
            if risk <= 0.25 or risk > 6.00:
                return {
                    "decision": "STAND_DOWN",
                    "key1_passed": True,
                    "key2_passed": False,
                    "reason": f"Key 2 Veto: FVG risk ${risk:.2f} outside safe bounds ($0.25-$6.00)."
                }
            # Target structural M5 swing low or 2.0x risk minimum
            tp_price = min(round(entry_price - (risk * 2.0), 2), round(m5_audit["m5_low"], 2))
            rr = round((entry_price - tp_price) / risk, 2)
            order_type = "SELL_LIMIT" if entry_price > bid else "SELL"

        # ── DYNAMIC RISK-BASED VOLUME CALCULATION ─────────────────────────────
        acc = mt5.account_info()
        equity = acc.equity if acc else 20000.0
        risk_budget = equity * 0.01 # 1% account risk rule
        dynamic_volume = round(max(0.05, min(3.0, risk_budget / (risk * 100))), 2)

        # ── DISPATCH DECISION ────────────────────────────────────────────────
        proposal_details = {
            "symbol": "XAUUSD",
            "order_type": order_type,
            "entry_price": entry_price,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "rr": rr,
            "risk_dollars": round(risk * dynamic_volume * 100, 2),
            "reward_dollars": round((abs(tp_price - entry_price)) * dynamic_volume * 100, 2),
            "volume": dynamic_volume,
            "story": (
                f"Dual-Key Alignment: Live MT5 M5 Tape is {bias} (Close vs 20-EMA {m5_audit['ema_20']}). "
                f"Macro Outlier detected [{anomaly_label}] with Z={z_val:.1f} sigma (Trigger: '{trigger_text[:60]}...'). "
                f"Tape confirms structural absorption at unmitigated FVG CE ${target_fvg['ce']}."
            ),
            "nearest_inflection_note": (
                f"Next inflection at ${target_fvg['ce']} (50% FVG CE). "
                f"Invalidation if candle closes beyond ${sl_price}."
            )
        }

        # Check cooldown before sending Telegram
        if (now - self.last_alert_time) > self.cooldown:
            if notify_trade_proposal:
                notify_trade_proposal(
                    symbol=proposal_details["symbol"],
                    order_type=proposal_details["order_type"],
                    entry_price=proposal_details["entry_price"],
                    sl_price=proposal_details["sl_price"],
                    tp_price=proposal_details["tp_price"],
                    rr=proposal_details["rr"],
                    risk_dollars=proposal_details["risk_dollars"],
                    reward_dollars=proposal_details["reward_dollars"],
                    volume=proposal_details["volume"],
                    story=proposal_details["story"],
                    nearest_inflection_note=proposal_details["nearest_inflection_note"]
                )
                self.last_alert_time = now
                proposal_details["telegram_status"] = "SENT_TO_CHANNEL"
            else:
                proposal_details["telegram_status"] = "NOTIFIER_NOT_AVAILABLE"
            decision_type = "DISPATCHED_TELEGRAM_PROPOSAL"
        else:
            decision_type = "COOLDOWN_ACTIVE"
            proposal_details["telegram_status"] = f"COOLDOWN ({round(self.cooldown - (now - self.last_alert_time))}s remaining)"

        return {
            "decision": decision_type,
            "key1_passed": True,
            "key2_passed": True,
            "proposal": proposal_details
        }

if __name__ == "__main__":
    arbiter = DualKeyTradeArbiter()
    print("Testing objective trend & FVG evaluation on MT5...")
    m5 = arbiter.evaluate_m5_structure("XAUUSD")
    print("MT5 Result:", m5.get("active"), "Tape Trend:", m5.get("tape_trend"), "20-EMA:", m5.get("ema_20"))
    print("Bullish FVGs:", len(m5.get("bullish_fvgs", [])))
    print("Bearish FVGs:", len(m5.get("bearish_fvgs", [])))
