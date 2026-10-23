# Assignment 5: Live iteration

**Section:** 5. Databricks Apps

Starting from a working app, make three incremental UI/feature changes (e.g., add a filter, add a chart, add an export button) one at a time, redeploying and validating after each change.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots and downloaded CSV supplied in chat)
- [x] Result and what I learned

## Notes

Iteration 1 is deployed and behaviorally verified. The screenshot supplied in chat shows **North** selected and every displayed row has `region = North` (7 matching rows). This confirms the region filter affects the displayed result.

Iteration 2 is deployed and behaviorally verified. The screenshot supplied in chat shows **North** selected and the monthly order-volume chart: January 1, February 2, May 2, and September 2. The monthly counts sum to the 7 displayed North orders.

Iteration 3 is deployed and verified. With **North** selected, clicked **Download filtered orders (CSV)** and inspected `orders_north.csv`. It contains 7 rows; every row has `region = North`, and the order IDs (1001, 1005, 1006, 1013, 1014, 1021, 1022) match the displayed filtered table.

All three iterations were deployed and checked independently: the region filter returns only the selected region, the monthly chart reflects the filtered rows, and the CSV export contains the same filtered records. The screenshots and downloaded CSV were supplied in chat and are not stored in this repository.

## Result and what I learned

- The region filter, monthly order-count chart, and CSV export work together over the same filtered dataframe.
- Verifying the downloaded file confirmed the export respects the selected region, rather than exporting the unfiltered source rows.
- Each feature was added as a separate iteration and checked in the deployed app.

