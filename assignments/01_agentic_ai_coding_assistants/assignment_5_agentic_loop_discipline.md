# Assignment 5: Agentic loop discipline

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Give the assistant a bug report with no other context. Require it to (a) reproduce/diagnose using tools before editing anything, (b) propose a fix, (c) apply the fix, and (d) verify with a test or `get_errors` — reject any output that skips the verify step.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned

## Approach

**Bug report (given with no other context):** "Asking the RAG app a question made only of stop words, such as 'what is the', returns a cited answer instead of refusing."

The loop, with the verify step required before finishing:

| Step | What was done |
|---|---|
| (a) Reproduce | Ran a script that retrieves and answers "what is the". Output: `top score: 0` and a returned chunk from `dq_rules.md`. Bug confirmed before editing anything. |
| Diagnose | The stop words are removed, so the query vector is empty and every chunk scores 0. `answer_from_hits` kept chunks with `s >= min_score`, and its default `min_score` is 0.0, so zero-score chunks passed and the first one was cited. |
| (b) Propose | Require `s > 0` in `answer_from_hits`. This is the smallest change and the answer layer is the right place to refuse. |
| (c) Apply | One line changed in `rag_app/rag.py` (`s > 0 and s >= min_score and ...`). |
| (d) Verify | Added regression test `test_stopword_only_query_is_refused`; `pytest` gave 10 passed; the editor error check on `rag.py` and `test_rag.py` reported no errors. |

## Evidence

Before the fix: `Q: what is the | top score: 0` followed by an answer starting `# Data Quality Rules Register ...`.
After the fix: test suite `10 passed`, including the new regression test.

## Result and what I learned

- Reproducing first showed the real cause (an empty query vector), which is not obvious from the symptom.
- The test is the proof: it fails on the old code and passes on the new.
- `retrieve` still returns zero-score chunks as filler; I left that alone because the ranking function is correct and the answer layer is where refusal belongs.
- **Caveat:** I found this bug myself while building the RAG app, so the bug report was not truly independent. For a stricter test, give another bug report to a fresh chat and reject any answer that skips the reproduce or verify step.

## Notes

