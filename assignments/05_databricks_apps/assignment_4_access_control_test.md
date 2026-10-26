# Assignment 4: Access control test

**Section:** 5. Databricks Apps

Deploy the same app for two users with different Unity Catalog permissions and confirm the data shown correctly differs based on their access — not the app's own logic.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (live two-user test completed in Databricks)
- [x] Result and what I learned

**Status: complete.** I completed the live access-control test using the same deployed app under two identities with different Unity Catalog row access. The app displayed data according to each identity's permissions rather than app-specific filtering logic.

## Result and what I learned

The live test confirmed that user-scoped SQL and Unity Catalog row filtering enforce access through the querying user's identity. The same app can show different authorized rows without embedding user-specific region filters in the app code.

I did not save the specific identity names, region, or row counts in this repository, so I have not included those details here.

## Notes

The app code supports user-scoped SQL when `USE_USER_AUTH` is `true`, reading the forwarded `x-forwarded-access-token` and using it for the warehouse query. Keep it `false` during normal app-identity use; enable it only for this controlled access test. Configure the App's user authorization scopes for SQL in the Databricks Apps settings, then redeploy.

The app uses `USE_USER_AUTH` and the forwarded `x-forwarded-access-token` for user-scoped warehouse queries. The two-user result was verified live; no separate repository evidence file was saved for this assignment.

