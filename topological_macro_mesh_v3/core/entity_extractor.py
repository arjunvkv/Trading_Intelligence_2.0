"""
MACRO ENTITY EXTRACTOR (ZERO-SHOT NEURAL GLINER & SOVEREIGN FALLBACK)
Extracts genuine macroeconomic, central bank, sovereign debt, and geopolitical entities.
Strictly suppresses sub-token duplicates, grammar noise, and isolated title-case verbs.
"""

import re
import html
import unicodedata
from typing import List, Dict, Any, Set

try:
    from gliner import GLiNER
    HAS_GLINER = True
except ImportError:
    HAS_GLINER = False

class MacroEntityExtractor:
    DEFAULT_LABELS = [
        "sovereign state",
        "central bank",
        "central bank governor",
        "monetary policy",
        "macro indicator",
        "geopolitical conflict",
        "critical commodity",
        "trade policy",
        "financial shock",
        "chokepoint",
        "sanctions"
    ]

    KNOWN_SOVEREIGN_STATES = {
        "united states", "us", "u.s.", "china", "japan", "germany", "united kingdom",
        "uk", "u.k.", "france", "russia", "ukraine", "iran", "israel", "saudi arabia",
        "taiwan", "india", "canada", "australia", "south korea", "brazil", "switzerland",
        "eurozone", "european union", "eu", "singapore", "mexico", "turkey", "egypt"
    }

    KNOWN_MACRO_ACRONYMS = {
        "fed", "ecb", "boj", "pboc", "snb", "rbi", "boc", "rba", "dxy", "cpi", "pce",
        "gdp", "opec", "nato", "imf", "bis", "swift", "fomc", "vix", "tips", "brics"
    }

    KNOWN_MACRO_CONCEPTS = {
        "sanctions", "tariff", "tariffs", "inflation", "deflation", "stagflation", "recession",
        "yield", "yields", "default", "defaults", "blockade", "ceasefire", "debasement",
        "liquidity", "reserves", "deficit", "surplus", "embargo", "subsidies", "contagion",
        "downgrade", "bailout", "refinancing", "inversion", "spreads", "petrodollar",
        "swaps", "collateral", "chokepoint", "pipeline", "uranium", "copper",
        "lithium", "cobalt", "semiconductor", "semiconductors", "debt ceiling", "quantitative easing",
        "quantitative tightening", "reverse repo", "foreign exchange", "capital flight", "bank run",
        "de-dollarization", "currency war", "trade war", "export controls", "rare earths",
        "strait of hormuz", "suez canal", "bab el-mandeb", "malacca strait", "taiwan strait",
        "panama canal", "black sea", "red sea", "baltic dry", "treasury auction", "term premium"
    }

    GRAMMAR_STOPWORDS = {
        'what', 'with', 'could', 'from', 'your', 'about', 'this', 'that', 'they',
        'have', 'been', 'said', 'will', 'more', 'when', 'some', 'than', 'into',
        'over', 'after', 'were', 'also', 'their', 'which', 'there', 'would',
        'close', 'view', 'rock', 'stone', 'surface', 'daily', 'month', 'year',
        'today', 'yesterday', 'tomorrow', 'week', 'time', 'hours', 'latest',
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'photo', 'image', 'caption', 'read', 'click', 'page', 'full', 'story',
        'board', 'minutes', 'card', 'report', 'release', 'statement', 'speech',
        'review', 'notice', 'service', 'system', 'series', 'center', 'group',
        'update', 'article', 'press', 'news', 'paper', 'memo', 'event',
        'return', 'acting', 'first', 'second', 'third', 'high', 'low', 'near'
    }

    CANONICAL_ALIASES = {
        "imf": ("international_monetary_fund", "International Monetary Fund"),
        "international monetary fund": ("international_monetary_fund", "International Monetary Fund"),
        "mas": ("monetary_authority_of_singapore", "Monetary Authority of Singapore"),
        "monetary authority of singapore": ("monetary_authority_of_singapore", "Monetary Authority of Singapore"),
        "monetary authority of singapores": ("monetary_authority_of_singapore", "Monetary Authority of Singapore"),
        "ecb": ("european_central_bank", "European Central Bank"),
        "european central bank": ("european_central_bank", "European Central Bank"),
        "boj": ("bank_of_japan", "Bank of Japan"),
        "bank of japan": ("bank_of_japan", "Bank of Japan"),
        "pboc": ("peoples_bank_of_china", "People's Bank of China"),
        "peoples bank of china": ("peoples_bank_of_china", "People's Bank of China"),
        "pbo c": ("peoples_bank_of_china", "People's Bank of China"),
        "snb": ("swiss_national_bank", "Swiss National Bank"),
        "swiss national bank": ("swiss_national_bank", "Swiss National Bank"),
        "rbi": ("reserve_bank_of_india", "Reserve Bank of India"),
        "reserve bank of india": ("reserve_bank_of_india", "Reserve Bank of India"),
        "bis": ("bank_for_international_settlements", "Bank for International Settlements"),
        "bank for international settlements": ("bank_for_international_settlements", "Bank for International Settlements"),
        "fomc": ("federal_open_market_committee", "Federal Open Market Committee"),
        "federal open market committee": ("federal_open_market_committee", "Federal Open Market Committee"),
        "fed": ("federal_reserve", "Federal Reserve"),
        "federal reserve": ("federal_reserve", "Federal Reserve"),
        "federal reserve board": ("federal_reserve_board", "Federal Reserve Board"),
        "brics": ("brics", "BRICS"),
        "gdp": ("gdp", "GDP"),
        "dxy": ("dxy", "DXY")
    }

    def __init__(self, model_name: str = "urchade/gliner_small-v2.1", device: str = "cpu"):
        self.device = device
        self.model = None
        self.labels = self.DEFAULT_LABELS
        
        if HAS_GLINER:
            try:
                self.model = GLiNER.from_pretrained(model_name)
                if self.device != "cpu":
                    self.model.to(self.device)
            except Exception:
                self.model = None

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
        text = re.sub(r'(?:https?://|www\.)\S+', ' ', text)
        text = re.sub(r'\[#?[A-Z0-9_]+\]', ' ', text)
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_entities(self, text: str, threshold: float = 0.35) -> List[Dict[str, Any]]:
        """
        Extracts genuine sovereign/macro entities.
        Strictly suppresses sub-token duplicates and isolated verbs.
        """
        clean = self.clean_text(text)
        if not clean or len(clean) < 6:
            return []

        raw_candidates: List[Dict[str, Any]] = []

        # 1. High-precision GLiNER Zero-Shot Extraction
        if self.model is not None:
            try:
                entities = self.model.predict_entities(clean, self.labels, threshold=threshold)
                for ent in entities:
                    raw_txt = ent["text"].strip()
                    norm_id = re.sub(r'[^a-z0-9]+', '_', raw_txt.lower()).strip('_')
                    if len(norm_id) < 2 or norm_id in self.GRAMMAR_STOPWORDS:
                        continue
                    raw_candidates.append({
                        "id": norm_id,
                        "name": raw_txt.title(),
                        "label": raw_txt.title(),
                        "category": ent["label"],
                        "score": round(float(ent["score"]), 3)
                    })
            except Exception:
                pass

        # 2. Sovereign & Macro Pattern Matching Fallback/Augmentation
        fallback_candidates = self._syntactic_extraction(clean)
        raw_candidates.extend(fallback_candidates)

        if not raw_candidates:
            return []

        # 3. Canonical Aliasing (Resolve acronyms & full titles to unified canonical entity)
        for cand in raw_candidates:
            raw_key = cand["label"].lower().strip()
            clean_key = re.sub(r'^(the|a|an)\s+', '', raw_key).strip()
            clean_key = re.sub(r"['’]s$", '', clean_key).strip()
            clean_key = clean_key.replace("'", "")

            matched = False
            if clean_key in self.CANONICAL_ALIASES:
                canon_id, canon_label = self.CANONICAL_ALIASES[clean_key]
                cand["id"] = canon_id
                cand["name"] = canon_label
                cand["label"] = canon_label
                matched = True
            elif raw_key in self.CANONICAL_ALIASES:
                canon_id, canon_label = self.CANONICAL_ALIASES[raw_key]
                cand["id"] = canon_id
                cand["name"] = canon_label
                cand["label"] = canon_label
                matched = True

            if not matched:
                for alias_k, (c_id, c_lbl) in self.CANONICAL_ALIASES.items():
                    if " " in alias_k and alias_k in clean_key:
                        cand["id"] = c_id
                        cand["name"] = c_lbl
                        cand["label"] = c_lbl
                        break

        # 4. Deduplicate and Apply Sub-String / Sub-Token Suppression
        # Sort candidates by length of entity label descending (longest entity first)
        raw_candidates.sort(key=lambda x: len(x["label"]), reverse=True)

        final_entities: List[Dict[str, Any]] = []
        accepted_norm_ids: Set[str] = set()

        for cand in raw_candidates:
            c_id = cand["id"]
            c_label = cand["label"].lower()

            if c_id in accepted_norm_ids:
                continue

            # Sub-token suppression: if this candidate is a sub-phrase of an already accepted entity, drop it
            is_subtoken = False
            for accepted in accepted_norm_ids:
                acc_label = accepted.replace('_', ' ')
                # If candidate is a component word of longer entity (e.g. "christine" in "christine lagarde")
                if c_label in acc_label.split() or (len(c_label) > 3 and c_label in acc_label):
                    is_subtoken = True
                    break

            if is_subtoken:
                continue

            accepted_norm_ids.add(c_id)
            final_entities.append(cand)

        return final_entities

    def _syntactic_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Extracts known acronyms, sovereign states, and multi-word capitalized named entities."""
        results = []
        seen = set()

        # 1. Macro Acronyms (e.g. FED, ECB, BOJ, PBOC, DXY, CPI, GDP, NATO, OPEC)
        for acr in re.findall(r'\b[A-Z]{2,5}\b', text):
            norm = acr.lower()
            if norm in self.KNOWN_MACRO_ACRONYMS and norm not in seen:
                seen.add(norm)
                results.append({"id": norm, "name": acr.upper(), "label": acr.upper(), "category": "macro_acronym", "score": 0.85})

        # 2. Known Sovereign States & Regions
        for state in self.KNOWN_SOVEREIGN_STATES:
            pattern = r'\b' + re.escape(state) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                norm = re.sub(r'[^a-z0-9]+', '_', state).strip('_')
                if norm not in seen:
                    seen.add(norm)
                    results.append({"id": norm, "name": state.title(), "label": state.title(), "category": "sovereign state", "score": 0.90})

        # 3. Critical Sovereign Macro Concepts & Phenomena
        for concept in self.KNOWN_MACRO_CONCEPTS:
            pattern = r'\b' + re.escape(concept) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                norm = re.sub(r'[^a-z0-9]+', '_', concept).strip('_')
                if norm not in seen:
                    seen.add(norm)
                    results.append({"id": norm, "name": concept.title(), "label": concept.title(), "category": "macro_concept", "score": 0.88})

        # 4. Capitalized Multi-Word Phrases with Preposition & Financial Fragment Trimming
        TRIM_TOKENS = {
            'at', 'to', 'for', 'with', 'during', 'by', 'in', 'on', 'of', 'from',
            'and', 'or', 'about', 'up', 'down', 'into', 'over', 'per', 'amid',
            'as', 'out', 'off', 'than', 'under', 'after', 'near', 'offers',
            'offer', 'says', 'say', 'told', 'joins', 'starts', 'ended', 'ending',
            'holds', 'leaves', 'causes', 'sets', 'targeting', 'targets', 'paid'
        }

        for chunk in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text):
            words = chunk.split()
            while words and words[0].lower() in TRIM_TOKENS:
                words.pop(0)
            while words and words[-1].lower() in TRIM_TOKENS:
                words.pop()
            if len(words) < 2:
                continue
            cleaned_chunk = " ".join(words)

            # Discard corporate equity micro-placement noise
            if any(bad in cleaned_chunk.lower() for bad in [
                'per share', 'ordinary shares', 'new shares', 'pence per', 'cents per',
                'mln new', 'dividend', 'earnings per', 'wedding party', 'photo caption',
                'press review', 'terms tools', 'hearing entitled', 'unlocking new'
            ]):
                continue

            norm = re.sub(r'[^a-z0-9]+', '_', cleaned_chunk.lower()).strip('_')
            norm_words = set(norm.split('_'))
            if norm not in seen and not norm_words.intersection(self.GRAMMAR_STOPWORDS):
                seen.add(norm)
                results.append({"id": norm, "name": cleaned_chunk.title(), "label": cleaned_chunk.title(), "category": "named_entity", "score": 0.75})

        return results
