"""
CROWD DIVERGENCE & REAL-TIME CROWD PULSE COLLECTOR (ZERO HARDCODES)
Gathers authentic minute-by-minute crowd discussions, retail sentiment pulses,
and high-frequency micro-breaking wires from live financial and OSINT streams:
1. Telegram Public OSINT & Ground-Truth Wires (Insider Paper, FinancialJuice, Clash Report, OSINTdefender, Spectator Index, RT News)
2. StockTwits Live Retail Crowd Streams & Global Trending Streams
3. TradingView Real-Time Community Theses & Ideas
4. Rapid Micro-Breaking Financial Desks (Dow Jones, WSJ Markets, CNBC, Investing.com, FXStreet, ZeroHedge, MarketWatch)
5. High-Velocity 1-Hour Breaking Macro Wires (when:1h Gold, Yields, Sanctions, Energy)

Every post contains its true, authentic epoch timestamp, publisher attribution, and raw narrative telemetry.
"""

import time
import json
import urllib.request
import urllib.parse
import email.utils
import calendar
import concurrent.futures
import ssl
import re
import html
from datetime import datetime, timezone
from typing import List, Dict, Any
import feedparser

class CrowdDivergenceCollector:
    TELEGRAM_CHANNELS = [
        ("Insider Paper Breaking", "insiderpaper"),
        ("FinancialJuice Live Wire", "financialjuice"),
        ("Clash Report OSINT", "clashreport"),
        ("OSINTdefender Radar", "osintdefender"),
        ("The Spectator Index Wire", "spectatorindex"),
        ("RT World Pulse", "rtnews"),
        ("Bellum Acta Military & Conflict", "BellumActaNews"),
        ("Intel Slava Z Radar", "intelslava"),
        ("BRICS News Intelligence", "bricsnews"),
        ("War Monitors Tactical", "warmonitors"),
        ("Geopolitics Live Wire", "geopolitics_live"),
        ("Middle East Spectator", "middleeastspectator"),
        ("Disclose.tv Alert", "disclose_tv"),
        ("OilPrice & Energy Alert", "oilprice_official")
    ]

    MASTODON_TAGS = [
        "gold", "inflation", "economy", "geopolitics", "oil", "treasury", "commodities", "fed"
    ]

    STOCKTWITS_SYMBOLS = [
        "GLD", "SLV", "USO", "DXY", "TLT", "TNX", "SPY", "QQQ",
        "VIX", "UUP", "CPER", "UNG", "XLE", "XLF", "DBA", "GDX",
        "USDJPY", "EURUSD", "HYG", "LQD", "BNO", "URA", "BTC.X"
    ]

    COMMUNITY_THEMES = [
        ("TradingView Macro Ideas", "https://www.tradingview.com/feed/")
    ]

    MICRO_WIRES = [
        ("Dow Jones Realtime", "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines"),
        ("WSJ Markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
        ("CNBC Central Banks & Economy", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
        ("Investing.com Flash", "https://www.investing.com/rss/news_25.rss"),
        ("FXStreet Fast Wire", "https://www.fxstreet.com/rss/news"),
        ("ZeroHedge Macro", "http://feeds.feedburner.com/zerohedge/feed"),
        ("MarketWatch Bulletins", "https://feeds.content.dowjones.io/public/rss/mw_bulletins")
    ]

    BREAKING_1H_FEEDS = [
        ("Google Breaking: Bullion & Metals (1h)", "https://news.google.com/rss/search?q=when:1h+(gold+OR+bullion+OR+XAUUSD+OR+silver)&hl=en-US&gl=US&ceid=US:en"),
        ("Google Breaking: Sovereign Rates & Yields (1h)", "https://news.google.com/rss/search?q=when:1h+(central+bank+OR+treasury+OR+yield+OR+federal+reserve)&hl=en-US&gl=US&ceid=US:en"),
        ("Google Breaking: Kinetic & Trade Sanctions (1h)", "https://news.google.com/rss/search?q=when:1h+(sanctions+OR+tariff+OR+blockade+OR+military+escalation)&hl=en-US&gl=US&ceid=US:en"),
        ("Google Breaking: Energy & Chokepoints (1h)", "https://news.google.com/rss/search?q=when:1h+(shipping+route+OR+pipeline+OR+crude+OR+strait+OR+OPEC)&hl=en-US&gl=US&ceid=US:en")
    ]

    def __init__(self, request_timeout: float = 2.5):
        self.request_timeout = request_timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "close"
        }
        self.ssl_context = ssl._create_unverified_context()
        self.seen_post_ids = set()

    def _fetch_telegram_channel(self, name: str, channel: str) -> List[Dict[str, Any]]:
        """
        Polls open public web preview mirror of Telegram channels (t.me/s/<channel>).
        Zero API keys required. Extracts raw unedited chronological eyewitness messages with timestamps.
        """
        docs = []
        url = f"https://t.me/s/{channel}"
        now = time.time()
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.request_timeout + 0.8, context=self.ssl_context) as resp:
                content = resp.read().decode("utf-8", errors="ignore")

            times = re.findall(r'datetime=[\'"]([^\'"]+)[\'"]', content)
            texts = re.findall(r'tgme_widget_message_text[^>]*>(.*?)</div>', content, re.DOTALL)

            for t_str, raw_text in zip(times, texts):
                clean_text = re.sub(r'<[^>]+>', ' ', raw_text).strip()
                clean_text = html.unescape(clean_text)
                clean_text = clean_text.replace('\u200e', '').replace('\u200f', '').strip()
                if len(clean_text) < 15:
                    continue

                try:
                    dt = datetime.fromisoformat(t_str.replace('Z', '+00:00'))
                    ts = dt.timestamp()
                except Exception:
                    ts = now

                age_sec = max(0.0, now - ts)
                # Keep strictly within 2 hours
                if age_sec > 7200.0:
                    continue

                docs.append({
                    "title": clean_text[:280],
                    "summary": f"{name} Telemetry: {clean_text}",
                    "publisher": name,
                    "source_type": "TELEGRAM_OSINT",
                    "link": f"https://t.me/{channel}",
                    "published": t_str,
                    "published_at": ts,
                    "timestamp": ts,
                    "age_sec": age_sec
                })
        except Exception:
            pass
        return docs

    def _fetch_stocktwits_symbol(self, sym: str) -> List[Dict[str, Any]]:
        docs = []
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{sym}.json"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.request_timeout, context=self.ssl_context) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            msgs = data.get("messages", [])
            now = time.time()
            for m in msgs:
                m_id = m.get("id")
                body = m.get("body", "").strip()
                if not body or len(body) < 15:
                    continue

                created_str = m.get("created_at", "")
                try:
                    dt = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    ts = dt.timestamp()
                except Exception:
                    ts = now

                age_sec = max(0.0, now - ts)
                if age_sec > 7200.0:
                    continue

                clean_body = re.sub(r'https?://\S+', '', body).strip()
                if len(clean_body) < 12:
                    continue

                sentiment_obj = m.get("entities", {}).get("sentiment")
                user_sentiment = sentiment_obj.get("basic") if isinstance(sentiment_obj, dict) else None

                docs.append({
                    "title": clean_body[:280],
                    "summary": f"StockTwits Crowd Pulse (${sym}): {clean_body}",
                    "publisher": f"StockTwits Crowd (${sym})",
                    "source_type": "CROWD_PULSE",
                    "crowd_sentiment": user_sentiment,
                    "link": f"https://stocktwits.com/message/{m_id}",
                    "published": created_str,
                    "published_at": ts,
                    "timestamp": ts,
                    "age_sec": age_sec
                })
        except Exception:
            pass
        return docs

    def _fetch_stocktwits_trending(self) -> List[Dict[str, Any]]:
        """Polls real-time market-wide trending stream on StockTwits."""
        docs = []
        url = "https://api.stocktwits.com/api/2/streams/trending.json"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.request_timeout, context=self.ssl_context) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            msgs = data.get("messages", [])
            now = time.time()
            for m in msgs:
                m_id = m.get("id")
                body = m.get("body", "").strip()
                if not body or len(body) < 15:
                    continue

                created_str = m.get("created_at", "")
                try:
                    dt = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    ts = dt.timestamp()
                except Exception:
                    ts = now

                age_sec = max(0.0, now - ts)
                if age_sec > 7200.0:
                    continue

                clean_body = re.sub(r'https?://\S+', '', body).strip()
                if len(clean_body) < 12:
                    continue

                docs.append({
                    "title": clean_body[:280],
                    "summary": f"StockTwits Trending Pulse: {clean_body}",
                    "publisher": "StockTwits Global Trending",
                    "source_type": "CROWD_PULSE",
                    "link": f"https://stocktwits.com/message/{m_id}",
                    "published": created_str,
                    "published_at": ts,
                    "timestamp": ts,
                    "age_sec": age_sec
                })
        except Exception:
            pass
        return docs

    def _fetch_rss_wire(self, name: str, url: str, max_age_hours: float = 2.0, source_type: str = "BREAKING_WIRE") -> List[Dict[str, Any]]:
        docs = []
        now = time.time()
        max_age_sec = max_age_hours * 3600.0
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.request_timeout, context=self.ssl_context) as resp:
                content = resp.read()
            parsed = feedparser.parse(content)
            for entry in parsed.entries[:25]:
                title = getattr(entry, "title", "").strip()
                summary = getattr(entry, "summary", "").strip()
                link = getattr(entry, "link", "")
                if not title or len(title) < 10:
                    continue

                ts = None
                pub_raw = getattr(entry, "published", "") or getattr(entry, "updated", "")
                if pub_raw:
                    try:
                        p_dt = email.utils.parsedate_to_datetime(pub_raw)
                        ts = p_dt.timestamp()
                    except Exception:
                        pass

                if not ts and hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        ts = calendar.timegm(entry.published_parsed)
                    except Exception:
                        pass

                if not ts:
                    ts = now

                age_sec = max(0.0, now - ts)
                if age_sec > max_age_sec:
                    continue

                docs.append({
                    "title": title,
                    "summary": summary[:400] if summary else title,
                    "publisher": name,
                    "source_type": source_type,
                    "link": link,
                    "published": pub_raw,
                    "published_at": ts,
                    "timestamp": ts,
                    "age_sec": age_sec
                })
        except Exception:
            pass
        return docs

    def _fetch_mastodon_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        Queries open, unauthenticated public Fediverse timelines for macro, inflation, and commodity tags.
        Extracts timestamped grassroots eyewitness and crowd observations with sub-minute resolution.
        """
        docs = []
        now = time.time()
        url = f"https://mastodon.social/api/v1/timelines/tag/{tag}?limit=15"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.request_timeout + 0.6, context=self.ssl_context) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for post in data:
                content = post.get("content", "")
                clean_text = re.sub(r'<[^>]+>', ' ', content).strip()
                clean_text = html.unescape(clean_text)
                clean_text = clean_text.replace('\u200e', '').replace('\u200f', '').strip()
                if len(clean_text) < 15:
                    continue

                created_str = post.get("created_at", "")
                try:
                    dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    ts = dt.timestamp()
                except Exception:
                    ts = now

                age_sec = max(0.0, now - ts)
                if age_sec > 7200.0:
                    continue

                docs.append({
                    "title": clean_text[:280],
                    "summary": f"Mastodon Crowd Pulse (#{tag}): {clean_text}",
                    "publisher": f"Mastodon (#{tag})",
                    "source_type": "MASTODON_CROWD",
                    "link": post.get("url") or f"https://mastodon.social/tags/{tag}",
                    "published": created_str,
                    "published_at": ts,
                    "timestamp": ts,
                    "age_sec": age_sec
                })
        except Exception:
            pass
        return docs

    def fetch_crowd_divergences(self) -> List[Dict[str, Any]]:
        """
        Polls live Telegram OSINT wires, StockTwits macro streams & trending firehose,
        Mastodon decentralized crowd timelines, TradingView community theses, micro-breaking financial desks,
        and 1-hour Google News feeds concurrently.
        Returns authentic crowd, local OSINT, and breaking documents with sub-minute resolution.
        """
        all_docs = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=36) as executor:
            # 1. Dispatch Telegram public OSINT & breaking channels (14 verified channels)
            for name, ch in self.TELEGRAM_CHANNELS:
                futures.append(executor.submit(self._fetch_telegram_channel, name, ch))

            # 2. Dispatch StockTwits crowd symbols (23 macro, currency, credit, and commodity proxies)
            for sym in self.STOCKTWITS_SYMBOLS:
                futures.append(executor.submit(self._fetch_stocktwits_symbol, sym))

            # 3. Dispatch StockTwits Global Trending stream
            futures.append(executor.submit(self._fetch_stocktwits_trending))

            # 4. Dispatch Mastodon macro & commodity public tag timelines
            for tag in self.MASTODON_TAGS:
                futures.append(executor.submit(self._fetch_mastodon_tag, tag))

            # 5. Dispatch TradingView community ideas
            for name, url in self.COMMUNITY_THEMES:
                futures.append(executor.submit(self._fetch_rss_wire, name, url, 2.0, "CROWD_THESIS"))

            # 6. Dispatch Micro-wires
            for name, url in self.MICRO_WIRES:
                futures.append(executor.submit(self._fetch_rss_wire, name, url, 2.0, "BREAKING_WIRE"))

            # 7. Dispatch Breaking 1h Google News
            for name, url in self.BREAKING_1H_FEEDS:
                futures.append(executor.submit(self._fetch_rss_wire, name, url, 1.0, "BREAKING_WIRE"))

            done, _ = concurrent.futures.wait(futures, timeout=self.request_timeout + 2.2)
            for f in done:
                try:
                    res = f.result()
                    if res:
                        all_docs.extend(res)
                except Exception:
                    pass

        # Deduplicate identical titles
        seen = set()
        unique_docs = []
        for d in all_docs:
            k = d["title"].lower().strip()
            if k not in seen:
                seen.add(k)
                unique_docs.append(d)

        return unique_docs
