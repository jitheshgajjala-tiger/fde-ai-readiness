# Assignment 4: Enforcing standards automatically

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Write a custom instructions file (`*.instructions.md` or `CLAUDE.md`) that encodes 3 real team coding conventions (naming, error handling, logging pattern). Verify the assistant follows all 3 without being reminded, across two unrelated code-generation requests.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned
- [ ] Repeat the two requests in a fresh Copilot Chat as a clean test (see caveat)

## Approach

**Instructions file:** `.github/copilot-instructions.md` (loaded automatically for every request) encodes three conventions:
1. **Naming:** `snake_case`; `clean_<source>` and `build_<output>`; private helpers prefixed `_`.
2. **Error handling:** validate at the boundary; `ValueError` or `FileNotFoundError` naming the source; no bare `except`.
3. **Logging:** `logger = logging.getLogger(__name__)`; no `print()` in library code; row counts at the start and end of each step.

**Two unrelated requests, with no reminder of the rules:**
1. "Write a function that cleans a CSV of support tickets" gave `topic1_demo/clean_tickets.py`.
2. "Write a function that totals revenue per day from order dicts" gave `topic1_demo/build_daily_revenue.py`.

## Evidence

| Convention | `clean_tickets.py` | `build_daily_revenue.py` |
|---|---|---|
| Naming | `clean_tickets`, helper `_normalize_priority` | `build_daily_revenue` |
| Error handling | `FileNotFoundError("tickets file not found: ...")` and `ValueError("tickets is missing required columns: ...")` | `ValueError("orders row N is missing required keys: ...")` |
| Logging | `logger = logging.getLogger(__name__)`, row count in and out | same pattern, rows in and days out |
| No `print()`, no bare `except` | confirmed by a text search of both files | confirmed |

## Result and what I learned

- Both files follow all three conventions even though the requests were unrelated and never mentioned them.
- The error messages name the source ("tickets", "orders"), as the rule requires.
- **Caveat:** I wrote these files in the same session where the instructions file was already attached to my context, and I checked compliance with a text search, not by running the code. For a clean test, open a new Copilot Chat, make the two requests yourself, and run the same search.
- Not covered by the file: the instructions say nothing about tests or type hints, so those vary from request to request.

## Notes

