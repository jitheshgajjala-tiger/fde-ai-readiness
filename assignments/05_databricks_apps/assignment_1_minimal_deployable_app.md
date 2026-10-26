# Assignment 1: Minimal deployable app

**Section:** 5. Databricks Apps

Deploy a basic Databricks App (Streamlit or Gradio) that runs a simple query against a SQL warehouse and displays the result — no hardcoded credentials.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (deployment and query results)
- [x] Result and what I learned

## Notes

Deployed the Streamlit app `fde-ai` with the `sql-warehouse` resource and table `workspace.fde_prep.fact_orders`. Clicking **Load orders** returned order rows in the app while it ran as the app service principal. The app uses the Databricks SQL connector and app resource configuration; no credentials are hardcoded in the source.

The first attempt failed because the app service principal lacked `USE SCHEMA` on `workspace.fde_prep`. After granting the required Unity Catalog permissions, the query succeeded and returned columns including `order_id`, `region`, dates, and `order_status`.

