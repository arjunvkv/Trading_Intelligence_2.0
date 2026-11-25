"""
SOVEREIGN WIRES COLLECTOR (CENTRAL BANKS & TREASURY PLUMBING)
Fetches official sovereign debt, reserve releases, interest rate decisions,
and bilateral currency swap announcements across 24 sovereign jurisdictions.
Includes full collector health diagnostics.
"""

import time
import urllib.request
import ssl
import feedparser
from typing import List, Dict, Any

class SovereignWiresCollector:
    SOVEREIGN_FEEDS = [
        {"name": "Federal Reserve Board", "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
        {"name": "Federal Reserve Monetary Policy", "url": "https://www.federalreserve.gov/feeds/press_monetary.xml"},
        {"name": "European Central Bank", "url": "https://www.ecb.europa.eu/rss/press.html"},
        {"name": "Bank of England News", "url": "https://www.bankofengland.co.uk/rss/news"},
        {"name": "Bank of Japan Releases", "url": "https://news.google.com/rss/search?q=%22Bank+of+Japan%22+OR+%22Kazuo+Ueda%22+OR+%22BOJ+policy+rate%22+OR+%22yen+carry+trade%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Bank for International Settlements BIS", "url": "https://news.google.com/rss/search?q=%22Bank+for+International+Settlements%22+OR+%22BIS+bulletin%22+OR+%22Basel+Committee%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "International Monetary Fund IMF", "url": "https://news.google.com/rss/search?q=%22International+Monetary+Fund%22+OR+%22IMF+bailout%22+OR+%22SDR+reserves%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "People's Bank of China / Macro Wires", "url": "https://news.google.com/rss/search?q=PBOC+OR+%22People%27s+Bank+of+China%22+OR+%22State+Administration+of+Foreign+Exchange%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Reserve Bank of India Sovereign", "url": "https://news.google.com/rss/search?q=%22Reserve+Bank+of+India%22+OR+%22RBI+monetary+policy%22+OR+%22forex+reserves%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Swiss National Bank SNB", "url": "https://news.google.com/rss/search?q=%22Swiss+National+Bank%22+OR+%22SNB+policy+rate%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Bank of Canada", "url": "https://news.google.com/rss/search?q=%22Bank+of+Canada%22+OR+%22BoC+interest+rate%22+OR+%22Tiff+Macklem%22+when:2d&hl=en-CA&gl=CA&ceid=CA:en"},
        {"name": "Reserve Bank of Australia", "url": "https://news.google.com/rss/search?q=%22Reserve+Bank+of+Australia%22+OR+%22RBA+cash+rate%22+OR+%22Michele+Bullock%22+when:2d&hl=en-AU&gl=AU&ceid=AU:en"},
        {"name": "Deutsche Bundesbank / Eurozone", "url": "https://news.google.com/rss/search?q=%22Bundesbank%22+OR+%22German+Bunds%22+OR+%22BTP+spread%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Monetary Authority of Singapore MAS", "url": "https://news.google.com/rss/search?q=%22Monetary+Authority+of+Singapore%22+OR+%22MAS+monetary+policy%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "US Treasury Debt & Auctions", "url": "https://news.google.com/rss/search?q=%22US+Treasury%22+OR+%22Treasury+auction%22+OR+%22bid-to-cover%22+OR+%22Treasury+yields%22+OR+%22debt+ceiling%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Global Sovereign FX Reserves & Swaps", "url": "https://news.google.com/rss/search?q=%22foreign+exchange+reserves%22+OR+%22bilateral+swap+line%22+OR+%22sovereign+debt+default%22+OR+%22de-dollarization%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Central Bank Liquidity Facilities", "url": "https://news.google.com/rss/search?q=%22reverse+repo%22+OR+%22discount+window%22+OR+%22liquidity+facility%22+OR+%22emergency+lending%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "BRICS & De-Dollarization Architecture", "url": "https://news.google.com/rss/search?q=%22BRICS+Pay%22+OR+%22cross-border+settlement%22+OR+%22alternative+currency%22+OR+%22mBridge%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Emirates News Agency WAM Sovereign", "url": "https://news.google.com/rss/search?q=%22Emirates+News+Agency%22+OR+site:wam.ae+OR+%22UAE+central+bank%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Saudi Press Agency SPA Energy Desk", "url": "https://news.google.com/rss/search?q=%22Saudi+Press+Agency%22+OR+site:spa.gov.sa+OR+%22Saudi+Aramco%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "OECD Sovereign Debt & Borrowing", "url": "https://news.google.com/rss/search?q=%22OECD%22+OR+%22sovereign+borrowing%22+OR+%22global+debt+outlook%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Global Gold & Bullion Vaults", "url": "https://news.google.com/rss/search?q=%22spot+gold%22+OR+%22gold+reserves%22+OR+%22central+bank+gold+buying%22+OR+%22XAUUSD%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "US Fiscal Dominance & Debt Issuance", "url": "https://news.google.com/rss/search?q=%22US+Treasury+auction%22+OR+%22fiscal+deficit%22+OR+%22debt+issuance%22+OR+%22term+premium%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Bilateral Settlements & Reserve Assets", "url": "https://news.google.com/rss/search?q=%22bilateral+settlement%22+OR+%22local+currencies%22+OR+%22de-dollarization%22+OR+%22reserve+diversification%22+when:2d&hl=en-US&gl=US&ceid=US:en"},
        {"name": "China Sovereign Macro & Liquidity", "url": "https://news.google.com/rss/search?q=%22China+macro%22+OR+%22PBOC+liquidity%22+OR+%22China+bonds%22+OR+%22yuan+devaluation%22+when:2d&hl=en-US&gl=US&ceid=US:en"}
    ]

    def __init__(self, request_timeout: float = 6.0):
        self.request_timeout = request_timeout
        self.last_fetch: Dict[str, float] = {}
        self.feed_states: Dict[str, Dict[str, Any]] = {}
        self.cooldown_sec = 10.0
        self.max_age_seconds = 48.0 * 3600.0  # 48-Hour Publication Age Gate

    def _parse_pub_ts(self, entry: Dict[str, Any]) -> float:
        """Extracts true UTC unix timestamp from entry published_parsed, updated_parsed, or published string."""
        now = time.time()
        parsed_time = entry.get("published_parsed") or entry.get("updated_parsed")
        if parsed_time:
            try:
                import calendar
                return float(calendar.timegm(parsed_time))
            except Exception:
                pass
        pub_raw = entry.get("published", "") or entry.get("updated", "")
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

        # Cooldown check
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
                        "source_type": "SOVEREIGN_CENTRAL_BANK",
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
                if feed_candidates[0]["age_sec"] <= (96.0 * 3600.0):
                    return [feed_candidates[0]]
            return []
        except Exception as e:
            self.feed_states[name]["status"] = "CONNECTION_ERROR"
            self.feed_states[name]["error_msg"] = str(e)[:50]
            return []

    def fetch_wires(self) -> List[Dict[str, Any]]:
        """Collects latest articles across sovereign financial feeds in parallel within the 48-hour gate."""
        import concurrent.futures
        articles = []
        now = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._fetch_single_feed, meta, now) for meta in self.SOVEREIGN_FEEDS]
            for fut in concurrent.futures.as_completed(futures):
                try:
                    res = fut.result()
                    if res:
                        articles.extend(res)
                except Exception:
                    pass

        return articles

    def get_health_states(self) -> Dict[str, Any]:
        """Provides status of sovereign feeds for the UI diagnostics flyout."""
        healthy_count = sum(1 for s in self.feed_states.values() if s["status"] == "HEALTHY")
        return {
            "healthy_count": healthy_count,
            "total_count": len(self.SOVEREIGN_FEEDS),
            "states": list(self.feed_states.values())
        }
