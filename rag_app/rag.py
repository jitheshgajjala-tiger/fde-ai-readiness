"""Local RAG: load docs, chunk, TF-IDF (keyword) and dense (semantic) indexes, hybrid retrieval, cited answers."""

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_STOPWORDS = {
    "the", "a", "an", "is", "are", "of", "to", "in", "and", "or", "for", "on", "what", "how", "do", "does",
    "many", "much", "which", "when", "who", "can", "have", "has", "with", "by", "from", "that", "this", "be",
}

NOT_FOUND_MESSAGE = "I could not find this in the provided documents."
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    doc_type: str
    text: str


@dataclass
class Index:
    chunks: list[Chunk]
    vectors: list[dict[str, float]]
    idf: dict[str, float]


@dataclass
class DenseIndex:
    chunks: list[Chunk]
    matrix: Any  # unit-normalised numpy array, one row per chunk
    model: Any


def _stem(token: str) -> str:
    return token[:-1] if len(token) > 3 and token.endswith("s") else token


def _tokenize(text: str) -> list[str]:
    return [_stem(t) for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


def _normalize(vector: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(v * v for v in vector.values()))
    return {t: v / norm for t, v in vector.items()} if norm else {}


def clean_documents(docs_dir: str | Path) -> list[dict[str, str]]:
    """Read every .md/.txt file under docs_dir; the sub-folder name becomes doc_type."""
    root = Path(docs_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"documents folder not found: {root}")
    documents = []
    for path in sorted(root.rglob("*")):
        if path.suffix not in {".md", ".txt"}:
            continue
        text = " ".join(path.read_text(encoding="utf-8").split())
        if not text:
            raise ValueError(f"document {path.name} is empty")
        doc_type = path.parent.name if path.parent != root else "general"
        documents.append({"source": path.name, "doc_type": doc_type, "text": text})
    if not documents:
        raise ValueError(f"documents folder {root} contains no .md or .txt files")
    logger.info("clean_documents: loaded %d documents from %s", len(documents), root)
    return documents


def build_chunks(documents: list[dict[str, str]], chunk_size: int = 60, overlap: int = 10) -> list[Chunk]:
    """Split documents into word-based chunks with overlap."""
    if chunk_size <= 0 or not 0 <= overlap < chunk_size:
        raise ValueError(f"chunking config invalid: chunk_size={chunk_size}, overlap={overlap}")
    logger.info("build_chunks: %d documents in", len(documents))
    chunks = []
    step = chunk_size - overlap
    for doc in documents:
        words = doc["text"].split()
        for n, start in enumerate(range(0, len(words), step)):
            piece = words[start:start + chunk_size]
            chunks.append(Chunk(f"{doc['source']}#{n}", doc["source"], doc["doc_type"], " ".join(piece)))
            if start + chunk_size >= len(words):
                break
    logger.info("build_chunks: %d chunks out", len(chunks))
    return chunks


def build_index(chunks: list[Chunk]) -> Index:
    """Build a TF-IDF (keyword) index over the chunks."""
    if not chunks:
        raise ValueError("chunks is empty, nothing to index")
    logger.info("build_index: %d chunks in", len(chunks))
    tokenized = [_tokenize(c.text) for c in chunks]
    doc_freq = Counter(t for tokens in tokenized for t in set(tokens))
    total = len(chunks)
    idf = {t: math.log((1 + total) / (1 + df)) + 1 for t, df in doc_freq.items()}
    vectors = [_normalize({t: tf * idf[t] for t, tf in Counter(tokens).items()}) for tokens in tokenized]
    logger.info("build_index: %d vectors, %d vocabulary terms", len(vectors), len(idf))
    return Index(chunks, vectors, idf)


def build_dense_index(chunks: list[Chunk], model_name: str = DEFAULT_EMBEDDING_MODEL) -> DenseIndex:
    """Embed the chunks with a local ONNX embedding model (requires fastembed and numpy)."""
    if not chunks:
        raise ValueError("chunks is empty, nothing to embed")
    try:
        import numpy as np
        from fastembed import TextEmbedding
    except ImportError as exc:
        raise ImportError("dense index requires 'fastembed' and 'numpy' (pip install fastembed numpy)") from exc
    logger.info("build_dense_index: %d chunks in, model %s", len(chunks), model_name)
    model = TextEmbedding(model_name)
    matrix = np.array(list(model.embed([c.text for c in chunks])), dtype=float)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    logger.info("build_dense_index: matrix shape %s", matrix.shape)
    return DenseIndex(chunks, matrix, model)


def retrieve(index: Index, query: str, top_k: int = 3, doc_type: str | None = None) -> list[tuple[Chunk, float]]:
    """Keyword (TF-IDF cosine) retrieval, optionally filtered by doc_type."""
    if not query.strip():
        raise ValueError("query is empty")
    query_vec = _normalize({t: tf * index.idf[t] for t, tf in Counter(_tokenize(query)).items() if t in index.idf})
    scored = []
    for chunk, vec in zip(index.chunks, index.vectors):
        if doc_type and chunk.doc_type != doc_type:
            continue
        scored.append((chunk, sum(w * vec.get(t, 0.0) for t, w in query_vec.items())))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]


def retrieve_dense(index: DenseIndex, query: str, top_k: int = 3, doc_type: str | None = None) -> list[tuple[Chunk, float]]:
    """Semantic (embedding cosine) retrieval, optionally filtered by doc_type."""
    if not query.strip():
        raise ValueError("query is empty")
    query_vec = next(iter(index.model.embed([query])))
    query_vec = query_vec / (sum(query_vec * query_vec) ** 0.5)
    sims = index.matrix @ query_vec
    scored = [(c, float(s)) for c, s in zip(index.chunks, sims) if not doc_type or c.doc_type == doc_type]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]


def retrieve_hybrid(
    dense_index: DenseIndex,
    keyword_index: Index,
    query: str,
    top_k: int = 3,
    doc_type: str | None = None,
    rrf_k: int = 60,
    keyword_weight: float = 1.0,
) -> list[tuple[Chunk, float]]:
    """Fuse semantic and keyword rankings with (weighted) Reciprocal Rank Fusion."""
    fused: dict[str, float] = {}
    by_id: dict[str, Chunk] = {}
    rankings = (
        (1.0, retrieve_dense(dense_index, query, len(dense_index.chunks), doc_type)),
        (keyword_weight, retrieve(keyword_index, query, len(keyword_index.chunks), doc_type)),
    )
    for weight, ranking in rankings:
        for rank, (chunk, score) in enumerate(ranking, start=1):
            if score <= 0:
                continue
            by_id[chunk.chunk_id] = chunk
            fused[chunk.chunk_id] = fused.get(chunk.chunk_id, 0.0) + weight / (rrf_k + rank)
    best = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:top_k]
    return [(by_id[chunk_id], score) for chunk_id, score in best]


def _coverage(query: str, text: str) -> float:
    """Share of the query's content terms that appear in the text."""
    query_terms = set(_tokenize(query))
    return len(query_terms & set(_tokenize(text))) / len(query_terms) if query_terms else 0.0


def answer_from_hits(
    query: str,
    hits: list[tuple[Chunk, float]],
    min_score: float = 0.0,
    min_coverage: float = 0.0,
) -> str:
    """Extractive answer with citations; refuses when no hit passes the score and coverage gates."""
    kept = [(c, s) for c, s in hits if s > 0 and s >= min_score and _coverage(query, c.text) >= min_coverage]
    logger.info("answer_from_hits: %d of %d chunks kept for query %r", len(kept), len(hits), query)
    if not kept:
        return NOT_FOUND_MESSAGE
    return "\n".join(f"{chunk.text} [{chunk.chunk_id}, score={score:.2f}]" for chunk, score in kept)


def answer(
    index: Index,
    query: str,
    top_k: int = 3,
    doc_type: str | None = None,
    min_score: float = 0.15,
    min_coverage: float = 0.0,
) -> str:
    """Keyword retrieval followed by answer_from_hits."""
    return answer_from_hits(query, retrieve(index, query, top_k, doc_type), min_score, min_coverage)


def build_prompt(query: str, hits: list[tuple[Chunk, float]]) -> str:
    """Grounded prompt for an LLM: numbered sources, cite-or-refuse instructions."""
    if not hits:
        raise ValueError("hits is empty, nothing to ground the prompt on")
    context = "\n".join(f"[{chunk.chunk_id}] {chunk.text}" for chunk, _ in hits)
    return (
        "Answer the question using ONLY the context below. Cite the chunk id in square brackets after each claim. "
        "Only answer what the context states explicitly; do not infer or use outside knowledge. "
        f"If the context does not contain the answer, reply exactly: {NOT_FOUND_MESSAGE}\n\n"
        f"Context:\n{context}\n\nQuestion: {query}"
    )
