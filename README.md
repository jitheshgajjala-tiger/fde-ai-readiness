# fde-ai-readiness

Hands-on readiness exercises for moving from data engineering toward forward-deployed engineering (FDE), with an emphasis on AI-native workflows and Databricks applications.

## Project map

- [`Data_Engineer_to_FDE_Readiness_Framework.md`](Data_Engineer_to_FDE_Readiness_Framework.md): concept guide and assignment index.
- [`assignments/`](assignments/): scenario instructions and evidence write-ups for six topics.
- [`section_01_agentic_ai_coding_assistants/`](section_01_agentic_ai_coding_assistants/): Python examples for Section 1 coding-standards exercises.
- [`section_03_rag/`](section_03_rag/): local RAG implementation and repeatable experiments for Section 3.
- [`databricks_sections_02_04_05_06/`](databricks_sections_02_04_05_06/): shared Databricks setup and notebooks for Sections 2, 4, 5, and 6. The numbered notebooks stay together because they use relative `%run` dependencies; app and agent-evaluation code have Section 5/6 subfolders.
- [`.github/`](.github/): repository instructions, reusable prompt and STTM validation skill.

## Local RAG app

From `section_03_rag/`, install dependencies, run tests, and try a question:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python main.py "How is order_total calculated?"
```

The first dense-retrieval run downloads the embedding model. See `section_03_rag/results.txt` for the recorded experiment output.

## Databricks exercises

See [`databricks_sections_02_04_05_06/README.md`](databricks_sections_02_04_05_06/README.md) for workspace setup, run order, cost hygiene and the status of the live exercises. Never commit credentials, tokens, or `.databrickscfg`.

## Current progress

- Topic 1: write-ups and starter artifacts are present; several clean-session verification steps remain.
- Topic 2: Genie setup guide and notebooks are prepared; workspace execution and assignment write-ups remain.
- Topic 3: local RAG scenarios are implemented and documented; run the final grounded-prompt check in an LLM.
- Topic 4: live AI Search results for all five scenarios are recorded in the assignment files.
- Topics 5 and 6: starter app/agent artifacts are prepared; deploy, test and document the live scenarios.