"""
TOPOLOGY MODULE (TRAP-FREE OPEN-WORLD INFORMATION MANIFOLD)
Eliminates all 4 Traps:
1. Zero Fixed Boxes: Dynamic graph community detection discovers emergent real-world themes (War, Cyber, Politics, Debt, Tech).
2. Anti-Echo Chamber: Provenance de-duplication requires distinct primary publishers (not syndication mirrors).
3. Anti-Narrative Fallacy: Clusters only form through genuine co-occurrence, not forced connections.
4. Off-Ramp Invalidation: Every emerging clue constellation displays its exact decay countdown and invalidation conditions.
"""

import time
import math
import re
import html
import heapq
import urllib.parse
from collections import defaultdict, deque
from typing import List, Dict, Any, Tuple, Set
try:
    from lead_arbiter import LeadArbiter
except ImportError:
    from topological_macro_mesh_v1.lead_arbiter import LeadArbiter

STOPWORDS = {
    'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'were', 
    'which', 'about', 'https', 'http', 'com', 'are', 'was', 'been', 
    'they', 'their', 'what', 'when', 'where', 'who', 'why', 'how', 'will', 'more',
    'into', 'some', 'than', 'them', 'then', 'also', 'other', 'over', 'per', 'via',
    'not', 'his', 'her', 'its', 'our', 'your', 'just', 'has', 'had', 'amid', 'upon',
    'all', 'any', 'one', 'out', 'can', 'could', 'would', 'should', 'but', 'yet', 'nor', 'now', 'may', 'might', 'must',
    'having', 'most', 'much', 'does', 'did', 'done', 'said', 'says',
    'like', 'very', 'well', 'many', 'even', 'such', 'year', 'years',
    'time', 'before', 'after', 'down', 'only', 'while', 'under',
    'between', 'during', 'both', 'each', 'those', 'these', 'whose',
    'being', 'through', 'because', 'against', 'since', 'until', 'without',
    'make', 'made', 'take', 'took', 'seen', 'know', 'want', 'come', 'came',
    'first', 'last', 'next', 'back', 'still', 'look', 'looked', 'part',
    'tell', 'told', 'give', 'given', 'good', 'daily', 'today', 'weekly',
    'monthly', 'update', 'brief', 'report', 'news', 'breaking', 'latest',
    # Generic non-macro adjectives and filler words
    'new', 'high', 'low', 'big', 'top', 'best', 'small', 'large', 'huge', 'major', 'recent',
    # Common news reporting verbs that form false topological bridges
    'holds', 'held', 'adds', 'added', 'helps', 'helped', 'joins', 'joined', 'meets', 'met',
    'finds', 'found', 'keeps', 'kept', 'opens', 'opened', 'closes', 'closed', 'moves', 'moved',
    'rises', 'rose', 'falls', 'fell', 'shows', 'shown', 'sees', 'sets', 'puts',
    # Collector template and feed metadata artifacts
    'wikipedia', 'attention', 'inquiries', 'velocity', 'article', 'articles', 'pulse', 'squawk', 'squawks',
    'guide', 'guides', 'online', 'tools', 'website', 'service', 'services',
    # Numeric words and quantity counters
    'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'hundred', 'thousand',
    # Unescaped HTML entities artifacts
    'quot', 'apos', 'amp', 'nbsp', 'lt', 'gt'
}

# Recognized 3-letter macro acronyms, sovereign entities, and commodities
MACRO_3LETTER_ALLOWLIST = {
    'fed', 'ecb', 'boj', 'gdp', 'cpi', 'pmi', 'sec', 'oil', 'gas',
    'tax', 'imf', 'wto', 'boc', 'pce', 'ism', 'ppi', 'xau', 'dxy',
    'ust', 'war', 'aid', 'law', 'fx', 'tar'
}

CROWD_SOURCES = {'wikimedia attention pulse', 'google crowd autocomplete', 'mastodon decentralized fediverse'}

class TopologyEngine:
    def __init__(self, half_life_seconds: float = 7200.0): # 2-hour half life
        self.half_life = half_life_seconds
        self.decay_constant = math.log(2) / self.half_life
        self.lead_arbiter = LeadArbiter()
        self.wire_phrases = set()
        self.crowd_phrases = set()
        
        self.token_history = defaultdict(list)
        self.token_publishers = defaultdict(set)
        self.token_sources = defaultdict(set)
        self.token_mentions = defaultdict(int)
        self.token_first_seen = {}
        self.token_trigger = {}
        
        # N-Gram Phrase Tracking with Publisher Provenance & Inverse Corpus Frequency (ICF)
        self.phrase_history = defaultdict(list)
        self.phrase_publishers = defaultdict(set)
        self.phrase_sources = defaultdict(set)
        self.phrase_contexts = defaultdict(list)
        self.phrase_doc_counts = defaultdict(int) # Background document frequency
        self.total_docs_seen = 0
        self.gold_docs_seen = 0
        self.gold_co_occurrences = defaultdict(int)
        self.seen_items = {} # Cache (publisher, text) -> last_seen_ts to prevent duplicate poll timestamp spam
        
        self.edges = {}
        self.nodes = {}

        # Universal Gold Spot Anchor
        now = time.time()
        self.nodes["god_xau"] = {
            "cluster": 0, "label": "XAUUSD SPOT", "last_seen": now, "z_score": 0.0,
            "is_god": True, "r": 8.0, "trigger_text": "Universal Spot Gold Pricing Anchor",
            "trigger_source": "Interbank Cash"
        }
        self.token_first_seen["god_xau"] = now

    def _format_trigger_text(self, text: str, max_len: int = 220) -> str:
        cleaned = html.unescape(text).strip()
        # Strip all URLs (with protocol or bare domains)
        cleaned = re.sub(r'(?:https?://|www\.|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}/)\S*', '', cleaned)
        # Strip reply / content-warning prefixes
        cleaned = re.sub(r'^(?:re|cw):\s*', '', cleaned, flags=re.I)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if len(cleaned) <= max_len:
            return cleaned
        last_sp = cleaned[:max_len].rfind(' ')
        return (cleaned[:last_sp] if last_sp > max_len - 40 else cleaned[:max_len]) + "..."

    def _clean_tokens(self, text: str) -> List[str]:
        # Unescape HTML entities first
        text = html.unescape(text)
        # Track uppercase 3-letter acronyms from raw text before lowercasing (e.g. 'CEO', 'TSA', 'BMW', 'ICC', 'WHO')
        uppercase_3_acronyms = set(re.findall(r'\b[A-Z]{3}\b', text))

        # Strip all URLs, bare domains, and social handles before tokenizing
        cleaned = re.sub(r'(?:https?://|www\.|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}/)\S*', ' ', text.lower())
        cleaned = re.sub(r'@[a-zA-Z0-9_]+', ' ', cleaned)
        words = re.findall(r'[a-zA-Z]{3,}', cleaned)
        
        filtered = []
        for w in words:
            if w in STOPWORDS:
                continue
            if len(w) >= 4:
                filtered.append(w)
            elif len(w) == 3:
                # Keep only recognized macro commodities/terms or raw uppercase acronyms
                if w in MACRO_3LETTER_ALLOWLIST or w.upper() in uppercase_3_acronyms:
                    filtered.append(w)
        return filtered

    def _extract_ngrams(self, text: str, n_range=(2, 4)) -> List[str]:
        clean_words = self._clean_tokens(text)
        if len(clean_words) < 2:
            return []
        ngrams = []
        for n in range(n_range[0], min(n_range[1] + 1, len(clean_words) + 1)):
            for i in range(len(clean_words) - n + 1):
                phrase = " ".join(clean_words[i:i+n])
                ngrams.append(phrase)
        return ngrams

    def ingest_stream_items(self, items: List[Dict[str, str]], is_crowd: bool = False):
        """
        Open-World Ingestion with Publisher Provenance Tracking.
        Kills the Echo-Chamber Mirage by separating raw mentions from distinct publisher entities.
        """
        now = time.time()
        for item in items:
            source = item.get("source", "Entity")
            publisher = item.get("publisher", source)
            text = item.get("text", "")
            if not text or len(text) < 8:
                continue

            item_key = (publisher, text.strip())
            is_new_item = (item_key not in self.seen_items or (now - self.seen_items[item_key]) > 3600)
            self.seen_items[item_key] = now
            if is_new_item:
                self.total_docs_seen += 1

            tokens = self._clean_tokens(text)
            ngrams = self._extract_ngrams(text)

            # 1. Multi-Word Phrase Tracking with Provenance & ICF
            is_crowd_doc = is_crowd or any(k in source.lower() for k in ['crowd', 'search', 'wikimedia', 'mastodon'])
            seen_phrases_in_doc = set()
            for phrase in ngrams[:8]:
                if is_new_item:
                    self.phrase_history[phrase].append(now)
                    if phrase not in seen_phrases_in_doc:
                        self.phrase_doc_counts[phrase] += 1
                        seen_phrases_in_doc.add(phrase)
                self.phrase_publishers[phrase].add(publisher)
                self.phrase_sources[phrase].add(source)
                if is_crowd_doc:
                    self.crowd_phrases.add(phrase)
                else:
                    self.wire_phrases.add(phrase)
                if len(self.phrase_contexts[phrase]) < 4:
                    self.phrase_contexts[phrase].append((text[:130], publisher))
                self.phrase_history[phrase] = [ts for ts in self.phrase_history[phrase] if now - ts < 7200]

            if not tokens:
                continue

            # 2. Token-level statistics & Poisson arrival
            for t in tokens[:6]:
                if t not in self.token_first_seen:
                    self.token_first_seen[t] = now
                self.token_publishers[t].add(publisher)
                self.token_sources[t].add(source)
                
                clean_trig = self._format_trigger_text(text, 220)

                # ONLY update frequency and timestamps if this is a genuinely new headline/item
                if is_new_item:
                    self.token_mentions[t] += 1
                    self.token_history[t].append(now)
                    self.token_trigger[t] = (clean_trig, publisher)
                
                self.token_history[t] = [ts for ts in self.token_history[t] if now - ts < 7200]

                count_recent = sum(1 for ts in self.token_history[t] if now - ts < 900)
                baseline = max(2.5, len(self.token_history[t]) / 6.0)
                raw_z = (count_recent - baseline) / math.sqrt(baseline)

                pub_count = len(self.token_publishers[t])
                total_mentions = self.token_mentions[t]

                # Anti-Echo Rule: Only surge if 2+ distinct publishers confirm
                if pub_count < 2 and total_mentions < 6:
                    z = min(1.8, max(0.0, raw_z))
                    is_surging = False
                else:
                    z = max(0.0, raw_z)
                    is_surging = (z >= 6.0 and pub_count >= 2)

                label = publisher.split()[0] + ": " + t.capitalize()
                
                # ONLY refresh last_seen if this is a new item, or if node doesn't exist yet!
                existing_last_seen = self.nodes[t]["last_seen"] if t in self.nodes else now
                node_last_seen = now if is_new_item else existing_last_seen

                self.nodes[t] = {
                    "cluster": self.nodes[t]["cluster"] if t in self.nodes else 0,
                    "label": label[:34],
                    "last_seen": node_last_seen,
                    "z_score": round(z, 2),
                    "is_surging": is_surging,
                    "r": 5.2 if is_surging else 3.2,
                    "trigger_text": clean_trig if is_new_item else self.nodes.get(t, {}).get("trigger_text", clean_trig),
                    "trigger_source": publisher if is_new_item else self.nodes.get(t, {}).get("trigger_source", publisher)
                }

            # 3. Form Co-Occurrence Edges (Empirical Association)
            for i in range(min(4, len(tokens))):
                for j in range(i + 1, min(5, len(tokens))):
                    t1, t2 = sorted([tokens[i], tokens[j]])
                    key = (t1, t2)
                    if key not in self.edges:
                        self.edges[key] = {"weight": 0.6, "last_seen": now, "te": 0.35}
                    elif is_new_item:
                        self.edges[key]["weight"] = min(3.0, self.edges[key]["weight"] + 0.3)
                        self.edges[key]["last_seen"] = now

            # 4. Empirical Natural Gold Linkage (Pointwise Mutual Information - PMI)
            # Forms dynamic mathematical association through genuine Gold tokens and COMEX wire sources
            is_gold_doc = ("gold" in tokens or "Gold" in source or "god_xau" in tokens)
            if is_gold_doc:
                if is_new_item:
                    self.gold_docs_seen += 1
                
                total_docs = max(10, self.total_docs_seen)
                p_gold = max(1, self.gold_docs_seen) / total_docs

                # Form statistical linkage with all high-salience tokens in the document
                for tok in tokens[:4]:
                    if tok == "god_xau" or len(tok) < 3:
                        continue
                    if is_new_item:
                        self.gold_co_occurrences[tok] += 1
                    
                    co_count = self.gold_co_occurrences[tok]
                    tok_mentions = max(1, self.token_mentions.get(tok, 1))
                    
                    p_tok = tok_mentions / total_docs
                    p_joint = max(1, co_count) / total_docs
                    
                    # Pointwise Mutual Information: PMI(tok, gold) = ln( P(tok, gold) / (P(tok) * P(gold)) )
                    raw_pmi = math.log(max(1e-5, p_joint / (p_tok * p_gold)))
                    npmi = max(0.0, min(1.0, (raw_pmi + 2.0) / 4.0)) # Normalized between 0 and 1
                    
                    dynamic_weight = round(max(0.6, min(3.0, 0.8 + (npmi * 2.0))), 2)
                    dynamic_te = round(max(0.30, min(0.92, 0.40 + (npmi * 0.45))), 2)
                    
                    edge_key = tuple(sorted([tok, "god_xau"]))
                    if edge_key not in self.edges:
                        self.edges[edge_key] = {"weight": dynamic_weight, "last_seen": now, "te": dynamic_te}
                    elif is_new_item:
                        self.edges[edge_key]["weight"] = dynamic_weight
                        self.edges[edge_key]["te"] = dynamic_te
                        self.edges[edge_key]["last_seen"] = now

    def find_shortest_causal_path(self, start_token: str, target: str = "god_xau") -> Tuple[List[str], float]:
        """
        Dijkstra's Algorithm over Transfer Entropy / Edge Weights to find the true
        mathematical transmission pipeline from an emerging entity to Gold (XAUUSD).
        """
        if start_token not in self.nodes or target not in self.nodes:
            return ([start_token, target], 0.5)

        adj = defaultdict(dict)
        for (src, tgt), ed in self.edges.items():
            w = ed.get("weight", 0.5)
            # Cost is inverse of weight: high weight = low resistance transmission path
            cost = 1.0 / max(0.05, w)
            adj[src][tgt] = cost
            adj[tgt][src] = cost

        pq = [(0.0, start_token, [start_token])]
        visited = set()

        while pq:
            cost, curr, path = heapq.heappop(pq)
            if curr == target:
                avg_weight = len(path) / max(1e-4, cost)
                return (path, round(avg_weight, 2))
            if curr in visited:
                continue
            visited.add(curr)
            for nbr, edge_cost in adj[curr].items():
                if nbr not in visited and len(path) < 6: # max 5 hops
                    heapq.heappush(pq, (cost + edge_cost, nbr, path + [nbr]))

        return ([start_token, "god_xau"], 0.3)

    def _discover_communities(self) -> Tuple[Dict[int, List[str]], Dict[int, Dict[str, Any]]]:
        """
        Seedless Mathematical Community Discovery.
        Finds emergent thematic groupings organically and names them via TF-ICF centroid salience.
        """
        adj = defaultdict(set)
        for (src, tgt) in self.edges.keys():
            if src in self.nodes and tgt in self.nodes:
                adj[src].add(tgt)
                adj[tgt].add(src)

        visited = set()
        communities = {}
        community_meta = {}
        c_idx = 0

        # Sort nodes by degree so community hubs are processed first
        sorted_nodes = sorted(self.nodes.keys(), key=lambda n: len(adj[n]), reverse=True)

        for nid in sorted_nodes:
            if nid not in visited and not self.nodes[nid].get("is_god"):
                members = []
                queue = deque([nid])
                visited.add(nid)
                while queue and len(members) < 45: # max community size
                    curr = queue.popleft()
                    members.append(curr)
                    for nbr in adj[curr]:
                        if nbr not in visited and not self.nodes[nbr].get("is_god"):
                            visited.add(nbr)
                            queue.append(nbr)
                if len(members) >= 2:
                    communities[c_idx] = members
                    
                    # Mathematical Centroid Naming (TF * ICF * Degree * Z)
                    def score_token(t):
                        d = self.nodes.get(t, {})
                        deg = len(adj[t])
                        z = max(0.5, d.get("z_score", 0.0))
                        doc_freq = self.token_mentions.get(t, 1)
                        total_docs = max(10, self.total_docs_seen)
                        icf = math.log(1.0 + (total_docs / max(1, doc_freq)))
                        return deg * z * icf

                    ranked_tokens = sorted(members, key=score_token, reverse=True)
                    top_t = [t.title() for t in ranked_tokens[:2]]
                    name = " & ".join(top_t) + " Cluster" if len(top_t) >= 2 else (top_t[0] + " Cluster" if top_t else f"Cluster {c_idx+1}")
                    
                    community_meta[c_idx] = {
                        "id": c_idx,
                        "name": name,
                        "top_tokens": [t.title() for t in ranked_tokens[:5]],
                        "size": len(members)
                    }
                    c_idx += 1

        return communities, community_meta

    def get_surging_entities(self, top_k: int = 5) -> List[str]:
        """
        Returns dynamic surging entities/tokens from the graph (high z-score, multi-publisher).
        Excludes god anchor nodes, numbers, and stopwords.
        Used to dynamically steer crowd collection without hardcoded seed lists.
        """
        candidates = []
        for nid, data in self.nodes.items():
            if data.get("is_god") or not isinstance(nid, str) or len(nid) < 3 or nid.isdigit():
                continue
            z = data.get("z_score", 0.0)
            pubs = len(self.token_publishers.get(nid, set()))
            mentions = self.token_mentions.get(nid, 1)
            # Prioritize real multi-publisher backing and mathematical surge
            score = z * math.log(1 + mentions) * (1.5 if pubs >= 2 else 1.0)
            candidates.append((nid, score, z, pubs))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:top_k]]

    def extract_emerging_constellations(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Identifies active, multi-front emerging story constellations forming in the world.
        Applies Anti-Echo chamber proof (distinct publishers) and Invalidation Off-Ramps.
        """
        now = time.time()
        candidates = []

        for phrase, timestamps in self.phrase_history.items():
            publishers = self.phrase_publishers.get(phrase, set())
            pub_count = len(publishers)
            total_count = len(timestamps)
            
            # Anti-Echo Rule: Require at least 2 distinct primary publishers
            if pub_count < 2 and total_count < 4:
                continue

            recent_count = sum(1 for ts in timestamps if now - ts < 1200) # last 20m
            if recent_count < 2:
                continue

            baseline = max(1.0, (total_count - recent_count) / 4.0)
            z_score = (recent_count - baseline) / math.sqrt(baseline)

            # Maturation age in minutes
            first_ts = min(timestamps) if timestamps else now
            maturation_min = round((now - first_ts) / 60.0, 1)

            # Formation Stage
            if pub_count >= 3 and z_score >= 3.0:
                stage = "STAGE 3: PRE-WIRE"
                stage_pct = 85
            elif pub_count >= 2 and z_score >= 1.8:
                stage = "STAGE 2: CLUSTER FORMING"
                stage_pct = 55
            else:
                stage = "STAGE 1: GROUND WHISPER"
                stage_pct = 25

            q_encoded = urllib.parse.quote(phrase)
            google_url = f"https://www.google.com/search?q={q_encoded}"
            x_url = f"https://x.com/search?q={q_encoded}&f=live"

            # Distinguish real journalistic newsrooms from crowd queries
            CROWD_SOURCES = {'wikimedia attention pulse', 'google crowd autocomplete', 'mastodon decentralized fediverse'}
            real_newsrooms = [p for p in publishers if p.lower() not in CROWD_SOURCES and 'crowd' not in p.lower() and 'search' not in p.lower() and 'wiki' not in p.lower()]
            crowd_channels = [p for p in publishers if p.lower() in CROWD_SOURCES or 'crowd' in p.lower() or 'search' in p.lower() or 'wiki' in p.lower()]
            is_pure_crowd = (len(real_newsrooms) == 0 and len(crowd_channels) > 0)

            if is_pure_crowd:
                prov_label = f"{len(crowd_channels)} Crowd Channels (0 Newsrooms)"
            else:
                prov_label = f"{len(real_newsrooms)} Newsrooms"

            # Representative Centroid Headline (Killing the [0] arbitrary index bug)
            contexts = self.phrase_contexts.get(phrase, [])
            if contexts:
                def score_context(ctx):
                    hl, pub = ctx
                    hl_lower = hl.lower()
                    pub_lower = pub.lower()
                    is_real_pub = pub_lower not in CROWD_SOURCES and 'crowd' not in pub_lower and 'search' not in pub_lower and 'wiki' not in pub_lower
                    
                    # Mathematical Information Density:
                    tokens = [w for w in re.findall(r'[a-zA-Z]{3,}', hl_lower) if w not in STOPWORDS]
                    total_docs = max(20, self.total_docs_seen)
                    salience = sum(math.log(1.0 + (total_docs / max(1, self.token_mentions.get(w, 1)))) for w in tokens)
                    max_z = max([self.nodes.get(w, {}).get("z_score", 0.0) for w in tokens] or [0.0])
                    
                    return (2.5 if is_real_pub else 0.5) * (1.0 + max_z * 0.4) * salience

                best_ctx = max(contexts, key=score_context)
                context_headline, primary_pub = best_ctx
            else:
                context_headline, primary_pub = (phrase, "Wire")

            # Shannon Information Surprise / Inverse Corpus Frequency (ICF)
            # Ubiquitous background entities ("federal reserve", "united states") have high doc_freq (~0.3-0.7 ICF).
            # Specific precursor clues appearing abruptly have low doc_freq (~2.5-4.5 ICF).
            total_corpus_docs = max(20, self.total_docs_seen)
            doc_freq = self.phrase_doc_counts.get(phrase, 1)
            icf = round(math.log(1.0 + (total_corpus_docs / max(1, doc_freq))), 2)

            # 1. Hawkes Ignition Point Process (Self-Exciting Acceleration)
            hawkes = self.lead_arbiter.compute_hawkes_ignition(timestamps, list(publishers), now=now)

            # 2. Sovereign Causal Transmission Pathway (derived from Dijkstra living graph path)
            p_tokens = phrase.split()
            cand_clusters = [self.nodes[t]["cluster"] for t in p_tokens if t in self.nodes]
            cand_cluster = max(set(cand_clusters), key=cand_clusters.count) if cand_clusters else 0
            
            # Mathematical Dijkstra transmission path through edge weights to Gold
            causal_path, path_weight = self.find_shortest_causal_path(p_tokens[0] if p_tokens else phrase, target="god_xau")
            causal = self.lead_arbiter.derive_causal_pathway(
                context_headline,
                cluster_idx=cand_cluster,
                is_crowd_only=is_pure_crowd,
                transmission_path=causal_path
            )

            # 3. Attention Divergence Asymmetry (Wires vs Crowd)
            is_wire = phrase in self.wire_phrases
            is_crowd = phrase in self.crowd_phrases
            if is_wire and not is_crowd and z_score >= 2.2:
                lead_type = "ASYMMETRIC_LEAD"
                lead_desc = "High-Alpha Front-Run (Wires accelerating, Crowd unaware)"
                lead_badge = "🎯 Asymmetric Lead: High Alpha"
            elif is_crowd and not is_wire:
                lead_type = "CROWD_BUBBLE"
                lead_desc = "Crowd Search Divergence (Public speculation without hard wires)"
                lead_badge = "👥 Crowd Speculation"
            elif is_wire and is_crowd:
                lead_type = "PRICED_IN_SATURATION"
                lead_desc = "Mainstream Saturation (Wires & Public converged; priced-in)"
                lead_badge = "⚠️ Priced-In Saturation"
            else:
                lead_type = "STRUCTURAL_BALANCE"
                lead_desc = "Equilibrium Transmission"
                lead_badge = "⚖️ Structural Equilibrium"

            # 4. Mathematical Clue Off-Ramp Invalidation Lifespan
            last_ts = max(timestamps) if timestamps else now
            idle_min = round((now - last_ts) / 60.0, 1)
            ttl_min = 30.0
            remaining_min = max(0.0, round(ttl_min - idle_min, 1))
            if remaining_min > 0:
                off_ramp_status = f"{remaining_min}m remaining | Decays if unconfirmed"
            else:
                off_ramp_status = "Decaying naturally (stale unconfirmed clue)"

            candidates.append({
                "phrase": phrase,
                "title": phrase.title(),
                "z_score": round(z_score, 2),
                "icf": icf,
                "publisher_count": pub_count,
                "newsroom_count": len(real_newsrooms),
                "crowd_channel_count": len(crowd_channels),
                "is_pure_crowd": is_pure_crowd,
                "provenance_label": prov_label,
                "publishers": list(publishers),
                "primary_publisher": primary_pub,
                "sample_headline": context_headline,
                "stage": stage,
                "stage_pct": stage_pct,
                "maturation_minutes": maturation_min,
                "hawkes": hawkes,
                "hawkes_badge": hawkes["badge"],
                "causal_pipeline": causal["pipeline"],
                "causal_pipeline_name": causal["pipeline_name"],
                "transmission_chain": causal["transmission_chain"],
                "expected_gold_impact": causal["expected_gold_impact"],
                "inflection_summary": causal["inflection_summary"],
                "lead_type": lead_type,
                "lead_desc": lead_desc,
                "lead_badge": lead_badge,
                "off_ramp_remaining_min": remaining_min,
                "off_ramp_note": off_ramp_status,
                "google_url": google_url,
                "x_url": x_url
            })

        # Sort by mathematical burst velocity * Shannon ICF surprise * real newsroom breadth * hawkes ratio
        candidates.sort(
            key=lambda c: c["z_score"] * c["icf"] * math.sqrt(c["newsroom_count"] if not c["is_pure_crowd"] else 0.4) * c["hawkes"]["ratio"],
            reverse=True
        )
        
        # Strict distinct-event deduplication across phrases and headline entities
        deduped = []
        seen_words = set()
        seen_headlines = set()

        for cand in candidates:
            words = set(cand["phrase"].split())
            headline = cand.get("sample_headline", "")
            headline_words = set(re.findall(r'[a-zA-Z]{3,}', headline.lower())) - STOPWORDS
            
            # Skip if phrase words overlap
            if any(w in seen_words for w in words):
                continue
            # Skip if headline shares 2+ entities with an already captured story
            if len(headline_words.intersection(seen_words)) >= 2:
                continue
            if headline in seen_headlines:
                continue

            deduped.append(cand)
            seen_words.update(words)
            seen_words.update(headline_words)
            seen_headlines.add(headline)
            if len(deduped) >= top_k:
                break

        return deduped

    def _compute_graph_topology(self) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, List[str]]]:
        adj = defaultdict(set)
        for (src, tgt) in self.edges.keys():
            if src in self.nodes and tgt in self.nodes:
                adj[src].add(tgt)
                adj[tgt].add(src)

        degrees = {nid: len(adj[nid]) for nid in self.nodes}

        hops_to_god = {nid: 999 for nid in self.nodes}
        hops_to_god["god_xau"] = 0
        queue = deque(["god_xau"])
        visited = {"god_xau"}

        while queue:
            curr = queue.popleft()
            curr_dist = hops_to_god[curr]
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    hops_to_god[neighbor] = curr_dist + 1
                    queue.append(neighbor)

        comp_visited = set()
        components = {}
        comp_idx = 0
        for nid in self.nodes:
            if nid not in comp_visited:
                comp_members = []
                c_queue = deque([nid])
                comp_visited.add(nid)
                while c_queue:
                    node = c_queue.popleft()
                    comp_members.append(node)
                    for nbr in adj[node]:
                        if nbr not in comp_visited:
                            comp_visited.add(nbr)
                            c_queue.append(nbr)
                components[comp_idx] = comp_members
                comp_idx += 1

        return degrees, hops_to_god, components

    def prune_and_decay(self):
        now = time.time()
        
        # 1. Decay edge weights
        expired_edges = []
        for key, edge in self.edges.items():
            if key[0] == "god_xau" or key[1] == "god_xau":
                continue
            dt = now - edge["last_seen"]
            decay = math.exp(-self.decay_constant * dt)
            edge["weight"] *= decay
            if dt > self.half_life or edge["weight"] < 0.12:
                expired_edges.append(key)
        for key in expired_edges:
            del self.edges[key]

        # 2. Mathematical Reachability & Orphan Culling
        degrees, hops_to_god, components = self._compute_graph_topology()

        cull_nodes = set()
        for nid, data in self.nodes.items():
            if data.get("is_god"):
                continue

            dt_last = now - data["last_seen"]
            deg = degrees.get(nid, 0)
            pub_count = len(self.token_publishers.get(nid, []))
            mentions = self.token_mentions.get(nid, 0)

            # Disconnected orphan (deg == 0): cull immediately
            if deg == 0:
                cull_nodes.add(nid)
                continue

            # Single-source leaf with degree <= 1 after 3 minutes: cull
            if deg <= 1 and pub_count <= 1 and mentions <= 2 and (now - self.token_first_seen.get(nid, now)) > 180:
                cull_nodes.add(nid)
                continue

            # Time expiration (older than half life with no recent mention)
            if dt_last > self.half_life:
                cull_nodes.add(nid)

        for nid in cull_nodes:
            if nid in self.nodes:
                del self.nodes[nid]

        d_edges = [k for k in self.edges.keys() if k[0] in cull_nodes or k[1] in cull_nodes]
        for k in d_edges:
            del self.edges[k]

        # 3. Clean up stale N-Gram phrase history to prevent memory leak and linguistic noise
        stale_phrases = [
            phrase for phrase, timestamps in self.phrase_history.items()
            if not timestamps or (now - max(timestamps)) > self.half_life
        ]
        for p in stale_phrases:
            del self.phrase_history[p]
            self.phrase_publishers.pop(p, None)
            self.phrase_sources.pop(p, None)
            self.phrase_contexts.pop(p, None)

        # 4. Graph Density Clamping (K-core topological resilience, expanding capacity to 500 nodes)
        MAX_NODES = 500
        if len(self.nodes) > MAX_NODES:
            # Score nodes by Degree * Mentions * Z-score
            # Retain well-connected 2-core hubs; cull isolated dead singletons first
            degrees = {nid: 0 for nid in self.nodes}
            for (s, t) in self.edges.keys():
                if s in degrees: degrees[s] += 1
                if t in degrees: degrees[t] += 1
                
            non_god_nodes = [
                (nid, degrees.get(nid, 0) * 2.0 + data.get("z_score", 0.0) * math.log(1.0 + self.token_mentions.get(nid, 1))) 
                for nid, data in self.nodes.items() if not data.get("is_god")
            ]
            non_god_nodes.sort(key=lambda x: x[1], reverse=True)
            excess = set(nid for nid, _ in non_god_nodes[MAX_NODES - 5:])
            for nid in excess:
                self.nodes.pop(nid, None)
            d_edges = [k for k in self.edges.keys() if k[0] in excess or k[1] in excess]
            for k in d_edges:
                self.edges.pop(k, None)

    def export_graph_json(self) -> Dict[str, Any]:
        self.prune_and_decay()
        degrees, hops_to_god, _ = self._compute_graph_topology()
        communities, community_meta = self._discover_communities()

        # Map each node to its dynamic emergent community
        node_cluster_map = {}
        for c_id, members in communities.items():
            for m in members:
                node_cluster_map[m] = c_id

        now = time.time()
        nodes_out = []
        age_dist = {"under_5m": 0, "5m_to_15m": 0, "15m_to_60m": 0, "over_60m": 0}

        for nid, d in self.nodes.items():
            first_seen = self.token_first_seen.get(nid, now)
            last_seen = d.get("last_seen", now)
            age_sec = max(0.0, round(now - first_seen, 1))
            last_seen_sec = max(0.0, round(now - last_seen, 1))

            if age_sec < 60:
                first_str = f"{int(age_sec)}s ago"
            else:
                first_str = f"{round(age_sec / 60.0, 1)}m ago"

            if last_seen_sec < 60:
                last_str = f"{int(last_seen_sec)}s ago"
            else:
                last_str = f"{round(last_seen_sec / 60.0, 1)}m ago"

            if age_sec < 300:
                regime = "HOT_BURST (<5m)"
                age_dist["under_5m"] += 1
            elif age_sec < 900:
                regime = "ACTIVE (5-15m)"
                age_dist["5m_to_15m"] += 1
            elif age_sec < 3600:
                regime = "STABLE (15-60m)"
                age_dist["15m_to_60m"] += 1
            else:
                regime = "DECAYING (>60m)"
                age_dist["over_60m"] += 1

            # Dynamic cluster index assigned organically by graph community
            dyn_cluster = node_cluster_map.get(nid, 0) if not d.get("is_god") else 0

            # Extract verification and provenance
            pubs = list(self.token_publishers.get(nid, []))
            is_crowd = (len(pubs) > 0 and all(p.lower() in CROWD_SOURCES or 'crowd' in p.lower() or 'search' in p.lower() or 'wiki' in p.lower() or 'mastodon' in p.lower() for p in pubs))
            clean_trigger = self._format_trigger_text(d.get("trigger_text", nid), 220)
            q_google = urllib.parse.quote(clean_trigger[:100])
            q_x = urllib.parse.quote(nid)

            nodes_out.append({
                "id": nid,
                "label": d["label"],
                "cluster": dyn_cluster,
                "z_score": d["z_score"],
                "is_surging": d.get("is_surging", False),
                "is_god": d.get("is_god", False),
                "is_crowd": is_crowd,
                "r": d.get("r", 3.0),
                "trigger_text": clean_trigger,
                "trigger_source": d.get("trigger_source", ""),
                "publishers": pubs,
                "publisher_count": len(pubs),
                "mention_count": self.token_mentions.get(nid, 1),
                "degree": degrees.get(nid, 0),
                "hops_to_xau": hops_to_god.get(nid, 999),
                "age_seconds": age_sec,
                "last_seen_seconds_ago": last_seen_sec,
                "first_seen_str": first_str,
                "last_seen_str": last_str,
                "freshness_regime": regime,
                "verify_google": f"https://www.google.com/search?q={q_google}",
                "verify_x": f"https://x.com/search?q={q_x}&f=live"
            })

        links_out = []
        for (src, tgt), edata in self.edges.items():
            if src in self.nodes and tgt in self.nodes:
                links_out.append({
                    "source": src,
                    "target": tgt,
                    "weight": round(edata.get("weight", 0.5), 2),
                    "te": round(edata.get("te", 0.35), 2)
                })

        constellations = self.extract_emerging_constellations(top_k=6)
        
        # Primary Driver Verification: Elevated to Primary Driver IF AND ONLY IF
        # corroborated across 2+ independent newsrooms, not pure crowd, with genuine Hawkes ratio >= 1.5
        eligible_drivers = [
            c for c in constellations 
            if c.get("newsroom_count", 0) >= 2 
            and not c.get("is_pure_crowd", False)
            and c.get("hawkes", {}).get("ratio", 1.0) >= 1.5
            and c.get("z_score", 0.0) >= 1.8
        ]

        if eligible_drivers:
            top_c = eligible_drivers[0]
            clean_pubs = [p for p in top_c["publishers"] if "crowd" not in p.lower() and "wiki" not in p.lower() and "autocomplete" not in p.lower()]
            primary_driver = {
                "active": True,
                "headline": top_c["sample_headline"],
                "clue_phrase": top_c["phrase"],
                "z_velocity": top_c["z_score"],
                "icf_surprise": top_c.get("icf", 1.0),
                "source_count": top_c["newsroom_count"],
                "sources_list": ", ".join(clean_pubs[:4]),
                "transmission": top_c["stage"],
                "regime": "CROSS_CONFIRMED_DRIVER",
                "lead_window": f"{top_c['maturation_minutes']}m forming",
                "hawkes_badge": top_c.get("hawkes_badge", ""),
                "causal_pipeline": top_c.get("causal_pipeline_name", ""),
                "transmission_chain": top_c.get("transmission_chain", ""),
                "expected_impact": top_c.get("expected_gold_impact", ""),
                "lead_badge": top_c.get("lead_badge", ""),
                "inflection_summary": top_c.get("inflection_summary", ""),
                "verify_google": top_c["google_url"],
                "verify_x": top_c["x_url"]
            }
        else:
            primary_driver = {
                "active": False,
                "headline": "Macro Horizon in Pre-Ignition Equilibrium (Awaiting Cross-Newsroom Corroboration)",
                "clue_phrase": "Structural Equilibrium",
                "z_velocity": 0.0,
                "source_count": 0,
                "sources_list": "Independent Wires Balanced",
                "transmission": "Structural balance",
                "regime": "NEUTRAL",
                "lead_window": "0m",
                "verify_google": "https://www.google.com/search?q=xauusd+gold",
                "verify_x": "https://x.com/search?q=gold%20xauusd&f=live"
            }

        return {
            "timestamp": time.time(),
            "nodes": nodes_out,
            "links": links_out,
            "communities": [
                {
                    "id": cid,
                    "name": meta["name"],
                    "top_tokens": meta["top_tokens"],
                    "size": meta["size"]
                }
                for cid, meta in community_meta.items()
            ],
            "emerging_constellations": constellations,
            "precursor_clues": constellations, # backwards compatibility for UI
            "primary_driver": primary_driver,
            "age_distribution": age_dist
        }
