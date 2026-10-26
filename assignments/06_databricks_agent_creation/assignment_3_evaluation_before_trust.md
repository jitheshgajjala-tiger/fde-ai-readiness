# Assignment 3: Evaluation before trust

**Section:** 6. Databricks Agent Creation (Mosaic AI Agent Framework)

Build a small eval set (10-15 question/expected-answer pairs) covering both easy and edge cases, run the agent through Agent Evaluation, and document at least one failure it surfaced.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (14-question Databricks evaluation output)
- [x] Result and what I learned

## Notes

Ran the 14-row evaluation in `08_agent.py` with all four tools enabled: `get_order_status`, `get_late_days`, `ask_genie`, and `search_docs`. The notebook's deterministic whole-token matcher scored answers against expected strings; this is a lightweight smoke evaluation, not an LLM-judge run.

## Evidence

Observed result with all four tools enabled: **13 of 14 passed**. An earlier run with only the two UC function tools passed 6 of 14; the expanded run below supersedes it as the final evaluation result.

| Tool need | Passed | Total |
|---|---:|---:|
| `docs` | 2 | 2 |
| `genie` | 7 | 7 |
| `none` | 1 | 1 |
| `uc_functions` | 3 | 4 |

Concrete failure: `How many days late was order 1008?` was marked false. The agent answered that order 1008 had not been delivered yet and that it could not determine how many days late it was. That answer is semantically consistent with a cancelled order, but the whole-token matcher did not match the configured expected phrases (`cancel`, `not delivered`, `no delivery`) because the response says “not been delivered.” This is an evaluator wording mismatch, not evidence that the agent invented a late-day value. The evaluation table and MLflow trace are observed evidence.

## Result and what I learned

- Enabling Genie and document search raised the score from 6/14 to 13/14; every Genie and docs-tagged question passed in the expanded run.
- The one failing row exposed a limitation in the exact-match evaluator: a reasonable paraphrase (“not been delivered”) was not covered by its expected phrases.
- This completes the prepared deterministic evaluation. LLM-judge scoring remains an optional stronger follow-up, not part of this measured result.

