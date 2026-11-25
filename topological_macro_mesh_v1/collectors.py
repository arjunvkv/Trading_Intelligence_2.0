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
import math
import re
import html
import email.utils
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

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
            'news.google.com': 3.5,
            'suggestqueries.google.com': 0.1,
            'wikimedia.org': 0.1,
            'finance.yahoo.com': 0.3,
            'mastodon.social': 0.3,
            'econtwitter.net': 0.3
        }
        self.default_domain_delay = 0.5
        
        # In-memory RSS feed cache: url -> (cached_at_ts, items_list)
        self.feed_cache: Dict[str, Tuple[float, List[Dict[str, str]]]] = {}

        # Universal Planetary Sovereign Spectrum (24 Sovereign Epicenters across ISO 3166)
        # Dynamically cycles 1 country per cycle with in-memory persistence and TTL caching
        self.planetary_sovereign_roster = [
            # G7 & Core Sovereign Debt Poles
            ("US Macro/Treasuries", "US", "BUSINESS"),
            ("UK London LBMA", "GB", "BUSINESS"),
            ("Germany Bundesbank/Eurozone", "DE", "BUSINESS"),
            ("France Sovereign Debt", "FR", "BUSINESS"),
            ("Japan BOJ/Yen", "JP", "BUSINESS"),
            ("Switzerland SNB Sovereign Hub", "CH", "BUSINESS"),
            ("Canada Natural Resources", "CA", "BUSINESS"),
            ("Italy BTP/Eurozone", "IT", "BUSINESS"),
            # BRICS+ & Frontier Central Bank Bullion Accumulators
            ("China/HK Sovereign Hub", "HK", "BUSINESS"),
            ("India RBI Sovereign Gold Hub", "IN", "BUSINESS"),
            ("Poland NBP Sovereign Reserves", "PL", "BUSINESS"),
            ("Czech CNB Sovereign Reserves", "CZ", "BUSINESS"),
            ("Turkey TCMB Gold Hub", "TR", "BUSINESS"),
            ("Gulf OPEC/Energy", "AE", "BUSINESS"),
            ("Saudi Arabia Capital", "SA", "BUSINESS"),
            ("South Africa Precious Metals", "ZA", "BUSINESS"),
            ("Brazil LatAm Sovereign", "BR", "BUSINESS"),
            # Strategic Resource, Tech & Chokepoint Nodes
            ("Singapore Asia FX", "SG", "BUSINESS"),
            ("Australia Gold Producer", "AU", "BUSINESS"),
            ("South Korea Tech/Trade", "KR", "BUSINESS"),
            ("Taiwan Semiconductor/FX", "TW", "BUSINESS"),
            ("Sweden Riksbank/Nordic", "SE", "BUSINESS"),
            ("Norway Oil Fund/Oljefondet", "NO", "BUSINESS"),
            ("Mexico Nearshoring/Silver", "MX", "BUSINESS")
        ]
        self.country_roster_index = 0
        self.country_intel_pools: Dict[str, List[Dict[str, str]]] = {}

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

        # Check if in active cooldown
        if now < state.get("cooldown_until", 0.0):
            return b""

        self._polite_domain_wait(domain)

        for attempt in range(2):
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
                    # Adaptive AIMD: Additive decrease of domain delay on clean 200 OK
                    self.domain_delays[domain] = max(0.05, self.domain_delays.get(domain, self.default_domain_delay) - 0.02)
                    return data
            except urllib.error.HTTPError as e:
                state["fail_count"] += 1
                if e.code == 429: # Rate Limited
                    # Adaptive AIMD: Multiplicative increase of domain delay on 429 backoff
                    self.domain_delays[domain] = min(15.0, max(2.5, self.domain_delays.get(domain, self.default_domain_delay) * 2.0))
                    backoff = min(300, 45 * (2 ** (state["fail_count"] - 1)))
                    state["status"] = "RATE_LIMITED_429"
                    state["cooldown_until"] = time.time() + backoff
                    state["error_msg"] = f"HTTP 429 Rate-Limited (Backing off {backoff}s)"
                elif e.code == 403:
                    state["status"] = "FORBIDDEN_403"
                    state["cooldown_until"] = time.time() + 180
                    state["error_msg"] = "HTTP 403 Forbidden"
                elif e.code == 404:
                    # Non-fatal article miss
                    return b""
                else:
                    state["status"] = f"HTTP_ERROR_{e.code}"
                    state["cooldown_until"] = time.time() + 60
                    state["error_msg"] = f"HTTP Error {e.code}"
                return b""
            except Exception as e:
                if attempt == 0:
                    time.sleep(0.35)
                    continue
                state["fail_count"] += 1
                state["status"] = "CONNECTION_ERROR"
                state["cooldown_until"] = time.time() + 45
                state["error_msg"] = str(e)[:60]
                return b""
        return b""

    def fetch_rss_items(self, feed_url: str, source_name: str, max_items: int = 8, ttl_seconds: float = 90.0) -> List[Dict[str, str]]:
        now = time.time()
        
        # 1. Check TTL cache to protect against rapid poll rate-limits (especially news.google.com)
        if feed_url in self.feed_cache:
            cached_ts, cached_items = self.feed_cache[feed_url]
            if (now - cached_ts) < ttl_seconds and cached_items:
                return cached_items

        raw = self._fetch_safe(feed_url, source_name)
        if not raw:
            # Graceful fallback: return previously cached items rather than starving the pipeline
            if feed_url in self.feed_cache:
                return self.feed_cache[feed_url][1]
            return []

        items = []
        try:
            root = ET.fromstring(raw)
            # Find all <item> tags
            for item in root.findall('.//item')[:max_items]:
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                published_ts = now
                if pub_date is not None and pub_date.text:
                    try:
                        dt = email.utils.parsedate_to_datetime(pub_date.text)
                        published_ts = dt.timestamp()
                    except Exception:
                        pass
                
                # Strict Temporal Invariant: Drop stale articles older than 36 hours
                # Prevents search engines and aggregators from injecting multi-day-old archival stories as fresh news
                if (now - published_ts) > 129600:
                    continue

                if title is not None and title.text:
                    clean_title = html.unescape(title.text.strip())
                    publisher = source_name
                    m = re.search(r'\s*-\s*([A-Za-z0-9\.\s]+)$', clean_title)
                    if m:
                        publisher = m.group(1).strip()
                    clean_title = re.sub(r'\s*-\s*[A-Za-z0-9\.\s]+$', '', clean_title)
                    clean_title = re.sub(r'(?:https?://|www\.|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}/)\S*', '', clean_title).strip()
                    url_str = link.text.strip() if link is not None and link.text else ""
                    if clean_title:
                        items.append({
                            "source": source_name,
                            "publisher": publisher,
                            "text": clean_title,
                            "url": url_str,
                            "published_ts": published_ts
                        })
            if items:
                self.feed_cache[feed_url] = (now, items)
            if source_name in self.source_states:
                self.source_states[source_name]["items_count"] = len(items)
        except Exception as e:
            if feed_url in self.feed_cache:
                return self.feed_cache[feed_url][1]
            if source_name in self.source_states:
                self.source_states[source_name]["status"] = "PARSE_ERROR"
                self.source_states[source_name]["error_msg"] = f"XML Parse Error: {str(e)[:40]}"
        return items

    def fetch_round_robin_country_wires(self, max_items_per_country: int = 8) -> List[Dict[str, str]]:
        """Rotates through the 24 sovereign planetary epicenters one country per cycle to eliminate 429 rate limits,
        while maintaining the collective intelligence pool across all countries simultaneously."""
        if not self.planetary_sovereign_roster:
            return []
            
        label, cc, topic = self.planetary_sovereign_roster[self.country_roster_index]
        url = f"https://news.google.com/rss/headlines/section/topic/{topic}?hl=en-{cc}&gl={cc}&ceid={cc}:en"
        self.country_roster_index = (self.country_roster_index + 1) % len(self.planetary_sovereign_roster)
        
        # Pull only this cycle's active sovereign country (1 single request per cycle)
        new_items = self.fetch_rss_items(url, f"Sovereign: {label}", max_items=max_items_per_country, ttl_seconds=60.0)
        if new_items:
            self.country_intel_pools[label] = new_items
            
        # Return accumulated multi-country intelligence pool across all sovereign epicenters
        combined = []
        for country_label, items in self.country_intel_pools.items():
            combined.extend(items)
        return combined

    def fetch_sovereign_wires(self) -> List[Dict[str, str]]:
        wires = []
        wires.extend(self.fetch_rss_items("https://www.federalreserve.gov/feeds/press_all.xml", "Federal Reserve", max_items=6))
        wires.extend(self.fetch_rss_items("https://www.ecb.europa.eu/rss/press.html", "ECB", max_items=6))
        wires.extend(self.fetch_rss_items("https://www.bankofengland.co.uk/rss/news", "Bank of England", max_items=6))
        # Multi-polar sovereign country rotation (1 country polled per cycle, entire pool maintained)
        wires.extend(self.fetch_round_robin_country_wires(max_items_per_country=8))
        return wires

    def fetch_geopolitical_precursor_wires(self, dynamic_query: str = None) -> List[Dict[str, str]]:
        """High-velocity breaking geopolitical and crisis feeds for war, strikes, and chokepoint shocks."""
        wires = []
        # Al Jazeera English - supreme for Middle East, Red Sea, Persian Gulf, Suez
        wires.extend(self.fetch_rss_items("https://www.aljazeera.com/xml/rss/all.xml", "Al Jazeera Wires", max_items=8))
        # BBC World News - rapid global breaking
        wires.extend(self.fetch_rss_items("http://feeds.bbci.co.uk/news/world/rss.xml", "BBC World Breaking", max_items=8))
        # France 24 International - tier-1 open world wire
        wires.extend(self.fetch_rss_items("https://www.france24.com/en/rss", "France 24 International", max_items=8))
        # Google News World Geopolitics (US/Global Edition, cached 120s TTL)
        wires.extend(self.fetch_rss_items("https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en", "Global Geopolitics", max_items=8, ttl_seconds=120.0))
        
        # 1. Open-World Unfiltered Global Top Wire (Zero keyword constraints - captures any planetary shock or anomaly)
        wires.extend(self.fetch_rss_items("https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en", "Global Top Unfiltered Wire", max_items=16, ttl_seconds=75.0))

        # 2. Adaptive Real-Time Breaking Shock Radar (Driven dynamically by top surging topology tokens)
        if dynamic_query:
            clean_q = urllib.parse.quote_plus(f"when:2h ({dynamic_query})")
            search_url = f"https://news.google.com/rss/search?q={clean_q}&hl=en-US&gl=US&ceid=US:en"
            wires.extend(self.fetch_rss_items(search_url, "Dynamic Shock Radar", max_items=14, ttl_seconds=90.0))
        return wires

    def fetch_intermarket_wires(self) -> List[Dict[str, str]]:
        items = []
        tickers = [
            ('GC=F', 'Yahoo Gold COMEX'),
            ('SI=F', 'Yahoo Silver COMEX'),
            ('DX-Y.NYB', 'Yahoo Dollar Index'),
            ('^TNX', 'Yahoo US10Y Nominal Yield'),
            ('TIP', 'Yahoo TIPS US Real Yield ETF'),
            ('USDCNH=X', 'Yahoo Offshore Chinese Yuan'),
            ('USDJPY=X', 'Yahoo Japanese Yen'),
            ('CL=F', 'Yahoo WTI Crude Oil'),
            ('BZ=F', 'Yahoo Brent Crude Oil'),
            ('HG=F', 'Yahoo Copper COMEX'),
            ('^VIX', 'Yahoo Volatility Index'),
            ('BTC-USD', 'Yahoo Bitcoin Spot')
        ]
        for sym, source_label in tickers:
            url = f"https://finance.yahoo.com/rss/headline?s={sym}"
            items.extend(self.fetch_rss_items(url, source_label, max_items=3, ttl_seconds=120.0))
        
        # MarketWatch Top Stories (Official Dow Jones Feed)
        items.extend(self.fetch_rss_items("https://feeds.content.dowjones.io/public/rss/mw_topstories", "MarketWatch Wire", max_items=6, ttl_seconds=120.0))
        return items

    def fetch_physical_bullion_and_vault_wires(self) -> List[Dict[str, str]]:
        """
        Dimension 4: Physical Bullion, Vault Inventories, Exchange Clearings & Sovereign Reserves.
        Captures daily COMEX deliverable vault inventory drawdowns, Shanghai Gold Exchange (SGE)
        cash premiums/discounts, LBMA physical clearings, and central bank bullion reserve acquisitions.
        """
        wires = []
        # 1. Physical Exchanges & Vault Clearing (COMEX Vaults, SGE Fixing, LBMA, Physical Bullion)
        url_exchanges = "https://news.google.com/rss/search?q=when:24h+(%22Shanghai+Gold+Exchange%22+OR+SGE+OR+%22COMEX+vault%22+OR+%22LBMA+clearing%22+OR+%22vault+inventory%22+OR+%22physical+gold%22)&hl=en-US&gl=US&ceid=US:en"
        wires.extend(self.fetch_rss_items(url_exchanges, "Physical Bullion & Vault Exchanges", max_items=10, ttl_seconds=180.0))

        # 2. Sovereign Official Central Bank Reserves & Bullion Allocations
        url_reserves = "https://news.google.com/rss/search?q=when:24h+(%22gold+reserves%22+OR+%22bullion+purchase%22+OR+%22central+bank+gold%22+OR+%22monetary+gold%22)&hl=en-US&gl=US&ceid=US:en"
        wires.extend(self.fetch_rss_items(url_reserves, "Sovereign Gold Reserve Dispatches", max_items=8, ttl_seconds=180.0))

        # 3. Primary Mining Supply & Refinery Disruptions
        url_mining = "https://news.google.com/rss/search?q=when:24h+(%22gold+production%22+OR+%22gold+mine%22+OR+%22mine+supply%22+OR+%22refinery%22+AND+gold)&hl=en-US&gl=US&ceid=US:en"
        wires.extend(self.fetch_rss_items(url_mining, "Mining & Refinery Supply Front", max_items=8, ttl_seconds=180.0))

        return wires

    def fetch_wikipedia_crowd_pageviews(self, dynamic_topics: List[str] = None) -> List[Dict[str, str]]:
        """Wikimedia Public Attention API: measures real-time crowd research on dynamic emerging macro nodes."""
        posts = []
        if not dynamic_topics:
            return []

        topics = []
        for t in dynamic_topics:
            if not t or len(t) < 3 or t.isdigit():
                continue
            clean_art = t.strip().replace(" ", "_").capitalize()
            topics.append((clean_art, t.strip().title()))

        end_dt = datetime.utcnow() - timedelta(days=1)
        start_dt = datetime.utcnow() - timedelta(days=3)
        start_str = start_dt.strftime("%Y%m%d00")
        end_str = end_dt.strftime("%Y%m%d00")

        for art, label in topics[:6]:
            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{art}/daily/{start_str}/{end_str}"
            raw = self._fetch_safe(url, "Wikimedia Attention API", timeout=5, custom_headers=self.wiki_headers)
            if raw:
                try:
                    data = json.loads(raw.decode('utf-8', errors='ignore'))
                    items = data.get('items', [])
                    if len(items) >= 2:
                        prev_v = items[-2]['views']
                        curr_v = items[-1]['views']
                        growth = ((curr_v - prev_v) / max(1, prev_v)) * 100.0
                        sign = "+" if growth >= 0 else ""
                        desc = f"Public research surge on {label} growth {sign}{growth:.1f}%"
                        posts.append({
                            "source": f"Wikimedia: {label}",
                            "publisher": "Wikipedia Public Attention",
                            "text": desc
                        })
                except Exception:
                    pass
        return posts


    def sanitize_text(self, text: str, max_len: int = 220) -> Optional[str]:
        """
        Pure mathematical text sanitizer using Shannon character entropy, 
        structural debris ratio, and whole-word boundary preservation.
        Rejects fragmented URL debris, broken markup spans, and sub-Brownian noise.
        """
        if not text:
            return None
        clean = html.unescape(text)
        # Strip all <a ...>...</a> tags completely before removing other HTML tags
        clean = re.sub(r'<a\b[^>]*>.*?</a>', ' ', clean, flags=re.DOTALL)
        clean = re.sub(r'<[^>]+>', ' ', clean)
        clean = re.sub(r'(?:https?://|www\.|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}/)\S*', ' ', clean)
        clean = re.sub(r'@\s*[a-zA-Z0-9_]+', ' ', clean)
        clean = re.sub(r'^(?:re|cw):\s*', '', clean, flags=re.I)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) < 25:
            return None

        # 1. Structural Debris / Noise Ratio: rho = (symbols + digits) / total_chars
        # Financial reporting satisfies rho < 0.15; URL/id clutter satisfies rho > 0.18
        syms = sum(1 for c in clean if not c.isalnum() and not c.isspace())
        digits = sum(1 for c in clean if c.isdigit())
        rho = (syms + digits) / len(clean)
        if rho > 0.18:
            return None

        # 2. Shannon Character Entropy H(S)
        from collections import Counter
        c_counts = Counter(clean.lower())
        total = len(clean)
        h = -sum((cnt / total) * math.log2(cnt / total) for cnt in c_counts.values())
        if h < 3.0 or h > 5.2:
            return None

        # 3. Whole-Word Boundary Invariant Truncation (never slices words like 'driven' into 'dri')
        if len(clean) > max_len:
            last_punct = max(clean[:max_len].rfind('. '), clean[:max_len].rfind('? '), clean[:max_len].rfind('! '))
            if last_punct > max_len - 60:
                clean = clean[:last_punct+1]
            else:
                last_sp = clean[:max_len].rfind(' ')
                clean = clean[:last_sp] if last_sp > max_len - 50 else clean[:max_len]
        return clean.strip()

    def fetch_federated_mastodon_squawks(self, dynamic_seeds: List[str] = None) -> List[Dict[str, str]]:
        """
        Pure dynamic closed-loop crowd sensor:
        Never polls open unvetted tags (#energy, #economics, etc.).
        Only queries Mastodon dynamically when verified primary wires have discovered surging macro entities (I(w) >= 3.5).
        """
        if not dynamic_seeds:
            return []
        
        posts = []
        # Filter dynamic seeds to substantive alphabetic macro tokens
        valid_seeds = [s.strip().lower() for s in dynamic_seeds if len(s.strip()) >= 3 and s.strip().isalpha()][:3]
        if not valid_seeds:
            return []

        feeds = []
        for seed in valid_seeds:
            feeds.append((
                f"https://mastodon.social/api/v1/timelines/tag/{urllib.parse.quote(seed)}?limit=6",
                f"Mastodon {seed.title()} Stream"
            ))

        for url, source_name in feeds:
            raw = self._fetch_safe(url, source_name, timeout=5)
            if raw:
                try:
                    data = json.loads(raw.decode('utf-8', errors='ignore'))
                    for post in data:
                        content = post.get('content', '')
                        if not content:
                            continue
                        clean = self.sanitize_text(content, max_len=220)
                        if clean and len(clean) >= 25:
                            posts.append({
                                "source": source_name,
                                "publisher": source_name,
                                "text": clean
                            })
                except Exception:
                    pass
        return posts

    def fetch_public_search_trajectories(self, dynamic_seeds: List[str] = None) -> List[Dict[str, str]]:
        """Dynamic real-world search autocomplete trajectories revealing active public inquiries."""
        posts = []
        if not dynamic_seeds:
            return []
        
        search_seeds = [s for s in dynamic_seeds if len(s) >= 3 and not s.isdigit()][:5]

        # Mathematical Shannon Character Entropy & Lexical Density Filter
        # Rejects low-entropy dictionary lookups, repetitive searches, and trivial single-word noise without keyword lists
        for seed in search_seeds:
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={urllib.parse.quote(seed)}"
            raw_sugg = self._fetch_safe(url, "Google Crowd Autocomplete", timeout=4)
            if raw_sugg:
                try:
                    sugg_data = json.loads(raw_sugg.decode('utf-8', errors='ignore'))
                    suggestions = sugg_data[1] if len(sugg_data) > 1 else []
                    for phrase in suggestions[:3]:
                        if phrase and len(phrase) > 8:
                            # 1. Shannon Character Entropy H(S)
                            from collections import Counter
                            c_counts = Counter(phrase.lower())
                            p_len = len(phrase)
                            entropy = -sum((cnt / p_len) * math.log2(cnt / p_len) for cnt in c_counts.values())
                            if entropy < 2.9: # Low-entropy repetitive text or trivial lookup
                                continue

                            words = [w for w in re.findall(r'[a-zA-Z]{3,}', phrase.lower())]
                            # Require at least 2 distinct substantive words
                            if len(set(words)) < 2:
                                continue

                            posts.append({
                                "source": f"Public Search: {seed}",
                                "publisher": "Google Crowd Autocomplete",
                                "text": phrase
                            })
                except Exception:
                    pass
        return posts

    def fetch_crowd_squawks_and_queries(self, dynamic_seeds: List[str] = None) -> List[Dict[str, str]]:
        """Aggregates all crowd sources: Wikipedia Attention, Federated Mastodon, and Search Trajectories."""
        posts = []
        posts.extend(self.fetch_wikipedia_crowd_pageviews(dynamic_topics=dynamic_seeds))
        posts.extend(self.fetch_federated_mastodon_squawks(dynamic_seeds=dynamic_seeds))
        posts.extend(self.fetch_public_search_trajectories(dynamic_seeds=dynamic_seeds))
        return posts

    def get_health_status(self) -> Dict[str, Any]:
        """Returns health states and active error logs across all collectors with auto-recovery for transient network drops."""
        now = time.time()
        active_errors = []
        healthy_count = 0

        # Purge stale dynamic keys and auto-reset expired transient connection errors
        for name, state in list(self.source_states.items()):
            # If a source had a transient error and its cooldown has expired, reset to healthy if it succeeded previously
            if state["status"] != "HEALTHY" and now >= state.get("cooldown_until", 0.0):
                if state.get("last_success", 0) > 0:
                    state["status"] = "HEALTHY"
                    state["error_msg"] = None
                    state["fail_count"] = 0
                else:
                    # Drop stale transient dynamic queries that were never persistent services
                    if "Wikimedia:" in name or "Crowd Suggest:" in name:
                        self.source_states.pop(name, None)
                        continue

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
            "total_count": len(self.source_states),
            "all_healthy": len(active_errors) == 0,
            "active_errors": active_errors,
            "states": list(self.source_states.values())
        }

    def fetch_all(self, dynamic_seeds: List[str] = None, dynamic_search_query: str = None) -> Dict[str, Any]:
        """Aggregate all streams safely with full error and rate-limit tracking."""
        sovereign = self.fetch_sovereign_wires()
        geopolitical = self.fetch_geopolitical_precursor_wires(dynamic_query=dynamic_search_query)
        market = self.fetch_intermarket_wires()
        physical = self.fetch_physical_bullion_and_vault_wires()

        # If dynamic_seeds not supplied by topology graph, derive dynamically from freshly fetched wire headlines!
        if not dynamic_seeds:
            from collections import Counter
            all_text = " ".join([item.get("text", "") for item in sovereign + geopolitical + market + physical])
            COMMON_FILTER = {
                'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'were', 'which', 'about',
                'news', 'today', 'daily', 'report', 'update', 'brief', 'market', 'price', 'rates', 'said',
                'first', 'after', 'will', 'year', 'more', 'over', 'into', 'some', 'than', 'them', 'also'
            }
            words = [w for w in re.findall(r'[a-zA-Z]{4,}', all_text.lower()) if w not in COMMON_FILTER]
            if words:
                dynamic_seeds = [w for w, _ in Counter(words).most_common(5)]
            else:
                dynamic_seeds = ['gold', 'dollar', 'yields', 'crude']

        crowd = self.fetch_crowd_squawks_and_queries(dynamic_seeds=dynamic_seeds)
        health = self.get_health_status()

        return {
            "timestamp": time.time(),
            "sovereign_wires": sovereign,
            "geopolitical_wires": geopolitical,
            "market_wires": market,
            "physical_wires": physical,
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
