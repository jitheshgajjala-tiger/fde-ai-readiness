# Assignment 1: Repeatable workflow

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Pick a task you do manually every week (e.g., generating a code review checklist, or scaffolding a new notebook). Build a slash command/prompt file for it and run it twice on two different inputs to prove it's reusable.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned
- [ ] Run `/review-pipeline-step` yourself in Copilot Chat on two targets and add a screenshot (not done yet)

## Approach

**Task I repeat:** reviewing a pipeline function against the team conventions (naming, error handling, logging) and checking its tests.

**Slash command:** `.github/prompts/review-pipeline-step.prompt.md`. It takes two inputs, `file` and `function`, reads `.github/copilot-instructions.md`, marks PASS/FAIL per convention with line numbers, lists untested behaviours, and proposes at most 3 fixes. It is read-only.

**Two runs on different inputs.** I executed the prompt body twice through two independent read-only sub-agents (not through the `/` command itself):

| Run | Input | Result |
|---|---|---|
| 1 | `rag_app/rag.py` `clean_documents` | Naming PASS. Error handling PASS. Logging partial: logs row count at the end only, no start-of-step log. Untested: empty-file error and no-valid-files error. |
| 2 | Customer 360 `starter_pipeline.py` `clean_orders` | Naming PASS. Logging FAIL: no `logger`, no row counts, and `print()` in `main()` (line 198). `errors="coerce"` silently turns bad values into 0 or NaT. Untested: invalid amounts and dates. |

## Result and what I learned

- The same prompt gave two structured, comparable reports on unrelated code, so it is reusable. Only the two inputs changed.
- **The reviewer was partly wrong, so I checked it.** Run 2 claimed `clean_orders` has "no input validation". In fact required columns are validated in `load_sources` (lines 60 to 66), one step earlier, and the sub-agent's line numbers were off by a few. The prompt should tell the reviewer to look at the caller before reporting missing validation.
- Run 1's logging finding is valid and cheap to fix.

## Evidence note

The two reports above are summarised from the sub-agent outputs. For proper evidence, type `/review-pipeline-step` in Copilot Chat, fill in the two inputs, and screenshot each run.

## Notes

