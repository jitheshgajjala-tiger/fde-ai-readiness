# Assignment 5: Live iteration

**Section:** 5. Databricks Apps

Starting from a working app, make three incremental UI/feature changes (e.g., add a filter, add a chart, add an export button) one at a time, redeploying and validating after each change.

## Deliverables

- [ ] Approach and steps taken
- [ ] Evidence (screenshots, output, or links)
- [ ] Result and what I learned

## Notes

Iteration 1 is deployed and behaviorally verified. The screenshot supplied in chat shows **North** selected and every displayed row has `region = North` (7 matching rows). This confirms the region filter affects the displayed result.

Iteration 2 is deployed and behaviorally verified. The screenshot supplied in chat shows **North** selected and the monthly order-volume chart: January 1, February 2, May 2, and September 2. The monthly counts sum to the 7 displayed North orders.

Iteration 3 is prepared locally in `databricks_prep/app/app.py`: **Download filtered orders (CSV)** exports the currently displayed rows, using a region-specific filename. This is not complete until the app is redeployed and the downloaded CSV is checked against the selected region's table. Screenshots are supplied in chat and are not stored in this repository.

