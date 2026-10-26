# Assignment 2: Multi-tool composition

**Section:** 6. Databricks Agent Creation (Mosaic AI Agent Framework)

Extend the agent from Assignment 1 to also use a vector search retriever (Section 4) or a Genie conversation (Section 2) as a second tool, and test it with questions that require each tool separately, plus one question that requires both.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (combined-question answer and MLflow trace)
- [x] Result and what I learned

## Notes

In the expanded run, `ENABLED_TOOLS` included `get_order_status`, `get_late_days`, `ask_genie`, and `search_docs`. The agent was asked: `How many orders were cancelled, and how many days do customers have to return unused products?`

Observed answer: **2 cancelled orders**; unused products may be returned within **30 days** for a full refund.

The MLflow trace breakdown shows both `ask_genie` and `search_docs` tool spans for this same question, followed by the final combined response. The separate-tool evaluation also passed all 7 Genie-tagged and both docs-tagged questions.

## Result and what I learned

- The agent composed a structured-data answer from Genie with a policy fact from document search in one response.
- The trace confirms both tools were used, rather than relying only on the answer text to infer tool use.
- The expanded evaluation supports the individual tool paths; the combined trace demonstrates their composition.

