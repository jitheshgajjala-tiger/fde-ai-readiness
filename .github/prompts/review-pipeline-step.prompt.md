---
description: Review one Python pipeline function against the repo conventions and report findings (read-only)
agent: agent
argument-hint: <file path> <function name>
---

Review the function `${input:function:function name}` in `${input:file:workspace-relative file path}`. Do not edit any file.

1. Read `.github/copilot-instructions.md` and the function.
2. Check each convention and mark PASS, FAIL or N/A with the line number:
   - **Naming:** `snake_case`; cleaning functions `clean_<source>`; aggregations `build_<output>`; private helpers prefixed `_`.
   - **Error handling:** input validated at the boundary; `ValueError` or `FileNotFoundError` with a message that names the source; no bare `except`; no silently swallowed errors.
   - **Logging:** module-level `logger = logging.getLogger(__name__)`; no `print()` in library code; row counts logged at the start and end of the step.
3. Find the tests that cover the function (search the `tests/` folder) and say which behaviours are untested.
4. Report as: a table of the checks, then at most 3 concrete fixes ordered by impact. Quote the exact line for each fix.
