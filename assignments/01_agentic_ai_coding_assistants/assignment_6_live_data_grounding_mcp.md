# Assignment 6: Live data grounding via MCP

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Ask a question that requires real, current data (e.g., "what's the schema of table X in our workspace") and confirm the assistant uses the connected MCP server to answer instead of guessing from training data.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned
- [ ] Repeat with a Databricks MCP server once a workspace exists (schema of a real table)

## Approach

There is no Databricks workspace yet, so I used the MCP server that is available in this editor, the **Pylance MCP server**, as the live system. It exposes real facts about the machine that cannot be known from training data.

**Question:** "Which Python interpreter does this workspace use, and is `fastembed` installed in it?"

1. Asked the MCP server for the workspace roots, then for the environments of the FDE2 root.
2. Asked it for the installed packages of the workspace interpreter, then of a second interpreter.

## Evidence

| MCP call | Answer returned |
|---|---|
| Python environments | Selected interpreter is `FDE2\.venv\Scripts\python.exe`; 3 others available (Python312, Python312-arm64, uv Python 3.14.7) |
| Installed packages of `.venv` | 45 packages, including pandas 2.3.3 and pytest 8.4.2; **no `fastembed`** |
| Installed packages of `Python312` | `fastembed 0.9.0`, `onnxruntime 1.31.0`, pytest 9.1.1 |

## Result and what I learned

- **Grounding changed the answer.** I had installed `fastembed` into the Python312 interpreter from the terminal and assumed that was what the editor used. The MCP server showed that the editor uses `.venv`, where `fastembed` is missing. Running the RAG experiments from the editor would fail with an `ImportError`, and the dense-retrieval test would be silently skipped. Guessing would have given the wrong answer.
- The terminal also disagreed with the editor: plain `python` resolves to the Microsoft Store shortcut, so terminal probes were misleading too.
- **Fix for the user:** install into the selected interpreter with `.venv\Scripts\python.exe -m pip install -r rag_app\requirements.txt`.
- **Limit of this evidence:** this is a local-environment MCP server, not Databricks. It proves the pattern (ask the tool, do not guess), but the assignment's example of a table schema from a workspace still needs a Databricks MCP server to be attached later.

## Notes

The Databricks-specific repeat was attempted with: "Using the connected Databricks MCP server, show the columns and data types for `workspace.fde_prep.fact_orders`." The first response said no Databricks MCP tool was connected in that chat, so it could not query the live schema.

After adding the legacy SQL MCP endpoint to the VS Code workspace configuration and enabling Managed MCP Servers, OAuth sign-in was attempted. Databricks returned `invalid_request`: the OAuth application with client ID `http://127.0.0.1:33418 https://vscode.dev/redirect` was not available in the Databricks account. The authorization URL included the SQL MCP endpoint and requested the `sql` scope. The error screenshot was supplied in chat and is retained as evidence of the current blocker.

Per the user's request, stop setup here: leave the existing MCP configuration unchanged and do not proceed with OAuth app registration. No live table schema was returned, so the Databricks-specific deliverable remains open.

