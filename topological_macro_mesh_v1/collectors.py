"""
COLLECTORS MODULE (RATE-LIMIT PROTECTED MULTI-SOURCE INTELLIGENCE)
Features:
- Rate-limit protection with exponential backoff and domain-level jitter
- Transparent error and status logging for every source
- Expanded sovereign, geopolitical, intermarket, and crowd precursors
- Zero crash on 429/403/timeout: marks source in cooldown and proceeds
"""

import ssl
import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DataCollector:
    def __init__(self):
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        self.wiki_headers = {
            'User-Agent': 'MacroMeshIntelligenceBot/2.0 (sovereign macro research desk; contact@tradingmesh.internal)',
            'Accept': 'application/json'
        }
        
        # Track health, errors, and backoff per source
        self.source_states: Dict[str, Dict[str, Any]] = {}
        
        # Rate-limiting tracker: domain -> last request timestamp
        self.domain_last_request: Dict[str, float] = {}
        # Domain-specific delays (strict on Google News, fast on open high-throughput CDNs)
        self.domain_delays: Dict[str, float] = {
            'news.google.com': 2.5,
            'suggestqueries.google.com': 0.1,
            'wikimedia.org': 0.1,
            'finance.yahoo.com': 0.3,
            'mastodon.social': 0.3,
            'econtwitter.net': 0.3
        }
        self.default_domain_delay = 0.5

    def _get_domain(self, url: str) -> str:
        try:
            return urllib.parse.urlparse(url).netloc
        except Exception:
            return "unknown"

    def _polite_domain_wait(self, domain: str):
        now = time.time()
        delay = self.domain_delays.get(domain, self.default_domain_delay)
        last = self.domain_last_request.get(domain, 0.0)
        elapsed = now - last
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.domain_last_request[domain] = time.time()

    def _fetch_safe(self, url: str, source_name: str, timeout: int = 6, custom_headers: Dict[str, str] = None) -> bytes:
        now = time.time()
        domain = self._get_domain(url)
        
        # Initialize state if needed
        if source_name not in self.source_states:
            self.source_states[source_name] = {
                "source": source_name,
                "domain": domain,
                "status": "HEALTHY",
                "last_success": 0.0,
                "last_attempt": now,
                "error_msg": None,
                "fail_count": 0,
                "cooldown_until": 0.0,
                "items_count": 0
            }

        state = self.source_states[source_name]
        state["last_attempt"] = now

        # Check if in cooldown
        if now < state.get("cooldown_until", 0.0):
            rem = int(state["cooldown_until"] - now)
            # Source is currently cooling down
            return b""

        self._polite_domain_wait(domain)

        try:
            req_headers = custom_headers if custom_headers is not None else self.headers
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=timeout) as resp:
                data = resp.read()
                state["status"] = "HEALTHY"
                state["last_success"] = time.time()
                state["error_msg"] = None
                state["fail_count"] = 0
                state["cooldown_until"] = 0.0
                return data
        except urllib.error.HTTPError as e:
            state["fail_count"] += 1
            if e.code == 429: # Rate Limited!
                backoff = min(600, 60 * (2 ** (state["fail_count"] - 1)))
                state["status"] = "RATE_LIMITED_429"
                state["cooldown_until"] = time.time() + backoff
                state["error_msg"] = f"HTTP 429 Rate-Limited (Backing off {backoff}s)"
            elif e.code == 403:
                state["status"] = "FORBIDDEN_403"
                state["cooldown_until"] = time.time() + 300
                state["error_msg"] = "HTTP 403 Forbidden / Walled Garden"
            elif e.code == 404:
                state["status"] = "NOT_FOUND_404"
                state["cooldown_until"] = time.time() + 300
                state["error_msg"] = "HTTP 404 Resource Moved or Not Found"
            else:
                state["status"] = f"HTTP_ERROR_{e.code}"
                state["cooldown_until"] = time.time() + 120
                state["error_msg"] = f"HTTP Error {e.code}"
            return b""
        except Exception as e:
            state["fail_count"] += 1
            state["status"] = "CONNECTION_ERROR"
            state["cooldown_until"] = time.time() + 60
            state["error_msg"] = str(e)[:60]
            return b""

    def fetch_rss_items(self, feed_url: str, source_name: str, max_items: int = 8) -> List[Dict[str, str]]:
        raw = self._fetch_safe(feed_url, source_name)
        if not raw:
            return []
        items = []
        try:
            root = ET.fromstring(raw)
            # Find all <item> tags
            for item in root.findall('.//item')[:max_items]:
                title = item.find('title')
                link = item.find('link')
                if title is not None and title.text:
                    clean_title = title.text.strip()
                    publisher = source_name
                    m = re.search(r'\s*-\s*([A-Za-z0-9\.\s]+)$', clean_title)
                    if m:
                        publisher = m.group(1).strip()
                    clean_title = re.sub(r'\s*-\s*[A-Za-z0-9\.\s]+$', '', clean_title)
                    url_str = link.text.strip() if link is not None and link.text else ""
                    if clean_title:
                        items.append({
                            "source": source_name,
                            "publisher": publisher,
                            "text": clean_title,
                            "url": url_str
                        })
            if source_name in self.source_states:
                self.source_states[source_name]["items_count"] = len(items)
        except Exception as e:
            if source_name in self.source_states:
                self.source_states[source_name]["status"] = "PARSE_ERROR"
                self.source_states[source_name]["error_msg"] = f"XML Parse Error: {str(e)[:40]}"
        return items

    def fetch_sovereign_wires(self) -> List[Dict[str, str]]:
        wires = []
        wires.extend(self.fetch_rss_items("https://www.federalreserve.gov/feeds/press_all.xml", "Federal Reserve", max_items=6))
        wires.extend(self.fetch_rss_items("https://www.ecb.europa.eu/rss/press.html", "ECB", max_items=6))
        wires.extend(self.fetch_rss_items("https://www.bankofengland.co.uk/rss/news", "Bank of England", max_items=6))
        return wires

    def fetch_geopolitical_precursor_wires(self) -> List[Dict[str, str]]:
        """High-velocity breaking geopolitical and crisis feeds for war, strikes, and chokepoint shocks."""
        wires = []
        # Al Jazeera English - supreme for Middle East, Red Sea, Persian Gulf, Suez
        wires.extend(self.fetch_rss_items("https://www.aljazeera.com/xml/rss/all.xml", "Al Jazeera Wires", max_items=8))
        # BBC World News - rapid global breaking
        wires.extend(self.fetch_rss_items("http://feeds.bbci.co.uk/news/world/rss.xml", "BBC World Breaking", max_items=8))
        # Google News World Geopolitics
        wires.extend(self.fetch_rss_items("https://news.google.com/rss/headlines/section/topic/WORLD", "Global Geopolitics", max_items=8))
        # Google News Real-time 1-hour Breaking Conflict & Macro Shock Search (Unified)
        wires.extend(self.fetch_rss_items(
            "https://news.google.com/rss/search?q=when:1h+(gold+OR+dollar+OR+yields+OR+treasury+OR+strike+OR+iran+OR+ukraine+OR+tariffs+OR+fed+OR+inflation+OR+debt+OR+crude+OR+opec)&hl=en-US&gl=US&ceid=US:en",
            "Realtime Conflict & Macro Wires",
            max_items=16
        ))
        return wires

    def fetch_intermarket_wires(self) -> List[Dict[str, str]]:
        items = []
        tickers = [
            ('GC=F', 'Yahoo Gold COMEX'),
            ('DX-Y.NYB', 'Yahoo Dollar Index'),
            ('^TNX', 'Yahoo US10Y Yield'),
            ('CL=F', 'Yahoo Crude Oil')
        ]
        for sym, source_label in tickers:
            url = f"https://finance.yahoo.com/rss/headline?s={sym}"
            items.extend(self.fetch_rss_items(url, source_label, max_items=4))
        
        # MarketWatch Top Stories (Official Dow Jones Feed)
        items.extend(self.fetch_rss_items("https://feeds.content.dowjones.io/public/rss/mw_topstories", "MarketWatch Wire", max_items=6))
        # Google Business Macro
        items.extend(self.fetch_rss_items("https://news.google.com/rss/headlines/section/topic/BUSINESS", "Global Business Wire", max_items=8))
        return items

    def fetch_wikipedia_crowd_pageviews(self) -> List[Dict[str, str]]:
        """Wikimedia Public Attention API: measures real-time crowd research on sovereign & crisis nodes."""
        posts = []
        articles = [
            ("Strait_of_Hormuz", "Hormuz Chokepoint"),
            ("Bab-el-Mandeb", "Bab el-Mandeb Chokepoint"),
            ("Gold_as_an_investment", "Gold Reserve Demand"),
            ("Federal_Reserve", "Federal Reserve Liquidity"),
            ("Red_Sea_crisis", "Red Sea Disruption"),
            ("Sovereign_debt", "Sovereign Debt Risk"),
            ("Inflation", "Inflationary Pressure")
        ]

        end_dt = datetime.utcnow() - timedelta(days=1)
        start_dt = datetime.utcnow() - timedelta(days=3)
        start_str = start_dt.strftime("%Y%m%d00")
        end_str = end_dt.strftime("%Y%m%d00")

        for art, label in articles:
            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{art}/daily/{start_str}/{end_str}"
            raw = self._fetch_safe(url, f"Wikimedia: {label}", timeout=5, custom_headers=self.wiki_headers)
            if raw:
                try:
                    data = json.loads(raw.decode('utf-8', errors='ignore'))
                    items = data.get('items', [])
                    if len(items) >= 2:
                        prev_v = items[-2]['views']
                        curr_v = items[-1]['views']
                        growth = ((curr_v - prev_v) / max(1, prev_v)) * 100.0
                        sign = "+" if growth >= 0 else ""
                        desc = f"Wikipedia Public Research Pulse: {label} ({curr_v:,} daily inquiries, {sign}{growth:.1f}% velocity)"
                        posts.append({
                            "source": f"Wikimedia: {label}",
                            "publisher": "Wikipedia Public Attention",
                            "text": desc
                        })
                except Exception:
                    pass
        return posts

    def fetch_federated_mastodon_squawks(self) -> List[Dict[str, str]]:
        """Multi-instance federated open squawks across academic economics, energy, and geopolitics."""
        posts = []
        feeds = [
            ("https://econtwitter.net/api/v1/timelines/tag/economics?limit=6", "EconTwitter Academic Desk"),
            ("https://mastodon.social/api/v1/timelines/tag/economics?limit=6", "Mastodon Macro Desk"),
            ("https://mastodon.social/api/v1/timelines/tag/geopolitics?limit=6", "Mastodon Geopolitics Desk"),
            ("https://mastodon.social/api/v1/timelines/tag/energy?limit=6", "Mastodon Energy Desk"),
            ("https://mastodon.social/api/v1/timelines/tag/inflation?limit=6", "Mastodon Debasement Desk")
        ]

        for url, source_name in feeds:
            raw = self._fetch_safe(url, source_name, timeout=5)
            if raw:
                try:
                    data = json.loads(raw.decode('utf-8', errors='ignore'))
                    for post in data:
                        content = post.get('content', '')
                        clean = re.sub(r'<[^>]+>', '', content).strip()
                        if clean and len(clean) > 20:
                            posts.append({
                                "source": source_name,
                                "publisher": source_name,
                                "text": clean[:180]
                            })
                except Exception:
                    pass
        return posts

    def fetch_public_search_trajectories(self) -> List[Dict[str, str]]:
        """Dynamic real-world search autocomplete trajectories revealing active public inquiries."""
        posts = []
        search_seeds = [
            'why is gold', 'why is dollar', 'hormuz', 'airspace', 
            'sanctions', 'bank liquidity', 'treasury yields', 
            'crude oil supply', 'central bank gold', 'red sea shipping'
        ]
        for seed in search_seeds:
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={urllib.parse.quote(seed)}"
            raw_sugg = self._fetch_safe(url, f"Crowd Suggest: {seed}", timeout=4)
            if raw_sugg:
                try:
                    sugg_data = json.loads(raw_sugg.decode('utf-8', errors='ignore'))
                    for phrase in sugg_data[1][:3]:
                        if phrase and len(phrase) > 8:
                            posts.append({
                                "source": f"Public Search: {seed}",
                                "publisher": "Google Crowd Autocomplete",
                                "text": phrase
                            })
                except Exception:
                    pass
        return posts

    def fetch_crowd_squawks_and_queries(self) -> List[Dict[str, str]]:
        """Aggregates all crowd sources: Wikipedia Attention, Federated Mastodon, and Search Trajectories."""
        posts = []
        posts.extend(self.fetch_wikipedia_crowd_pageviews())
        posts.extend(self.fetch_federated_mastodon_squawks())
        posts.extend(self.fetch_public_search_trajectories())
        return posts

    def get_health_status(self) -> Dict[str, Any]:
        """Returns health states and active error logs across all collectors."""
        now = time.time()
        active_errors = []
        healthy_count = 0
        total_count = len(self.source_states)

        for name, state in self.source_states.items():
            is_healthy = (state["status"] == "HEALTHY")
            if is_healthy:
                healthy_count += 1
            else:
                rem = max(0, int(state.get("cooldown_until", 0.0) - now))
                active_errors.append({
                    "source": name,
                    "status": state["status"],
                    "error": state.get("error_msg", "Unknown error"),
                    "cooldown_remaining_sec": rem
                })

        return {
            "healthy_count": healthy_count,
            "total_count": total_count,
            "all_healthy": len(active_errors) == 0,
            "active_errors": active_errors,
            "states": list(self.source_states.values())
        }

    def fetch_all(self) -> Dict[str, Any]:
        """Aggregate all streams safely with full error and rate-limit tracking."""
        sovereign = self.fetch_sovereign_wires()
        geopolitical = self.fetch_geopolitical_precursor_wires()
        market = self.fetch_intermarket_wires()
        crowd = self.fetch_crowd_squawks_and_queries()
        health = self.get_health_status()

        return {
            "timestamp": time.time(),
            "sovereign_wires": sovereign,
            "geopolitical_wires": geopolitical,
            "market_wires": market,
            "crowd_discussions": crowd,
            "collector_health": health
        }

if __name__ == "__main__":
    print("Testing Rate-Limit Protected Multi-Source Collectors...")
    c = DataCollector()
    res = c.fetch_all()
    print(f"Collected:")
    print(f"  • Sovereign: {len(res['sovereign_wires'])} items")
    print(f"  • Geopolitical Precursors: {len(res['geopolitical_wires'])} items")
    print(f"  • Intermarket: {len(res['market_wires'])} items")
    print(f"  • Crowd Queries & Squawks: {len(res['crowd_discussions'])} items")
    health = res["collector_health"]
    print(f"Health: {health['healthy_count']}/{health['total_count']} healthy")
    if health["active_errors"]:
        print(f"Active Errors/Rate Limits:")
        for err in health["active_errors"]:
            print(f"  [ALERT] {err['source']}: {err['error']} ({err['cooldown_remaining_sec']}s cooldown)")
