# Databricks prep (Sections 2, 4, 5, 6)

Workspace setup and a baseline AI Search query have been run. Verified resources include the three order tables, two
Unity Catalog functions, the 24-row document-chunks table, the standard AI Search endpoint, and the Delta Sync index.
The baseline query returned three chunks. Record each remaining experiment's actual output in its assignment file;
don't infer or copy expected values as observed results. Local seed/eval tests passed (24 tests). The notebooks were
checked against the Databricks docs on 2026-10-18; expect small fixes when workspace APIs change.

Product names changed in the docs: Genie Spaces are now **Genie Agents**, Vector Search is now **AI Search**
(`pip install databricks-ai-search`). The assignment files still use the old names.

## Day plan (order matters)
| Step | Do this | Needs |
|---|---|---|
| 0 | Import `notebooks/` into the workspace (Workspace, Import, the folder). Keep all files in one folder: `%run ./x` needs it. | |
| 1 | Run `01_preflight`. Fill `SQL_WAREHOUSE_ID` and confirm model endpoint names in `00_config`. | Compute |
| 2 | Run `02_seed_gold_tables`. | SQL warehouse or serverless |
| 3 | **Section 2 (Genie):** follow `genie_space_setup.md`; then `03_genie_governance` and `04_genie_api`. | A second user for A3 |
| 4 | **Section 4 (AI Search):** run `05_seed_doc_chunks`, then `06_ai_search` cell by cell. | Serverless, AI Search endpoint |
| 5 | **Section 5 (Apps):** deploy `app/`, then add one feature at a time. | Apps enabled |
| 6 | **Section 6 (Agents):** run `07_uc_functions`, then `08_agent`. | Chat model endpoint |

Do Section 2 before 5 and 6 (they reuse the Genie space), and Section 4 before 6 (the docs tool uses the index).

## What to capture per assignment
Screenshot or paste the printed output, then fill the Approach, Evidence, Result checklist in `assignments/<topic>/`.
Write what **failed** too; the Topic 3 write-ups show the expected level of honesty.

### Save and publish Section 4 results
1. In the Databricks notebook, copy the relevant cell output (include query, filter/top-k, result rows and scores) into the matching `assignments/04_vector_database_databricks/assignment_N_*.md` file under **Evidence**.
2. Under **Result and what I learned**, write the observed conclusion, including any failures or unexpected ranking. Do not substitute the expected result for the actual output.
3. For screenshot evidence, create `assignments/04_vector_database_databricks/evidence/` and save files such as `a2_freshness.png`. Link them from the assignment markdown: `[freshness result](evidence/a2_freshness.png)`.
4. To preserve the full run, use the Databricks notebook menu **File → Export → IPython Notebook**, then save the exported `.ipynb` in that `evidence/` folder. Keep the short text summary in the assignment file so reviewers can see the result without opening the notebook.
5. Review the five assignment files, then commit the markdown and evidence files to the repo or publish the repo branch/PR. Never include tokens, secrets, or private customer data in the exported notebook or screenshots.

## Section 5: Apps
1. Compute, Apps, Create app (custom). Upload `app/` (or sync it from the CLI).
2. Add a **SQL warehouse** resource with the key `sql-warehouse`. Edit `ORDERS_TABLE` in `app.yaml` to your catalog.
3. Grant the app's service principal `USE CATALOG`, `USE SCHEMA` and `SELECT` on `fact_orders` (Authorization tab shows its id).
4. A1: deploy and click **Load orders**. No credentials appear in the code.
5. A2: add a **Genie** resource (key `genie-space`), uncomment the `GENIE_SPACE_ID` block, redeploy.
6. A3: add a **serving endpoint** resource (key `serving-endpoint`), uncomment `SERVING_ENDPOINT`, redeploy. Test the failure case by pointing it at a wrong name or a stopped endpoint and confirm the UI shows a friendly message.
7. A4: set `USE_USER_AUTH` to `true`, add the `sql` (and `genie`) user authorization scopes in the app settings, and apply the row filter from `03_genie_governance`. Open the app as two users: the rows must differ without any app code change.
8. A5: make three changes one at a time and redeploy after each: a region filter, a chart, an export button. Write down what you checked after each.

CLI syntax for sync and deploy was not verified; check `databricks apps --help` before relying on it.

## Section 6: Agents
* A1: `ENABLED_TOOLS` has the two UC functions. Expect the lookup questions to pass and the aggregate and document questions to fail.
* A2: add `"ask_genie"` and `"search_docs"` to `ENABLED_TOOLS`, rerun the eval. The `needs` column shows which questions each tool unlocks.
* A3: the eval is the 14 questions in `agent_eval/eval_set.jsonl`. The loop scores with a simple whole-token match; if you want LLM judges, run the same questions through MLflow evaluation as an extra step and document at least one failure.
* A4: set `BREAK_TOOL = True` in `07_uc_functions`, rerun, then find the bad span in the MLflow trace without opening the agent code. Restore afterwards.
* A5 (deployment): **not prepared**. Databricks now documents an Agent Bricks CLI path and a legacy Model Serving path; read the current "Deploy agents on Databricks" page on the day and choose the one your workspace supports.

## If something is unavailable (for example on a free workspace)
Run `01_preflight` first; it reports which features are missing. Likely fallbacks: no AI Search endpoint means do Section 4 in the UI only if
it is offered, otherwise document the limit; no custom serving endpoints means skip A5 deployment and record why.

## Cost hygiene
AI Search endpoints and Genie warehouses bill while they exist or run. The last cell of `06_ai_search` lists the delete calls (commented out). Stop the warehouse and delete the endpoint when you finish each day.

## Files
* `notebooks/`: Databricks source notebooks (`seed_data.py`, `seed_chunks.py` and `eval_data.py` are generated or shared data).
* `app/`: Streamlit app, `app.yaml`, `requirements.txt`.
* `agent_eval/eval_set.jsonl`: evaluation questions, built by `build_eval_set.py` from the seed data.
* `make_chunk_seed.py`, `build_eval_set.py`, `tests/`: local helpers; run `python -m pytest -q` here.
