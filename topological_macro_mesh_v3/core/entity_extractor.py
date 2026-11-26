"""
MACRO ENTITY EXTRACTOR (ZERO-SHOT GLINER & FASTEMBED DENSE VECTOR CANONICALIZATION)
Zero hardcoded entity lists. Zero hardcoded dictionaries. Zero regex pattern aliases.
Extracts genuine macroeconomic, sovereign debt, central bank, and geopolitical entities
using open-vocabulary zero-shot neural transformers (GLiNER) and resolves aliases
via FastEmbed ONNX dense semantic vector equivalence and algorithmic initials.
"""

import re
import html
import unicodedata
from typing import List, Dict, Any, Set, Tuple, Optional
import numpy as np

try:
    from gliner import GLiNER
    HAS_GLINER = True
except ImportError:
    HAS_GLINER = False

try:
    from fastembed import TextEmbedding
    HAS_FASTEMBED = True
except ImportError:
    HAS_FASTEMBED = False


def is_acronym_of(acronym: str, phrase: str) -> bool:
    """
    Universal algorithmic acronym check.
    Checks if 'acronym' matches initials of 'phrase' with zero hardcoding.
    Examples:
    - 'BOJ' <-> 'Bank of Japan' -> True
    - 'PBOC' <-> 'Peoples Bank of China' -> True
    - 'ECB' <-> 'European Central Bank' -> True
    - 'FOMC' <-> 'Federal Open Market Committee' -> True
    - 'IMF' <-> 'International Monetary Fund' -> True
    """
    a = acronym.strip().lower()
    if not (2 <= len(a) <= 6 and a.isalpha()):
        return False
    words = [w for w in re.split(r'[\s\-]+', phrase.strip()) if w]
    if len(words) < len(a):
        return False
    # Check 1: Direct initials across all words
    initials_all = "".join(w[0] for w in words).lower()
    if a == initials_all:
        return True
    # Check 2: Initials excluding functional stop-words (of, and, the, for, in, to)
    non_stop = [w for w in words if w.lower() not in {'of', 'the', 'for', 'and', 'in', 'to', 'on', 'at'}]
    initials_non_stop = "".join(w[0] for w in non_stop).lower()
    return a == initials_non_stop


class MacroEntityExtractor:
    # Open-vocabulary natural language target prompts for GLiNER zero-shot transformer
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

    def __init__(self, model_name: str = "urchade/gliner_small-v2.1", device: str = "cpu"):
        self.device = device
        self.model = None
        self.labels = self.DEFAULT_LABELS
        self.embedder = None
        self.vector_cache: Dict[str, np.ndarray] = {}
        self.canonical_cache: Dict[str, Tuple[str, str]] = {}

        if HAS_GLINER:
            try:
                self.model = GLiNER.from_pretrained(model_name)
                if self.device != "cpu":
                    self.model.to(self.device)
            except Exception:
                self.model = None

        if HAS_FASTEMBED:
            try:
                self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            except Exception:
                self.embedder = None

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

    def _batch_resolve_labels(self, unique_labels: List[str]) -> Dict[str, Tuple[str, str]]:
        """
        High-performance vectorized batch resolution for entity labels.
        Embeds all unseen entities in a single vectorized FastEmbed call.
        Computes dense cosine similarity matrix (>= 0.88) and universal algorithmic acronyms.
        Zero hardcoded dictionaries.
        """
        resolved: Dict[str, Tuple[str, str]] = {}
        unseen_to_embed: List[str] = []

        for lbl in unique_labels:
            low = lbl.lower().strip()
            if low in self.canonical_cache:
                resolved[low] = self.canonical_cache[low]
            else:
                if low not in self.vector_cache:
                    unseen_to_embed.append(lbl)

        # 1. Batch embed all unseen labels at once
        if unseen_to_embed and self.embedder is not None:
            try:
                embeddings = list(self.embedder.embed(unseen_to_embed))
                for txt, vec in zip(unseen_to_embed, embeddings):
                    v = np.array(vec, dtype=np.float32)
                    norm = np.linalg.norm(v)
                    if norm > 0:
                        v = v / norm
                    self.vector_cache[txt.lower().strip()] = v
            except Exception:
                pass

        # 2. Pairwise resolve unresolved labels via dense similarity & acronyms
        unresolved = [lbl for lbl in unique_labels if lbl.lower().strip() not in resolved]
        if len(unresolved) > 1 and self.vector_cache:
            valid = [lbl for lbl in unresolved if lbl.lower().strip() in self.vector_cache]
            if len(valid) > 1:
                mat = np.array([self.vector_cache[lbl.lower().strip()] for lbl in valid])
                sims = np.dot(mat, mat.T)
                n = len(valid)
                matched: Dict[int, int] = {}
                for i in range(n):
                    for j in range(i + 1, n):
                        is_acr = (is_acronym_of(valid[i], valid[j]) or is_acronym_of(valid[j], valid[i]))
                        sim = float(sims[i, j])
                        if is_acr or sim >= 0.88:
                            # Prefer longer phrase as canonical title (e.g. "Federal Reserve" over "Fed")
                            if len(valid[i]) >= len(valid[j]):
                                target, source = i, j
                            else:
                                target, source = j, i
                            matched[source] = target

                for s_idx, t_idx in matched.items():
                    s_low = valid[s_idx].lower().strip()
                    canon_lbl = valid[t_idx].strip()
                    canon_id = re.sub(r'[^a-z0-9]+', '_', canon_lbl.lower()).strip('_')
                    resolved[s_low] = (canon_id, canon_lbl.title())
                    self.canonical_cache[s_low] = (canon_id, canon_lbl.title())

        # 3. For remaining unresolved, map to their own title-case
        for lbl in unique_labels:
            low = lbl.lower().strip()
            if low not in resolved:
                norm_id = re.sub(r'[^a-z0-9]+', '_', low).strip('_')
                resolved[low] = (norm_id, lbl.title())
                self.canonical_cache[low] = (norm_id, lbl.title())

        return resolved

    def _suppress_subtokens(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suppresses sub-phrase components of longer recognized entities."""
        candidates.sort(key=lambda x: len(x["label"]), reverse=True)
        final_entities: List[Dict[str, Any]] = []
        accepted_norm_ids: Set[str] = set()

        for cand in candidates:
            c_id = cand["id"]
            c_label = cand["label"].lower()

            if c_id in accepted_norm_ids:
                continue

            is_subtoken = False
            for accepted in accepted_norm_ids:
                acc_label = accepted.replace('_', ' ')
                if c_label in acc_label.split() or (len(c_label) > 3 and c_label in acc_label):
                    is_subtoken = True
                    break

            if is_subtoken:
                continue

            accepted_norm_ids.add(c_id)
            final_entities.append(cand)

        return final_entities

    def extract_entities(self, text: str, threshold: float = 0.35) -> List[Dict[str, Any]]:
        """
        Extracts genuine sovereign/macro entities using pure GLiNER neural inference.
        """
        clean = self.clean_text(text)
        if not clean or len(clean) < 6:
            return []

        raw_candidates: List[Dict[str, Any]] = []

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

        if not raw_candidates:
            return []

        unique_labels = list({c["label"].strip() for c in raw_candidates})
        resolved_map = self._batch_resolve_labels(unique_labels)

        for cand in raw_candidates:
            low = cand["label"].strip().lower()
            if low in resolved_map:
                c_id, c_lbl = resolved_map[low]
                cand["id"] = c_id
                cand["name"] = c_lbl
                cand["label"] = c_lbl

        return self._suppress_subtokens(raw_candidates)

    def batch_extract_entities(self, texts: List[str], threshold: float = 0.35, batch_size: int = 32) -> List[List[Dict[str, Any]]]:
        """
        High-performance batch zero-shot entity extraction for hundreds of documents simultaneously.
        """
        cleaned_texts = [self.clean_text(t) for t in texts]
        valid_indices = [i for i, t in enumerate(cleaned_texts) if t and len(t) >= 6]

        all_results = [[] for _ in texts]
        if not valid_indices:
            return all_results

        gliner_outputs = [[] for _ in valid_indices]
        if self.model is not None:
            sub_texts = [cleaned_texts[i] for i in valid_indices]
            try:
                if hasattr(self.model, "inference"):
                    gliner_outputs = self.model.inference(sub_texts, self.labels, threshold=threshold, batch_size=batch_size)
                elif hasattr(self.model, "batch_predict_entities"):
                    gliner_outputs = self.model.batch_predict_entities(sub_texts, self.labels, threshold=threshold, batch_size=batch_size)
                else:
                    gliner_outputs = [self.model.predict_entities(t, self.labels, threshold=threshold) for t in sub_texts]
            except Exception:
                gliner_outputs = [[] for _ in valid_indices]

        # 1. Collect all raw candidates across all documents
        doc_raw_candidates = []
        all_labels_set = set()

        for idx_in_sub in range(len(valid_indices)):
            ents = gliner_outputs[idx_in_sub] if idx_in_sub < len(gliner_outputs) else []
            doc_cands = []
            for ent in ents:
                raw_txt = ent["text"].strip()
                norm_id = re.sub(r'[^a-z0-9]+', '_', raw_txt.lower()).strip('_')
                if len(norm_id) < 2 or norm_id in self.GRAMMAR_STOPWORDS:
                    continue
                doc_cands.append({
                    "id": norm_id,
                    "name": raw_txt.title(),
                    "label": raw_txt.title(),
                    "category": ent["label"],
                    "score": round(float(ent["score"]), 3)
                })
                all_labels_set.add(raw_txt.title())
            doc_raw_candidates.append(doc_cands)

        # 2. Vectorized Batch Resolve all unique labels at once (< 0.5s)
        resolved_map = self._batch_resolve_labels(list(all_labels_set))

        # 3. Apply canonical mapping and sub-token suppression per document
        for idx_in_sub, orig_idx in enumerate(valid_indices):
            raw_cands = doc_raw_candidates[idx_in_sub]
            for cand in raw_cands:
                low = cand["label"].strip().lower()
                if low in resolved_map:
                    c_id, c_lbl = resolved_map[low]
                    cand["id"] = c_id
                    cand["name"] = c_lbl
                    cand["label"] = c_lbl

            all_results[orig_idx] = self._suppress_subtokens(raw_cands)

        return all_results
