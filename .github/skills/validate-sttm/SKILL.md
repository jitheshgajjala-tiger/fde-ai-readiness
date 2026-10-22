---
name: validate-sttm
description: 'Validate a source-to-target mapping (STTM) markdown document for completeness. Use when asked to check, review, lint, QA or sign off an STTM, a mapping spec, or a "gold table load" document, e.g. "is this mapping doc complete", "check the orders STTM before I hand it over".'
---

# Validate an STTM file

Use this when a user wants to know whether an STTM document (a markdown file describing how a gold table is loaded from its source) is complete and consistent.

## When to use
- The user names or opens a file ending in `_sttm.md`, or under a `sttm/` folder.
- The user asks to check, review, QA or sign off a mapping or load specification.

Do not use it for DRD or policy documents; they have a different structure.

## Steps
1. Run the checker on the file or folder (from the repository root):
   `python .github/skills/validate-sttm/validate_sttm.py <path-to-file-or-folder>`
   If `python` is not found, locate the interpreter first; do not guess a path.
2. Read the report. Each document gets one line per check marked `PASS`, `WARN` or `FAIL`. The exit code is 1 when any check is `FAIL`.
3. For every `FAIL` or `WARN`, quote the missing element and say what sentence should be added to the document. Do not edit the document unless the user asks.
4. Summarise per document: ready / not ready, followed by the list of gaps.

## What the checks mean
| Check | Level | Rule |
|---|---|---|
| `title` | FAIL | First line is `# <Name> STTM` |
| `target_table` | FAIL | Names the target as `gold.<table>` |
| `load_schedule` | FAIL | States a load time such as `02:00 UTC` |
| `source` | FAIL | A sentence saying loaded or refreshed `from` a source |
| `column_rules` | WARN | At least one `The column <name> ...` transformation rule |
| `reject_handling` | WARN | Says what happens to bad rows (rejected, quarantined) |

## Conventions
The checker follows the repo rules in `.github/copilot-instructions.md`: it raises `FileNotFoundError` or `ValueError` with the source named, and logs counts through `logging`.
