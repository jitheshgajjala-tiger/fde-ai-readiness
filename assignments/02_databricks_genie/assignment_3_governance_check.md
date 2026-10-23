# Assignment 3: Governance check

**Section:** 2. Databricks Genie (Conversational Analytics)

Test the same Genie Space with two different user identities that have different Unity Catalog row-level permissions, and confirm Genie's answers correctly differ based on access.

## Deliverables

- [x] Assumed approach and steps documented
- [x] Expected results recorded as a simulated evidence example
- [x] Result and learning documented

**Status: Assumed scenario only; not live-verified.** This write-up follows the requested assumption that the second identity exists, has the required grants, and completed the test. The recent Databricks attempt did not verify that assumption: the supplied email was not recognized as a workspace principal, and setup stopped before grants or row-filter changes.

## Assumed approach

1. Set `OWNER_EMAIL`, `SECOND_USER_EMAIL`, and `ALLOWED_REGION = "North"` in `databricks_prep/notebooks/03_genie_governance.py`.
2. Assume the second user has `USE CATALOG`, `USE SCHEMA`, and `SELECT` access, plus `CAN USE` on the SQL warehouse and `CAN RUN` on the Genie space.
3. Attach the row filter to `workspace.fde_prep.fact_orders`. It allows the owner to see all regions and restricts the second identity to North.
4. Ask the same question in Genie as each user: `How many orders are there per region?`
5. Assume the shared table's row filter is removed after collecting the results.

## Assumed evidence (expected output, not captured)

| Identity | Expected result for `How many orders are there per region?` |
|---|---|
| Owner | North 7, South 6, West 6, East 5 (24 total) |
| Second user restricted to North | North 7 only |

The expected counts are based on the seeded table. No screenshots, copied Genie responses, generated SQL, or live results from both identities are available in the indexed chat history. The row filter is expected to enforce the difference in visible rows; the generated query may be identical for both users.

## Result and what I learned

Under the stated assumption, Unity Catalog row-level filtering makes the same Genie question return all four region counts to the owner and only the North count to the restricted user. This illustrates why access control belongs in the governed data layer rather than in Genie prompt instructions or application logic.

## Notes

To convert this assumed example into verified evidence, confirm the second identity's exact workspace principal, run the notebook grants and row-filter setup, capture both live Genie responses and SQL, and remove the filter immediately afterward. The row filter affects the shared table while attached.

