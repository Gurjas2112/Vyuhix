"""Knowledge retrieval (RAG) over Vyuhix's own docs and research notes.

Hybrid search: BM25 keyword scores and dense embeddings (BAAI/bge-small-en-v1.5 through fastembed,
ONNX on CPU, no API key) fused with reciprocal-rank fusion. If fastembed or the model download is
unavailable, search falls back to BM25 alone and reports that in `status()`.
Passages are data for the copilot to quote and cite, never instructions.
"""
from __future__ import annotations

import hashlib
import math
import os
import re
import threading
from collections import Counter

import numpy as np

from .settings import MODEL_CACHE, ROOT, RUNTIME_DIR

SOURCES = ["docs/*.md", "research/*.md", "data/demo/acme-fintech/README.md"]
SKIP = {"docs/README.md", "research/README.md"}            # tables of contents, not content
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
DENSE = os.getenv("VYUHIX_RAG_DENSE", "auto")             # "auto" or "off"
MAX_CHARS = 1200
RRF_K = 60

STOP = set("""a an and are as at be by can do does for from has have how i if in into is it its of on or our
so that the their them then there these this to us was we what when where which who why will with you your""".split())

_lock = threading.Lock()
_index: dict | None = None


# ── corpus ───────────────────────────────────────────────────────────────────────────────
def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _split(text: str) -> list[str]:
    """Paragraph-packed windows of at most MAX_CHARS; an oversized paragraph (a long table) splits by line."""
    parts: list[str] = []
    for para in re.split(r"\n\s*\n", text.strip()):
        if len(para) <= MAX_CHARS:
            parts.append(para)
        else:
            parts.extend(para.splitlines())
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) + 2 > MAX_CHARS:
            out.append(cur)
            cur = ""
        cur = f"{cur}\n\n{p}" if cur else p
    if cur.strip():
        out.append(cur)
    return out


def chunk_markdown(rel: str, text: str) -> list[dict]:
    """One chunk per `##`/`###` section (split further if long), each tagged with document title and section."""
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), rel)
    chunks: list[dict] = []
    section, buf = "Overview", []

    def flush():
        body = "\n".join(buf).strip()
        for i, piece in enumerate(_split(body) if body else []):
            cid = f"{rel}#{_slug(section)}" + (f"-{i + 1}" if i else "")
            chunks.append({"id": cid, "source": rel, "title": title, "section": section, "text": piece})

    for ln in text.splitlines():
        if ln.startswith("# "):
            continue
        if m := re.match(r"#{2,3}\s+(.*)", ln):
            flush()
            section, buf = m.group(1).strip(), []
        else:
            buf.append(ln)
    flush()
    return chunks


def corpus() -> list[dict]:
    out: list[dict] = []
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            if rel not in SKIP:
                out.extend(chunk_markdown(rel, path.read_text(encoding="utf-8")))
    return out


# ── BM25 ─────────────────────────────────────────────────────────────────────────────────
def tokens(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP]


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.docs, self.k1, self.b = [Counter(d) for d in docs], k1, b
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / max(len(docs), 1)
        df = Counter(t for d in self.docs for t in d)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: list[str]) -> np.ndarray:
        out = np.zeros(len(self.docs))
        for i, (d, ln) in enumerate(zip(self.docs, self.len)):
            for t in query:
                if f := d.get(t):
                    out[i] += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * ln / self.avg))
        return out


# ── dense embeddings ─────────────────────────────────────────────────────────────────────
def _embedder():
    from fastembed import TextEmbedding                   # optional dependency
    return TextEmbedding(EMBED_MODEL, cache_dir=str(MODEL_CACHE))


def _dense_matrix(model, chunks: list[dict]) -> np.ndarray:
    """Passage embeddings, cached on disk and keyed by the corpus content and model."""
    key = hashlib.sha256((EMBED_MODEL + "".join(c["id"] + c["text"] for c in chunks)).encode()).hexdigest()[:16]
    path = RUNTIME_DIR / "rag" / f"{key}.npy"
    if path.exists():
        return np.load(path)
    mat = np.array(list(model.passage_embed([_passage(c) for c in chunks])), dtype=np.float32)
    mat /= np.linalg.norm(mat, axis=1, keepdims=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, mat)
    return mat


def _passage(c: dict) -> str:
    return f"{c['title']} — {c['section']}\n{c['text']}"


def index() -> dict:
    global _index
    with _lock:
        if _index is None:
            chunks = corpus()
            idx = {"chunks": chunks, "bm25": BM25([tokens(_passage(c)) for c in chunks]),
                   "model": None, "dense": None, "dense_error": None}
            if DENSE != "off":
                try:
                    idx["model"] = _embedder()
                    idx["dense"] = _dense_matrix(idx["model"], chunks)
                except Exception as e:                    # not installed, offline, model download failed
                    idx["dense_error"] = f"{type(e).__name__}: {str(e)[:160]}"
            _index = idx
    return _index


def status() -> dict:
    idx = index()
    return {"chunks": len(idx["chunks"]), "documents": len({c["source"] for c in idx["chunks"]}),
            "method": "hybrid" if idx["dense"] is not None else "bm25",
            "embedding_model": EMBED_MODEL if idx["dense"] is not None else None, "dense_error": idx["dense_error"]}


# ── search ───────────────────────────────────────────────────────────────────────────────
def _rank(scores: np.ndarray) -> list[int]:
    return [int(i) for i in np.argsort(-scores, kind="stable")]


def search(query: str, k: int = 4, method: str = "hybrid") -> list[dict]:
    """Top-k passages. method: "bm25", "dense" or "hybrid" (hybrid becomes bm25 when no embeddings)."""
    idx = index()
    lex = idx["bm25"].scores(tokens(query))
    cos = None
    if idx["dense"] is not None and method in ("dense", "hybrid"):
        q = np.array(next(iter(idx["model"].query_embed([query]))), dtype=np.float32)
        cos = idx["dense"] @ (q / np.linalg.norm(q))
    if method == "dense" and cos is None:
        raise RuntimeError("dense retrieval unavailable: " + (idx["dense_error"] or "disabled"))

    if method == "bm25" or cos is None:
        order, score = _rank(lex), lex
    elif method == "dense":
        order, score = _rank(cos), cos
    else:
        fused = np.zeros(len(lex))
        for ranking in (_rank(lex), _rank(cos)):
            for r, i in enumerate(ranking):
                fused[i] += 1 / (RRF_K + r + 1)
        order, score = _rank(fused), fused
    return [{**idx["chunks"][i], "score": float(score[i]), "bm25": float(lex[i]),
             "cosine": float(cos[i]) if cos is not None else None} for i in order[:k]]


def relevant(hit: dict) -> bool:
    """Whether a top hit plausibly answers the query, used by the offline router to refuse off-topic questions."""
    if hit["cosine"] is not None:
        return hit["cosine"] >= 0.60 and hit["bm25"] > 0
    return hit["bm25"] >= 4.0
