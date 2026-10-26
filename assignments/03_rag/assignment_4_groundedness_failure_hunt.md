# Assignment 4: Groundedness failure hunt

**Section:** 3. Retrieval-Augmented Generation (RAG)

Deliberately ask a question the source documents do *not* answer, and confirm the system says so rather than hallucinating an answer. Fix the prompt/pipeline if it doesn't.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (experiment output and recorded prompt replies)
- [x] Result and what I learned
- [x] Run the generated grounded prompt through Copilot Chat and record unanswerable and answerable replies under Notes

## Approach

Run with `python experiments.py a4` in `section_03_rag/`.

1. Asked 4 questions the documents do not answer, using the baseline pipeline (dense top-1, refuse only if score < 0.55).
2. Added a **coverage gate** in `answer_from_hits`. It refuses when too few of the query's content words appear in the cited chunk.
3. Swept the gate threshold on 8 answerable and 4 unanswerable questions.
4. Added `build_prompt`, a grounded prompt with "cite the chunk or reply exactly: I could not find this in the provided documents."

## Evidence

Baseline output on unanswerable questions:

| Question | Baseline behaviour |
|---|---|
| Refund policy for cryptocurrency payments? | **Failure.** Returned the returns policy, which says nothing about crypto. |
| Warranty period for laptops? | **Failure.** Returned the returns policy. |
| Who is the CEO? | Correct refusal (score 0.49 is below 0.55). |
| Data retention period for the orders table? | **Failure.** Returned the orders STTM. |

Coverage gate sweep (8 answerable, 4 unanswerable):

| min_coverage | answerable still answered | unanswerable refused |
|---|---|---|
| 0.0 | 8/8 | 1/4 |
| 0.5 | 6/8 | 3/4 |
| 0.7 | 4/8 | 3/4 |
| 0.8 | 4/8 | 4/4 |

## Result and what I learned

- **The failure is real:** the pipeline answered 3 of 4 unanswerable questions with a confident, cited, but irrelevant chunk. Retrieval always returns *something*, and a cited answer looks trustworthy.
- **A score threshold does not fix it.** Dense scores for answerable and unanswerable questions overlap, so no cut-off separates them (in a quick check with 60-word chunks, the crypto question scored about 0.70 and the answerable customer-segment question about 0.66).
- **The lexical coverage gate is a trade-off, not a fix.** The only setting that refused all 4 (0.8) also dropped 4 of the 8 good answers, because paraphrases ("time" vs "at 02:00 UTC") look like missing words.
- **The real fix belongs in the generation step:** an LLM that is told to answer only from the context and to refuse otherwise. `build_prompt` produces that prompt. The retrieval side only reduces how often the LLM is asked.
- I did not run the prompt through an LLM, so I have no evidence yet that the refusal works. That is the open item above.

## Notes

Prompt test via Copilot Chat:

**Unanswerable question:** “What is the refund policy for cryptocurrency payments?”

**Reply:** “I could not find this in the provided documents.”

This matches the required refusal exactly. The retrieved context contained the general returns policy and shipping policy, but neither mentions cryptocurrency.

**Answerable question:** “Within how many days can unused products be returned?”

**Reply:** “Unused products may be returned within 30 days of delivery for a full refund. [returns_policy.md#0]”

This answer is supported by the cited chunk. Both prompts were generated from the current local RAG index and tested with Copilot; no external model or separate fresh-session test was used.

