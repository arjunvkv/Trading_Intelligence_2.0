"""
SOVEREIGN WIRES COLLECTOR (CENTRAL BANKS & TREASURY PLUMBING)
Fetches official sovereign debt, reserve releases, interest rate decisions,
and bilateral currency swap announcements across 24 sovereign jurisdictions.
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
        {"name": "Bank of Japan Releases", "url": "https://www.boj.or.jp/en/rss/whatsnew.xml"},
        {"name": "People's Bank of China / Macro Wires", "url": "https://news.google.com/rss/search?q=PBOC+OR+%22People%27s+Bank+of+China%22+OR+%22State+Administration+of+Foreign+Exchange%22&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Reserve Bank of India Sovereign", "url": "https://news.google.com/rss/search?q=%22Reserve+Bank+of+India%22+OR+%22RBI+monetary+policy%22+OR+%22forex+reserves%22&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Swiss National Bank SNB", "url": "https://news.google.com/rss/search?q=%22Swiss+National+Bank%22+OR+%22SNB+policy+rate%22&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Bank of Canada", "url": "https://www.bankofcanada.ca/valet/rss/press-releases"},
        {"name": "Reserve Bank of Australia", "url": "https://www.rba.gov.au/rss/rss-cb-bulletin.xml"},
        {"name": "US Treasury Debt & Auctions", "url": "https://news.google.com/rss/search?q=%22US+Treasury%22+OR+%22Treasury+auction%22+OR+%22bid-to-cover%22+OR+%22Treasury+yields%22&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Global Sovereign FX Reserves", "url": "https://news.google.com/rss/search?q=%22foreign+exchange+reserves%22+OR+%22bilateral+swap+line%22+OR+%22sovereign+debt+default%22&hl=en-US&gl=US&ceid=US:en"}
    ]

    def __init__(self, request_timeout: float = 6.0):
        self.request_timeout = request_timeout
        self.last_fetch: Dict[str, float] = {}
        self.cooldown_sec = 25.0

    def fetch_wires(self) -> List[Dict[str, Any]]:
        """Collects latest articles across sovereign financial feeds."""
        articles = []
        now = time.time()

        for feed_meta in self.SOVEREIGN_FEEDS:
            name = feed_meta["name"]
            url = feed_meta["url"]

            # Cooldown check
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
                            "source_type": "SOVEREIGN_CENTRAL_BANK",
                            "link": link,
                            "published": published,
                            "timestamp": now
                        })
                self.last_fetch[name] = now
            except Exception:
                # Fault tolerant: proceed without crashing on isolated network timeout
                continue

        return articles
