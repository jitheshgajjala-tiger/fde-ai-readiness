# Assignment 1: Baseline pipeline

**Section:** 3. Retrieval-Augmented Generation (RAG)

Build a RAG pipeline over a small internal document set (e.g., a handful of STTM/DRD documents): chunk, embed, index, retrieve, and answer 5 test questions with citations back to the source chunk.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned

## Approach

Code: `rag_app/rag.py`, run with `rag_app/experiments.py a1`. No Databricks needed; everything runs locally.

1. **Documents:** 7 short docs in `rag_app/docs/` in three folders (`sttm/`, `drd/`, `policy/`). The folder name becomes the `doc_type` metadata.
2. **Chunk:** `build_chunks` splits on words (80 words, overlap 15).
3. **Embed:** local ONNX model `BAAI/bge-small-en-v1.5` (384 dimensions) via `fastembed`.
4. **Index:** unit-normalised matrix held in memory.
5. **Retrieve:** cosine similarity, top-1.
6. **Answer:** extractive. It returns the retrieved chunk with a citation `[chunk_id, score]`. There is no LLM, so there are no generated words that could be hallucinated.

## Evidence

Full output: `rag_app/results.txt` (section A1).

| # | Question | Cited chunk | Score | Correct chunk? |
|---|---|---|---|---|
| 1 | How is order_total calculated? | `orders_sttm.md#0` | 0.78 | Yes |
| 2 | What time does the nightly orders load run? | `orders_sttm.md#0` | 0.67 | Yes |
| 3 | Within how many days can unused products be returned? | `returns_policy.md#0` | 0.86 | Yes |
| 4 | How is the customer segment determined? | `customers_sttm.md#0` | 0.66 | Yes |
| 5 | Who can see which regions in the sales dashboard? | `sales_dashboard_drd.md#0` | 0.77 | Yes |

"Correct" means the chunk contains the expected fact (checked by a phrase match in code).

## Result and what I learned

- 5 of 5 questions were answered with the right source cited.
- Question 2 shares no key words with its answer ("nightly" vs "every night at 02:00 UTC"). A first TF-IDF-only version retrieved the shipping policy for it. Embeddings handled it, which is the main reason to embed.
- Because the docs are short, an 80-word chunk is almost a whole document. The answer is right but the returned text is much longer than the one sentence needed (see Assignment 2).
- Cosine scores from this model sit between roughly 0.5 and 0.85. A raw score is a weak sign of "answerable" (see Assignment 4).

## Notes

