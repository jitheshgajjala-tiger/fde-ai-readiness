# Assignment 3: Governance check

**Section:** 2. Databricks Genie (Conversational Analytics)

Test the same Genie Space with two different user identities that have different Unity Catalog row-level permissions, and confirm Genie's answers correctly differ based on access.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence from the completed two-user test
- [x] Result and learning documented

**Status: complete.** I completed the live two-identity Genie governance test. I asked the same Genie question under identities with different Unity Catalog row-level access and confirmed the results differed according to each identity's permissions.

## Approach

1. Configure the users' Unity Catalog permissions and row-level filter for the governed orders table.
2. Ask the same question in Genie under each identity.
3. Compare results to confirm access is enforced by Unity Catalog, not prompt instructions.
4. Remove the temporary row filter after the test.

## Evidence

I verified both identities successfully and confirmed Genie returned results consistent with their respective row-level permissions. I did not save the exact identity names, returned counts, generated SQL, or screenshots in this repository, so I have not reproduced those details here.

## Result and what I learned

My test confirmed that Unity Catalog row-level filtering governs what each identity can see through Genie. I learned that access control belongs in the governed data layer rather than Genie prompt instructions or application logic.

## Notes

The row filter affects the shared table while attached; remove it after the controlled test. Detailed screenshots and row counts were not archived in this repository.

