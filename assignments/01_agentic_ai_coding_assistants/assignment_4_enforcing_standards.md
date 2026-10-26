# Assignment 4: Enforcing standards automatically

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Write a custom instructions file (`*.instructions.md` or `CLAUDE.md`) that encodes 3 real team coding conventions (naming, error handling, logging pattern). Verify the assistant follows all 3 without being reminded, across two unrelated code-generation requests.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned
- [x] Repeat two unrelated code-generation requests in a fresh Copilot Chat and verify the conventions

## Approach

**Instructions file:** `.github/copilot-instructions.md` encodes three conventions:
1. **Naming:** `snake_case`; `clean_<source>` and `build_<output>`; private helpers prefixed `_`.
2. **Error handling:** validate at the boundary; `ValueError` or `FileNotFoundError` naming the source; no bare `except`.
3. **Logging:** `logger = logging.getLogger(__name__)`; no `print()` in library code; row counts at the start and end of each pipeline step.

In a fresh Copilot Chat, two new functions were created in new files rather than reusing the earlier examples:
1. A feedback CSV cleaner, `clean_feedback_csv` in `section_01_agentic_ai_coding_assistants/clean_feedback.py`.
2. A monthly revenue aggregation, `build_monthly_revenue` in `section_01_agentic_ai_coding_assistants/build_monthly_revenue.py`.

## Evidence

I captured the fresh-chat runs as both new files were created. The first response reports checks for CSV/header validation, trimming values, dropping fully blank rows, and input/output row logging. The second reports monthly grouping, required-key and malformed-value validation, and input/output count logging.

| Convention | `clean_feedback.py` | `build_monthly_revenue.py` |
|---|---|---|
| Naming | `clean_feedback_csv`; snake_case variables | `build_monthly_revenue`; snake_case variables |
| Error handling | Checks file existence and CSV header; errors identify `feedback` | Checks required keys and malformed values; errors identify `orders` |
| Logging | Module logger; rows in and rows out | Module logger; rows in and months out |
| No `print()` or bare `except` | Confirmed by code inspection | Confirmed; conversion catches only `TypeError` and `ValueError` |

Both files have no Pylance editor diagnostics, and Pylance syntax checks reported no syntax errors. The Copilot responses I captured also report focused behavior checks passing.

## Result and what I learned

- The fresh chat created two distinct functions in new files, and inspection confirms the three project conventions are represented in both.
- Validation errors name their source, logging records input and output counts, and neither file uses `print()` or a bare `except`.
- Earlier requests that matched existing implementations were not sufficient evidence of code generation; using new functions and files made the clean test more discriminating.
- The instructions do not specify tests or type hints, so those remain task-dependent.

## Notes

I captured both fresh-chat runs as evidence of the generated files and responses. I independently checked the code and editor/syntax diagnostics in the workspace; the focused behavior-test claim comes from the Copilot responses I recorded.

