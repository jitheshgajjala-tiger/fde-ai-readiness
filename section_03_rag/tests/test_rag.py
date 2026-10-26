import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag import (
    NOT_FOUND_MESSAGE,
    Chunk,
    answer,
    answer_from_hits,
    build_chunks,
    build_dense_index,
    build_index,
    build_prompt,
    clean_documents,
    retrieve,
    retrieve_hybrid,
)

DOCS = Path(__file__).resolve().parents[1] / "docs"
HAS_DENSE = importlib.util.find_spec("fastembed") is not None


@pytest.fixture(scope="module")
def index():
    return build_index(build_chunks(clean_documents(DOCS)))


def test_answer_cites_correct_source(index):
    result = answer(index, "How is order_total calculated?")
    assert "orders_sttm.md#" in result


def test_unanswerable_question_is_refused(index):
    assert answer(index, "Who won the football world cup?") == NOT_FOUND_MESSAGE


def test_stopword_only_query_is_refused(index):
    assert answer(index, "what is the", min_score=0.0) == NOT_FOUND_MESSAGE


def test_doc_type_filter_limits_results(index):
    hits = retrieve(index, "cancelled orders", top_k=5, doc_type="policy")
    assert hits and all(chunk.doc_type == "policy" for chunk, _ in hits)


def test_coverage_gate_refuses_partial_match():
    chunk = Chunk("returns_policy.md#0", "returns_policy.md", "policy", "Refunds are issued to the original payment method.")
    question = "What is the refund policy for cryptocurrency payments?"
    assert answer_from_hits(question, [(chunk, 0.8)]) != NOT_FOUND_MESSAGE
    assert answer_from_hits(question, [(chunk, 0.8)], min_coverage=0.9) == NOT_FOUND_MESSAGE


def test_prompt_contains_sources_and_refusal_instruction():
    chunk = Chunk("a.md#0", "a.md", "policy", "Returns are accepted within 30 days.")
    prompt = build_prompt("How long do I have to return an item?", [(chunk, 0.9)])
    assert "[a.md#0] Returns are accepted within 30 days." in prompt
    assert NOT_FOUND_MESSAGE in prompt


def test_prompt_without_hits_raises():
    with pytest.raises(ValueError, match="hits is empty"):
        build_prompt("anything", [])


@pytest.mark.skipif(not HAS_DENSE, reason="fastembed not installed")
def test_hybrid_finds_exact_rule_id():
    chunks = build_chunks(clean_documents(DOCS), 20, 10)
    hits = retrieve_hybrid(build_dense_index(chunks), build_index(chunks), "DQ-4107 rule", 1)
    assert "DQ-4107" in hits[0][0].text


def test_missing_docs_folder_raises():
    with pytest.raises(FileNotFoundError, match="documents folder"):
        clean_documents(DOCS / "nope")


def test_invalid_overlap_raises():
    with pytest.raises(ValueError, match="chunking config"):
        build_chunks([{"source": "x", "doc_type": "g", "text": "a b c"}], chunk_size=5, overlap=5)
