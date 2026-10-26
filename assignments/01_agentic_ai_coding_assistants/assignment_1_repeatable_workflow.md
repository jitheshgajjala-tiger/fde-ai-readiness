# Assignment 1: Repeatable workflow

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Pick a task you do manually every week (e.g., generating a code review checklist, or scaffolding a new notebook). Build a slash command/prompt file for it and run it twice on two different inputs to prove it's reusable.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (recorded outputs and review notes)
- [x] Result and what I learned
- [x] Run `/review-pipeline-step` in Copilot Chat on two targets and record the results

## Approach

**Task I repeat:** reviewing a pipeline function against the team conventions (naming, error handling, logging) and checking its tests.

**Slash command:** `.github/prompts/review-pipeline-step.prompt.md`. It takes two inputs, `file` and `function`, reads `.github/copilot-instructions.md`, marks PASS/FAIL per convention with line numbers, lists untested behaviours, and proposes at most 3 fixes. It is read-only.

**Two runs on different inputs.** I ran the slash command directly in Copilot Chat for both targets. I first reviewed the prompt behavior, then verified the workflow with these two direct runs:

| Run | Input | Result |
|---|---|---|
| 1 | `section_03_rag/rag.py` `clean_documents` | Naming PASS. Error handling PASS. Logging FAIL: logs loaded count at the end, but not at the start. Untested: empty-file and no-supported-files errors; nested-folder `doc_type`. |
| 2 | Customer 360 `starter_pipeline.py` `clean_orders` | Naming PASS. Error handling FAIL for malformed values because `errors="coerce"` silently converts them; required columns are validated by `load_sources` before the normal call. Logging FAIL: no module logger or row-count logs in this function. Untested: malformed values, direct-call missing columns, and invalid input types. |

## Result and what I learned

- The same prompt gave two structured, comparable reports on unrelated code, so it is reusable. Only the two inputs changed.
- **I checked an incorrect finding.** An initial review claimed `clean_orders` has "no input validation". I checked its caller and found that `load_sources` validates required columns (lines 60 to 66) before the normal call; the initial review's line numbers were also off by a few. The prompt should tell reviewers to inspect the caller before reporting missing validation.
- Run 1's logging finding is valid and cheap to fix.

## Notes

I ran `/review-pipeline-step` directly in Copilot Chat on both targets. The returned findings are recorded below.

- `section_03_rag/rag.py` / `clean_documents`: Naming PASS; error handling PASS; logging PARTIAL because the function reports the loaded document count at the end but does not log at entry. Tests cover a missing directory, but not an empty document or a directory with no supported files.
- Customer 360 `starter_pipeline.py` / `clean_orders`: Naming PASS; logging FAIL because the module has no logger or row-count logs; numeric/date parsing uses `errors="coerce"`, so malformed values are not reported. Tests cover valid discounted revenue, not malformed values.

**Validation correction:** an initial review incorrectly reported that required-column validation was missing. I checked `load_sources`, which validates the required `orders` columns before calling `clean_orders`. The remaining concern is malformed values, which column-presence checks do not validate.

Both required direct command runs are complete, and I recorded their findings above.

