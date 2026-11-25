"""
GEOPOLITICAL WIRES COLLECTOR
Monitors defense, kinetic conflicts, maritime chokepoint blockades,
sanctions regimes, critical commodity trade controls, and bilateral diplomacy.
Includes full collector health diagnostics.
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
        {"name": "Strategic Energy & Maritime Chokepoints", "url": "https://news.google.com/rss/search?q=%22Suez+Canal%22+OR+%22Bab+el-Mandeb%22+OR+%22OPEC+output%22+OR+%22oil+embargo%22+OR+%22tanker+seizure%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Trade Sanctions & Export Controls", "url": "https://news.google.com/rss/search?q=%22export+controls%22+OR+%22OFAC+sanctions%22+OR+%22trade+tariffs%22+OR+%22secondary+sanctions%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Middle East Security & Military Fronts", "url": "https://news.google.com/rss/search?q=%22missile+strike%22+OR+%22naval+blockade%22+OR+%22drone+attack%22+OR+%22ceasefire+talks%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Asia-Pacific & Taiwan Strait Wires", "url": "https://news.google.com/rss/search?q=%22Taiwan+Strait%22+OR+%22South+China+Sea%22+OR+%22semiconductor+sanctions%22+OR+%22rare+earths%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Eastern Europe & NATO Defense", "url": "https://news.google.com/rss/search?q=%22NATO+defense%22+OR+%22Black+Sea+grain%22+OR+%22sanctions+evasion%22+OR+%22border+skirmish%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Critical Minerals & Supply Disruptions", "url": "https://news.google.com/rss/search?q=%22rare+earths+export%22+OR+%22lithium+nationalization%22+OR+%22uranium+supply%22+OR+%22copper+mine+strike%22+when:1d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Nikkei Asia Macro & Central Banks", "url": "https://news.google.com/rss/search?q=site:asia.nikkei.com+OR+%22Nikkei+Asia%22+OR+%22Bank+of+Japan%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "South China Morning Post Macro & Trade", "url": "https://news.google.com/rss/search?q=site:scmp.com+OR+%22South+China+Morning+Post%22+OR+%22PBOC%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "TASS Diplomatic & Energy Vectors", "url": "https://news.google.com/rss/search?q=site:tass.com+OR+%22TASS%22+OR+%22Russian+Central+Bank%22+when:2d&hl=en-US&gl=US&ceid=US:en"}
    ]

    def __init__(self, request_timeout: float = 6.0):
        self.request_timeout = request_timeout
        self.last_fetch: Dict[str, float] = {}
        self.feed_states: Dict[str, Dict[str, Any]] = {}
        self.cooldown_sec = 25.0

    def fetch_wires(self) -> List[Dict[str, Any]]:
        """Collects latest articles across geopolitical feeds."""
        articles = []
        now = time.time()

        for feed_meta in self.GEOPOLITICAL_FEEDS:
            name = feed_meta["name"]
            url = feed_meta["url"]

            if name not in self.feed_states:
                self.feed_states[name] = {"source": name, "status": "HEALTHY", "last_success": 0.0, "error_msg": None}

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
                for entry in parsed.entries[:14]:
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", "").strip()
                    link = entry.get("link", url)
                    published = entry.get("published", "")

                    if title and len(title) > 10:
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
                self.feed_states[name]["status"] = "HEALTHY"
                self.feed_states[name]["last_success"] = now
                self.feed_states[name]["error_msg"] = None
            except Exception as e:
                self.feed_states[name]["status"] = "CONNECTION_ERROR"
                self.feed_states[name]["error_msg"] = str(e)[:50]
                continue

        return articles

    def get_health_states(self) -> Dict[str, Any]:
        """Provides status of geopolitical feeds for the UI diagnostics flyout."""
        healthy_count = sum(1 for s in self.feed_states.values() if s["status"] == "HEALTHY")
        return {
            "healthy_count": healthy_count,
            "total_count": len(self.GEOPOLITICAL_FEEDS),
            "states": list(self.feed_states.values())
        }
