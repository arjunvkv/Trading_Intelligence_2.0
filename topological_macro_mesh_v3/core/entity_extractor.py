"""
ZERO-SHOT MACRO ENTITY EXTRACTOR
Utilizes GLiNER (Generalist and Lightweight Named Entity Recognition)
for zero-shot open-domain macro entity extraction on CPU.
Eliminates regex tokenization and grammar particle noise (What, With, Could).
"""

import re
import html
import unicodedata
from typing import List, Dict, Any, Optional

try:
    from gliner import GLiNER
    HAS_GLINER = True
except ImportError:
    HAS_GLINER = False

class MacroEntityExtractor:
    DEFAULT_LABELS = [
        "sovereign state",
        "central bank",
        "monetary policy",
        "macro indicator",
        "geopolitical conflict",
        "critical commodity",
        "trade policy",
        "financial shock"
    ]

    # Universal grammar and temporal stopword exclusion
    GRAMMAR_STOPWORDS = {
        'what', 'with', 'could', 'from', 'your', 'about', 'this', 'that', 'they',
        'have', 'been', 'said', 'will', 'more', 'when', 'some', 'than', 'into',
        'over', 'after', 'were', 'also', 'their', 'which', 'there', 'would',
        'close', 'view', 'rock', 'stone', 'surface', 'daily', 'month', 'year',
        'today', 'yesterday', 'tomorrow', 'week', 'time', 'hours', 'latest',
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr',
        'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
        'photo', 'image', 'caption', 'read', 'click', 'page', 'full', 'story',
        'board', 'minutes', 'card', 'report', 'release', 'statement', 'speech',
        'review', 'notice', 'service', 'system', 'series', 'center', 'group',
        'update', 'article', 'press', 'news', 'paper', 'memo', 'event'
    }

    def __init__(self, model_name: str = "urchade/gliner_small-v2.1", device: str = "cpu"):
        self.device = device
        self.model = None
        self.labels = self.DEFAULT_LABELS
        
        if HAS_GLINER:
            try:
                # Load lightweight GLiNER small model (~150MB, CPU-optimized)
                self.model = GLiNER.from_pretrained(model_name)
                self.model.eval()
            except Exception as e:
                print(f"[MacroEntityExtractor] GLiNER load error: {e}. Falling back to syntactic chunker.")
                self.model = None

    def clean_text(self, text: str) -> str:
        """Sanitizes raw wire headline from HTML, tags, URLs, and PR scrape noise."""
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
        text = re.sub(r'(?:https?://|www\.)\S+', ' ', text)
        text = re.sub(r'\[#?[A-Z0-9_]+\]', ' ', text) # PR trade-show tags
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_entities(self, text: str, threshold: float = 0.45) -> List[Dict[str, Any]]:
        """
        Extracts genuine sovereign/macro entities.
        Returns a list of dicts: [{'text': 'Federal Reserve', 'label': 'central bank', 'id': 'federal_reserve', 'score': 0.89}]
        """
        clean = self.clean_text(text)
        if not clean or len(clean) < 6:
            return []

        # 1. High-precision GLiNER Neural Zero-Shot Extraction
        if self.model is not None:
            try:
                entities = self.model.predict_entities(clean, self.labels, threshold=threshold)
                results = []
                seen_ids = set()
                for ent in entities:
                    raw_txt = ent["text"].strip()
                    norm_id = re.sub(r'[^a-z0-9]+', '_', raw_txt.lower()).strip('_')
                    if len(norm_id) < 3 or norm_id in self.GRAMMAR_STOPWORDS or norm_id in seen_ids:
                        continue
                    seen_ids.add(norm_id)
                    results.append({
                        "id": norm_id,
                        "name": raw_txt.title(),
                        "label": raw_txt.title(),
                        "category": ent["label"],
                        "score": round(float(ent["score"]), 3)
                    })
                if results:
                    return results
            except Exception:
                pass

        # 2. Resilient Syntactic Fallback Chunker (Strict entity patterns, zero single grammar words)
        return self._syntactic_fallback_extraction(clean)

    def _syntactic_fallback_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Fallback: extracts multi-word proper nouns, acronyms, and sovereign phrases."""
        results = []
        seen = set()

        # Acronyms (e.g. FED, ECB, BOJ, PBOC, DXY, CPI, GDP, NATO, OPEC)
        for acr in re.findall(r'\b[A-Z]{2,5}\b', text):
            norm = acr.lower()
            if norm not in seen and norm not in self.GRAMMAR_STOPWORDS:
                seen.add(norm)
                results.append({"id": norm, "name": acr.upper(), "label": acr.upper(), "category": "macro_acronym", "score": 0.8})

        # Capitalized multi-word named entities (e.g. "US Treasury", "Middle East", "Critical Minerals")
        for chunk in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text):
            norm = re.sub(r'[^a-z0-9]+', '_', chunk.lower()).strip('_')
            words = set(norm.split('_'))
            if norm not in seen and not words.intersection(self.GRAMMAR_STOPWORDS):
                seen.add(norm)
                results.append({"id": norm, "name": chunk.title(), "label": chunk.title(), "category": "named_entity", "score": 0.75})

        # Single key sovereign nouns (must not be grammar stopwords)
        for single in re.findall(r'\b[A-Z][a-z]{3,}\b', text):
            norm = single.lower()
            if norm not in seen and norm not in self.GRAMMAR_STOPWORDS:
                seen.add(norm)
                results.append({"id": norm, "name": single.title(), "label": single.title(), "category": "entity", "score": 0.65})

        return results
