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
        {"name": "AP Diplomatic & World", "url": "https://news.google.com/rss/search?q=%22diplomatic%22+OR+%22sanctions%22+OR+%22ceasefire%22+OR+%22military+strike%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Reuters Sovereign Defense", "url": "https://news.google.com/rss/search?q=%22sovereign+defense%22+OR+%22strait+of+hormuz%22+OR+%22red+sea+shipping%22+OR+%22taiwan+strait%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "BBC World Geopolitics", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
        {"name": "Al Jazeera Geopolitical Wires", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
        {"name": "France 24 International", "url": "https://www.france24.com/en/rss"},
        {"name": "Strategic Energy & Maritime Chokepoints", "url": "https://news.google.com/rss/search?q=%22Suez+Canal%22+OR+%22Bab+el-Mandeb%22+OR+%22OPEC+output%22+OR+%22oil+embargo%22+OR+%22tanker+seizure%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Trade Sanctions & Export Controls", "url": "https://news.google.com/rss/search?q=%22export+controls%22+OR+%22OFAC+sanctions%22+OR+%22trade+tariffs%22+OR+%22secondary+sanctions%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Middle East Security & Military Fronts", "url": "https://news.google.com/rss/search?q=%22missile+strike%22+OR+%22naval+blockade%22+OR+%22drone+attack%22+OR+%22ceasefire+talks%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Asia-Pacific & Taiwan Strait Wires", "url": "https://news.google.com/rss/search?q=%22Taiwan+Strait%22+OR+%22South+China+Sea%22+OR+%22semiconductor+sanctions%22+OR+%22rare+earths%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Eastern Europe & NATO Defense", "url": "https://news.google.com/rss/search?q=%22NATO+defense%22+OR+%22Black+Sea+grain%22+OR+%22sanctions+evasion%22+OR+%22border+skirmish%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Critical Minerals & Supply Disruptions", "url": "https://news.google.com/rss/search?q=%22rare+earths+export%22+OR+%22lithium+nationalization%22+OR+%22uranium+supply%22+OR+%22copper+mine+strike%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Nikkei Asia Macro & Central Banks", "url": "https://news.google.com/rss/search?q=site:asia.nikkei.com+OR+%22Nikkei+Asia%22+OR+%22Bank+of+Japan%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "South China Morning Post Macro & Trade", "url": "https://news.google.com/rss/search?q=site:scmp.com+OR+%22South+China+Morning+Post%22+OR+%22PBOC%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "TASS Diplomatic & Energy Vectors", "url": "https://news.google.com/rss/search?q=site:tass.com+OR+%22TASS%22+OR+%22Russian+Central+Bank%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Defense One & Military Logistics", "url": "https://news.google.com/rss/search?q=%22Defense+One%22+OR+%22CENTCOM%22+OR+%22missile+defense%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Baltic Dry & Global Freight Shipping", "url": "https://news.google.com/rss/search?q=%22Baltic+Dry%22+OR+%22container+shipping%22+OR+%22freight+rates%22+OR+%22port+congestion%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Global Energy Infrastructure & Pipelines", "url": "https://news.google.com/rss/search?q=%22pipeline+leak%22+OR+%22gas+transit%22+OR+%22crude+export%22+OR+%22energy+crisis%22+when:2d&hl=en-US&gl=US&ceid=US:en"}
    ]

    def __init__(self, request_timeout: float = 6.0):
        self.request_timeout = request_timeout
        self.last_fetch: Dict[str, float] = {}
        self.feed_states: Dict[str, Dict[str, Any]] = {}
        self.cooldown_sec = 10.0
        self.max_age_seconds = 48.0 * 3600.0  # 48-Hour Publication Age Gate

    def _parse_pub_ts(self, entry: Dict[str, Any]) -> float:
        """Extracts unix timestamp from entry published_parsed or published string."""
        now = time.time()
        if entry.get("published_parsed"):
            try:
                return float(time.mktime(entry.published_parsed))
            except Exception:
                pass
        pub_raw = entry.get("published", "")
        if pub_raw:
            import email.utils
            try:
                dt = email.utils.parsedate_to_datetime(pub_raw)
                if dt:
                    return dt.timestamp()
            except Exception:
                pass
        return now

    def _fetch_single_feed(self, feed_meta: Dict[str, Any], now: float) -> List[Dict[str, Any]]:
        name = feed_meta["name"]
        url = feed_meta["url"]

        if name not in self.feed_states:
            self.feed_states[name] = {"source": name, "status": "HEALTHY", "last_success": 0.0, "error_msg": None}

        if now - self.last_fetch.get(name, 0.0) < self.cooldown_sec:
            return []

        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SovereignMacro/3.0"}
            )
            with urllib.request.urlopen(req, context=ctx, timeout=self.request_timeout) as resp:
                raw_data = resp.read()

            parsed = feedparser.parse(raw_data)
            feed_candidates = []
            for entry in parsed.entries[:40]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                link = entry.get("link", url)
                published = entry.get("published", "")
                pub_ts = self._parse_pub_ts(entry)
                age_sec = max(0.0, now - pub_ts)

                if title and len(title) > 10:
                    feed_candidates.append({
                        "title": title,
                        "summary": summary,
                        "publisher": name,
                        "source_type": "GEOPOLITICAL_KINETIC",
                        "link": link,
                        "published": published,
                        "published_at": pub_ts,
                        "timestamp": now,
                        "age_sec": age_sec
                    })

            self.last_fetch[name] = now
            self.feed_states[name]["status"] = "HEALTHY"
            self.feed_states[name]["last_success"] = now
            self.feed_states[name]["error_msg"] = None

            # Apply 48-Hour Publication Age Gate
            fresh_items = [item for item in feed_candidates if item["age_sec"] <= self.max_age_seconds]
            if fresh_items:
                return fresh_items
            elif feed_candidates:
                feed_candidates.sort(key=lambda x: x["age_sec"])
                if feed_candidates[0]["age_sec"] <= (72.0 * 3600.0):
                    return [feed_candidates[0]]
            return []
        except Exception as e:
            self.feed_states[name]["status"] = "CONNECTION_ERROR"
            self.feed_states[name]["error_msg"] = str(e)[:50]
            return []

    def fetch_wires(self) -> List[Dict[str, Any]]:
        """Collects latest articles across geopolitical feeds in parallel within the 48-hour gate."""
        import concurrent.futures
        articles = []
        now = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._fetch_single_feed, meta, now) for meta in self.GEOPOLITICAL_FEEDS]
            for fut in concurrent.futures.as_completed(futures):
                try:
                    res = fut.result()
                    if res:
                        articles.extend(res)
                except Exception:
                    pass

        return articles

    def get_health_states(self) -> Dict[str, Any]:
        """Provides status of geopolitical feeds for the UI diagnostics flyout."""
        healthy_count = sum(1 for s in self.feed_states.values() if s["status"] == "HEALTHY")
        return {
            "healthy_count": healthy_count,
            "total_count": len(self.GEOPOLITICAL_FEEDS),
            "states": list(self.feed_states.values())
        }
