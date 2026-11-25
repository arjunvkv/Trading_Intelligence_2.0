"""
GEOPOLITICAL WIRES COLLECTOR
Monitors defense, kinetic conflicts, maritime chokepoint blockades,
sanctions regimes, and strategic diplomatic bilateral summits.
"""

import time
import urllib.request
import ssl
import feedparser
from typing import List, Dict, Any

class GeopoliticalWiresCollector:
    GEOPOLITICAL_FEEDS = [
        {"name": "AP Diplomatic & World", "url": "https://news.google.com/rss/search?q=%22diplomatic%22+OR+%22sanctions%22+OR+%22ceasefire%22+OR+%22military+strike%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Reuters Sovereign Defense", "url": "https://news.google.com/rss/search?q=%22sovereign+defense%22+OR+%22strait+of+hormuz%22+OR+%22red+sea+shipping%22+OR+%22taiwan+strait%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "BBC World Geopolitics", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
        {"name": "Al Jazeera Geopolitical Wires", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
        {"name": "France 24 International", "url": "https://www.france24.com/en/rss"},
        {"name": "Strategic Energy & Chokepoints", "url": "https://news.google.com/rss/search?q=%22Suez+Canal%22+OR+%22Bab+el-Mandeb%22+OR+%22OPEC+output+cut%22+OR+%22oil+embargo%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Trade Sanctions & Export Controls", "url": "https://news.google.com/rss/search?q=%22export+controls%22+OR+%22OFAC+sanctions%22+OR+%22trade+tariffs%22+when:1d&hl=en-US&gl=US&ceid=US:en"}
    ]

    def __init__(self, request_timeout: float = 6.0):
        self.request_timeout = request_timeout
        self.last_fetch: Dict[str, float] = {}
        self.cooldown_sec = 25.0

    def fetch_wires(self) -> List[Dict[str, Any]]:
        """Collects latest articles across geopolitical feeds."""
        articles = []
        now = time.time()

        for feed_meta in self.GEOPOLITICAL_FEEDS:
            name = feed_meta["name"]
            url = feed_meta["url"]

            if now - self.last_fetch.get(name, 0.0) < self.cooldown_sec:
                continue

            try:
                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SovereignMacro/3.0"}
                )
                with urllib.request.urlopen(req, context=ctx, timeout=self.request_timeout) as resp:
                    raw_data = resp.read()

                parsed = feedparser.parse(raw_data)
                for entry in parsed.entries[:5]:
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", "").strip()
                    link = entry.get("link", url)
                    published = entry.get("published", "")

                    if title and len(title) > 12:
                        articles.append({
                            "title": title,
                            "summary": summary,
                            "publisher": name,
                            "source_type": "GEOPOLITICAL_KINETIC",
                            "link": link,
                            "published": published,
                            "timestamp": now
                        })
                self.last_fetch[name] = now
            except Exception:
                continue

        return articles
