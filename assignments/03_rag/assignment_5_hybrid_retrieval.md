# Assignment 5: Hybrid retrieval

**Section:** 3. Retrieval-Augmented Generation (RAG)

Combine keyword search with semantic (vector) search for one query where pure semantic search underperforms (e.g., an exact code/ID lookup), and show the improvement.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned

## Approach

Run with `python experiments.py a5` in `rag_app/`.

- **Corpus:** `docs/drd/dq_rules.md`, six data quality rules with near-identical wording and codes such as DQ-1047, DQ-1074, DQ-1407 and DQ-1470. This is a hard case for embeddings.
- **Semantic retriever:** `BAAI/bge-small-en-v1.5` embeddings.
- **Keyword retriever:** TF-IDF on word tokens (not BM25).
- **Hybrid:** `retrieve_hybrid` fuses the two rankings with Reciprocal Rank Fusion (RRF, k=60).
- **Test set:** 9 queries, 6 exact-ID lookups and 3 paraphrases with no shared rule code. Chunks are 20 words with overlap 10. A query passes if the top-1 chunk contains the expected rule ID.

## Evidence

| query | kind | dense | keyword | hybrid |
|---|---|---|---|---|
| DQ-1470 | exact id | PASS | PASS | PASS |
| What does rule DQ-1470 check? | exact id | PASS | PASS | PASS |
| rule DQ-4170 | exact id | PASS | PASS | PASS |
| Explain DQ-1407 | exact id | PASS | PASS | PASS |
| what is DQ-1074 | exact id | PASS | PASS | PASS |
| DQ-4107 rule | exact id | **FAIL** | PASS | PASS |
| which check blocks duplicated order identifiers? | paraphrase | PASS | **FAIL** | PASS |
| what validates that the product code is known? | paraphrase | FAIL | FAIL | FAIL |
| which rule prevents negative totals? | paraphrase | PASS | PASS | PASS |
| **total** | | 7/9 | 7/9 | **8/9** |

## Result and what I learned

- **Hybrid scored 8/9 against 7/9 for each retriever alone.** The two single retrievers failed on *different* queries, which is why fusing them helps.
- **Dense failed on an exact code:** "DQ-4107 rule" returned a different rule, because the embeddings of near-identical rule sentences are almost the same (in a quick check with 20-word, no-overlap chunks, the top three scores were 0.69, 0.69 and 0.67). The keyword side matched the exact token and fixed it.
- **Keyword failed on a paraphrase:** "duplicated order identifiers" shares no word with "order_id is unique". The dense side fixed it.
- **Fusion cannot fix a query that both fail.** "product code is known" is still wrong for both retrievers, so for hybrid as well.
- **Honest caveats:**
  - Dense did better on exact IDs than I expected, since 5 of 6 passed. The improvement is real but small: one query out of nine.
  - I tried three chunk configs before choosing this one. In the other two (24/12 and 30/15), plain keyword scored 7/9 and 8/9, and unweighted hybrid scored 6/9 in both. So hybrid is not automatically better; it depends on chunking and on how the fusion is weighted.
  - Nine queries on a six-rule corpus is a demonstration, not a benchmark.

## Notes

