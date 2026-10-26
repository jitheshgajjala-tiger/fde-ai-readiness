"""Reproduces the experiments for the five RAG assignments. Run: python experiments.py [a1 a2 a3 a4 a5]."""

import logging
import sys
from pathlib import Path

from rag import (
    BASELINE_MIN_SCORE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    NOT_FOUND_MESSAGE,
    answer_from_hits,
    build_chunks,
    build_dense_index,
    build_index,
    build_prompt,
    clean_documents,
    retrieve,
    retrieve_dense,
    retrieve_hybrid,
)

DOCS = Path(__file__).resolve().parent / "docs"

# (question, phrase the correct chunk must contain)
ANSWERABLE = [
    ("How is order_total calculated?", "quantity multiplied by unit_price"),
    ("What time does the nightly orders load run?", "02:00 UTC"),
    ("Within how many days can unused products be returned?", "within 30 days of delivery"),
    ("How is the customer segment determined?", "customer_segment is derived from lifetime_value"),
    ("Who can see which regions in the sales dashboard?", "Access is restricted by region"),
    ("What happens to products without a sku?", "Products with a null sku are rejected"),
    ("How fast is express shipping?", "express shipping takes 1 to 2 business days"),
    ("What is the KPI for the sales dashboard?", "net_revenue"),
]

UNANSWERABLE = [
    "What is the refund policy for cryptocurrency payments?",
    "What is the warranty period for laptops?",
    "Who is the CEO of the company?",
    "What is the data retention period for the orders table?",
]

# (query, expected rule id, kind)
RULE_QUERIES = [
    ("DQ-1470", "DQ-1470", "exact id"),
    ("What does rule DQ-1470 check?", "DQ-1470", "exact id"),
    ("rule DQ-4170", "DQ-4170", "exact id"),
    ("Explain DQ-1407", "DQ-1407", "exact id"),
    ("what is DQ-1074", "DQ-1074", "exact id"),
    ("DQ-4107 rule", "DQ-4107", "exact id"),
    ("which check blocks duplicated order identifiers?", "DQ-1047", "paraphrase"),
    ("what validates that the product code is known?", "DQ-4107", "paraphrase"),
    ("which rule prevents negative totals?", "DQ-1470", "paraphrase"),
]


def _hit(hits, phrase, k):
    return any(phrase.lower() in chunk.text.lower() for chunk, _ in hits[:k])


def run_a1(documents):
    print(
        f"## A1: Baseline pipeline (chunk_size={DEFAULT_CHUNK_SIZE}, overlap={DEFAULT_CHUNK_OVERLAP}, "
        "dense embeddings BAAI/bge-small-en-v1.5)\n"
    )
    dense = build_dense_index(build_chunks(documents, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP))
    for question, phrase in ANSWERABLE[:5]:
        hits = retrieve_dense(dense, question, 1)
        print(f"Q: {question}\nA: {answer_from_hits(question, hits)}\nCorrect chunk retrieved: {_hit(hits, phrase, 1)}\n")


def run_a2(documents):
    print("## A2: Chunking trade-offs (8 questions, hit@k = correct phrase inside top-k chunks)\n")
    print("| config | chunks | avg words/chunk | TF-IDF hit@1 | TF-IDF hit@3 | dense hit@1 | dense hit@3 | avg top-1 words (dense) |")
    print("|---|---|---|---|---|---|---|---|")
    for size, overlap in [(25, 0), (25, 5), (80, 0), (80, 15)]:
        chunks = build_chunks(documents, size, overlap)
        keyword, dense = build_index(chunks), build_dense_index(chunks)
        kw = [retrieve(keyword, q, 3) for q, _ in ANSWERABLE]
        dn = [retrieve_dense(dense, q, 3) for q, _ in ANSWERABLE]
        phrases = [p for _, p in ANSWERABLE]
        n = len(ANSWERABLE)
        score = lambda runs, k: sum(_hit(h, p, k) for h, p in zip(runs, phrases))  # noqa: E731
        avg_words = sum(len(c.text.split()) for c in chunks) / len(chunks)
        top1_words = sum(len(h[0][0].text.split()) for h in dn) / n
        print(
            f"| {size} words, overlap {overlap} | {len(chunks)} | {avg_words:.0f} | {score(kw, 1)}/{n} | {score(kw, 3)}/{n} "
            f"| {score(dn, 1)}/{n} | {score(dn, 3)}/{n} | {top1_words:.0f} |"
        )
    print()


def run_a3(documents):
    print("## A3: Metadata-filtered retrieval (chunk_size=40, overlap=8, dense)\n")
    dense = build_dense_index(build_chunks(documents, 40, 8))
    query = "How are cancelled orders handled?"
    for label, doc_type in [("no filter", None), ("doc_type=sttm", "sttm"), ("doc_type=policy", "policy")]:
        print(f"[{label}] {query}")
        for chunk, score in retrieve_dense(dense, query, 3, doc_type):
            print(f"  {chunk.chunk_id:<24} type={chunk.doc_type:<7} score={score:.2f}  {chunk.text[:70]}...")
        print()


def run_a4(documents):
    print(
        f"## A4: Groundedness failure hunt (chunk_size={DEFAULT_CHUNK_SIZE}, "
        f"overlap={DEFAULT_CHUNK_OVERLAP}, dense, top-1, min_score={BASELINE_MIN_SCORE})\n"
    )
    dense = build_dense_index(build_chunks(documents, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP))
    print("Baseline on questions the docs do NOT answer:\n")
    for question in UNANSWERABLE:
        hits = retrieve_dense(dense, question, 1)
        print(f"Q: {question}\nA: {answer_from_hits(question, hits, min_score=BASELINE_MIN_SCORE)[:120]}\n")
    print("Sweep of the coverage gate (share of query terms that must appear in the cited chunk):\n")
    print("| min_coverage | answerable answered | unanswerable refused |")
    print("|---|---|---|")
    for gate in [0.0, 0.5, 0.6, 0.7, 0.8, 0.9]:
        answered = sum(
            answer_from_hits(q, retrieve_dense(dense, q, 1), BASELINE_MIN_SCORE, gate) != NOT_FOUND_MESSAGE
            for q, _ in ANSWERABLE
        )
        refused = sum(
            answer_from_hits(q, retrieve_dense(dense, q, 1), BASELINE_MIN_SCORE, gate) == NOT_FOUND_MESSAGE
            for q in UNANSWERABLE
        )
        print(f"| {gate} | {answered}/{len(ANSWERABLE)} | {refused}/{len(UNANSWERABLE)} |")
    question = UNANSWERABLE[0]
    print(f"\nGrounded prompt to paste into an LLM for: {question}\n")
    print(build_prompt(question, retrieve_dense(dense, question, 2)))
    print()


def run_a5(documents):
    print("## A5: Hybrid retrieval (chunk_size=20, overlap=10, top-1 must contain the expected rule id)\n")
    chunks = build_chunks(documents, 20, 10)
    keyword, dense = build_index(chunks), build_dense_index(chunks)
    print("| query | kind | dense | keyword | hybrid (RRF) |")
    print("|---|---|---|---|---|")
    totals = {"dense": 0, "keyword": 0, "hybrid": 0}
    for query, expected, kind in RULE_QUERIES:
        runs = {
            "dense": retrieve_dense(dense, query, 1),
            "keyword": retrieve(keyword, query, 1),
            "hybrid": retrieve_hybrid(dense, keyword, query, 1),
        }
        marks = {}
        for name, hits in runs.items():
            ok = _hit(hits, expected, 1)
            totals[name] += ok
            marks[name] = "PASS" if ok else "FAIL"
        print(f"| {query} | {kind} | {marks['dense']} | {marks['keyword']} | {marks['hybrid']} |")
    n = len(RULE_QUERIES)
    print(f"| **total** | | {totals['dense']}/{n} | {totals['keyword']}/{n} | {totals['hybrid']}/{n} |\n")


def main():
    logging.basicConfig(level=logging.WARNING)
    selected = [a.lower() for a in sys.argv[1:]] or ["a1", "a2", "a3", "a4", "a5"]
    documents = clean_documents(DOCS)
    runners = {"a1": run_a1, "a2": run_a2, "a3": run_a3, "a4": run_a4, "a5": run_a5}
    for name in selected:
        if name not in runners:
            raise ValueError(f"unknown experiment {name!r}, choose from {sorted(runners)}")
        runners[name](documents)


if __name__ == "__main__":
    main()
