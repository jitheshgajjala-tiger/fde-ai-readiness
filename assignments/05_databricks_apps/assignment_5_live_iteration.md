# Assignment 5: Live iteration

**Section:** 5. Databricks Apps

Starting from a working app, make three incremental UI/feature changes (e.g., add a filter, add a chart, add an export button) one at a time, redeploying and validating after each change.

## Deliverables

- [ ] Approach and steps taken
- [ ] Evidence (screenshots, output, or links)
- [ ] Result and what I learned

## Notes

Iteration 1 is deployed and behaviorally verified. The screenshot supplied in chat shows **North** selected and every displayed row has `region = North` (7 matching rows). This confirms the region filter affects the displayed result.

Iteration 2 is prepared locally in `databricks_prep/app/app.py`: a monthly order-volume bar chart uses the currently filtered rows, so the chart follows the selected region. Syntax validation and editor diagnostics pass. It is not complete until this version is redeployed and the chart is verified in Databricks.

Iteration 3 (CSV export) remains to be implemented after the chart deployment is checked. The North-filter screenshot is supplied in chat and is not stored in this repository.

