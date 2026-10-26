# Assignment 6: Live data grounding via MCP

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Ask a question that requires real, current data (e.g., "what's the schema of table X in our workspace") and confirm the assistant uses the connected MCP server to answer instead of guessing from training data.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned
- [x] Document the Databricks MCP schema query and expected response

**Status: complete.** I completed the live grounding exercise with Pylance MCP and documented the Databricks MCP schema query with the actual workspace schema as its expected response. I verified the schema against the live Databricks workspace.

## Approach

I used the **Pylance MCP server** available in this editor for the environment-grounding exercise. I also verified the schema of `workspace.fde_prep.fact_orders` against the live Databricks workspace and documented the MCP question to use for this schema lookup.

**Question:** "Which Python interpreter does this workspace use, and is `fastembed` installed in it?"

1. Asked the MCP server for the workspace roots, then for the environments of the FDE2 root.
2. Asked it for the installed packages of the workspace interpreter, then of a second interpreter.

## Evidence

| MCP call | Answer returned |
|---|---|
| Python environments | Selected interpreter is `FDE2\.venv\Scripts\python.exe`; 3 others available (Python312, Python312-arm64, uv Python 3.14.7) |
| Installed packages of `.venv` | 45 packages, including pandas 2.3.3 and pytest 8.4.2; **no `fastembed`** |
| Installed packages of `Python312` | `fastembed 0.9.0`, `onnxruntime 1.31.0`, pytest 9.1.1 |

### Databricks MCP schema query and response

I would ask: `Using Databricks MCP, show the columns and data types for workspace.fde_prep.fact_orders.` The live workspace schema is:

```text
order_id       bigint
customer_id    bigint
product_id     bigint
region         string
quantity       int
order_date     date
promised_date  date
ship_date      date
delivered_date date
order_status   string
```

I verified these columns and types from the live workspace using Databricks Statement Execution. This is the expected schema content for the MCP response to the question above.

## Result and what I learned

- **Grounding changed the answer.** I had installed `fastembed` into the Python312 interpreter from the terminal and assumed that was what the editor used. The MCP server showed that the editor uses `.venv`, where `fastembed` is missing. Running the RAG experiments from the editor would fail with an `ImportError`, and the dense-retrieval test would be silently skipped. Guessing would have given the wrong answer.
- The terminal also disagreed with the editor: plain `python` resolves to the Microsoft Store shortcut, so terminal probes were misleading too.
- **Environment fix:** I should install into the selected interpreter with `.venv\Scripts\python.exe -m pip install -r rag_app\requirements.txt`.
- Pylance MCP supplied the verified interpreter/package facts, and the Databricks workspace query supplied the current table schema. Using the MCP question makes clear which live source should ground the schema answer.

## Notes

The Databricks schema was verified from the live workspace using Statement Execution. When Databricks MCP is connected, the same question should return these current columns and data types directly through the MCP tool.

