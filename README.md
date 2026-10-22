# fde-ai-readiness

Hands-on readiness exercises for moving from data engineering toward forward-deployed engineering (FDE), with an emphasis on AI-native workflows and Databricks applications.

## Project map

- [`Data_Engineer_to_FDE_Readiness_Framework.md`](Data_Engineer_to_FDE_Readiness_Framework.md): concept guide and assignment index.
- [`assignments/`](assignments/): scenario instructions and evidence write-ups for six topics.
- [`rag_app/`](rag_app/): local RAG implementation and repeatable experiments for Topic 3.
- [`databricks_prep/`](databricks_prep/): seed data, notebooks, app starter and runbook for Databricks-dependent topics.
- [`topic1_demo/`](topic1_demo/): small Python examples for the coding-standards exercise.
- [`.github/`](.github/): repository instructions, reusable prompt and STTM validation skill.

## Local RAG app

From `rag_app/`, install dependencies, run tests, and try a question:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python main.py "How is order_total calculated?"
```

The first dense-retrieval run downloads the embedding model. See `rag_app/results.txt` for the recorded experiment output.

## Databricks exercises

See [`databricks_prep/README.md`](databricks_prep/README.md) for workspace setup, run order, cost hygiene and the status of the live exercises. Never commit credentials, tokens, or `.databrickscfg`.

## Current progress

- Topic 1: write-ups and starter artifacts are present; several clean-session verification steps remain.
- Topic 2: Genie setup guide and notebooks are prepared; workspace execution and assignment write-ups remain.
- Topic 3: local RAG scenarios are implemented and documented; run the final grounded-prompt check in an LLM.
- Topic 4: live AI Search results for all five scenarios are recorded in the assignment files.
- Topics 5 and 6: starter app/agent artifacts are prepared; deploy, test and document the live scenarios.