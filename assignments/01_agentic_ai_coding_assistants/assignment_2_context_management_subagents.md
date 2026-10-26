# Assignment 2: Context management with subagents

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Take a task that requires exploring an unfamiliar part of the codebase before making a change (e.g., "find every place a given config value is used and update it"). Delegate the investigation to a subagent, and only bring the final file list back into your main session.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned
- [x] Apply an actual update to the listed files and verify the code references

## Approach

**Task:** find every place that uses the baseline chunking configuration (80 words, overlap 15) and the refusal threshold `min_score=0.55`, across code, tests and markdown, before changing either value.

**Delegation:** I gave the whole search to a read-only `Explore` sub-agent with strict output rules: no file contents, only `path:line - kind` lines, plus a file count. Only that compact list came back into the main session.

## Evidence

Initial compact result returned by the sub-agent: 8 files.

| Value | Where |
|---|---|
| chunking 80/15 (code) | `section_03_rag/experiments.py` lines 61, 71, 101; `section_03_rag/main.py` lines 20 and 21 (CLI defaults) |
| chunking 80/15 (prose) | `section_03_rag/experiments.py` lines 60 and 100 (headers), `section_03_rag/results.txt`, `assignment_1_baseline_pipeline.md`, `assignment_2_chunking_tradeoffs.md` |
| min_score 0.55 (code) | `section_03_rag/experiments.py` lines 105, 111, 114 |
| min_score 0.55 (prose) | `section_03_rag/results.txt`, `assignment_4_groundedness_failure_hunt.md` |

I re-checked the code hits with a search in the main session; the line numbers matched.

## Result and what I learned

- The main conversation received about 25 lines instead of every file the sub-agent read, so the context stayed small.
- The list showed something I would have missed: the values are hardcoded in **two places in code plus prose in 4 other files**. Changing the value in code alone would leave `results.txt` and both assignment write-ups stating the old configuration. That is a concrete argument for a single constant.
- A sub-agent is stateless, so the prompt must say exactly what format to return. Without the format rule I would have received file dumps.
- **Update applied without changing experiment settings:** centralized the baseline chunk size, overlap and score threshold as constants in `section_03_rag/rag.py`; the experiment and CLI code now reference those constants. The historical experiment outputs and their stated configurations were left unchanged.
- Re-ran the bounded search after the edit. `rag.py` now owns the definitions; `experiments.py` and `main.py` import and reference them. No duplicate executable baseline settings remain. `results.txt` and the assignment write-ups retain literal values as historical experiment evidence.

## Notes

