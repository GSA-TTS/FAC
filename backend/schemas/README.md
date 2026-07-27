
# Updating the Cluster Names

1. Review the latest [OMB Compliance Supplement](https://www.fac.gov/compliance/) cluster listings usually in a table/matrix.
2. Compare dataset with [existing Cluster Names](`backend/schemas/source/data/cluster-names.csv`)
3. Add any new cluster names
4. See below to regenerate schemas and templates.

#  Updating the ALN (formerly CFDA) listings and bumping workbook template version
Perform these steps below to update the ALN workbooks. Please follow all steps carefully and in order. 

As of May 2026, workbook versioning is now driven by `backend/schemas/source/data/workbook_version.json`, which stores both the current workbook version and the list of authorized workbook versions accepted during validation. The automation of the workbook creation is done by the make all command in step 2, it will take some time to complete.

Follow these steps to update the aln listing and version bump the workbook templates:
1. Activate your virtual env and change current directory to inside `backend/schemas`. Create a new branch to contain the incoming changes. 
2. Run `SAM_API_KEY=my-sam-key make all WORKBOOK_VERSION=d.d.d` where my-sam-key is your SAM API Key and d.d.d is the new workbook version. 
    - (NOTE: If reusing existing ALN data and skipping the SAM.gov fetch: run `SAM_API_KEY=my-sam-key make skip WORKBOOK_VERSION=d.d.d`)
3. Verify:
- workbook templates generated successfully in `backend/schemas/output/excel/xlsx/` and `backend/schemas/output/excel/json/`
- section schemas regenerated successfully in `backend/schemas/output/sections/`
- Cypress test workbooks regenerated successfully in `backend/cypress/fixtures/test_workbooks/`
- workbook_version.json updated correctly with the new current_workbook_version and authorized_workbook_versions in `backend/schemas/source/data/workbook_version.json`
- lookup schemas regenerated successfully in one or both (whatever is applicable): `backend/schemas/source/base/FederalProgramNames.json` (for ALNs) and `backend/schemas/source/base/ClusterNames.json` (for Cluster Names)
4. Git add, commit and push the changed files. Create a pull request on the updated branch.
5. After your PR is created, on the Github FAC repo you can go to Actions, scroll to the "Sync updated aln workbook files to FAC-transition-site" workflow, and Run workflow. The workflow entry box takes the Pull Request number containing the files you want to update.
- What the workflow does is copy the updated workbook templates from `backend/schemas/output/excel/xlsx/` into `assets/workbooks/` of the [static site repo](https://github.com/GSA-TTS/FAC-transition-site).
6. Once your PR is merged, please share the update to the oros-fac-dev channel to inform the team.

## A note about generate_lookup_schemas.py
`make all` executes `make source_data`, which, calls `generate_lookup_schemas.py`. This script can generate either cluster names or CFDA listings or agencies, depending on the args given (see docstring in the script). The format of the CSVs can change (and have), so changes to `generate_lookup_schemas.py` may be necessary in the future.


#### Workbooks Affected
- additional-eins-workbook
- additional-ueis-workbook
- audit-findings-text-workbook 
- corrective-action-plan-workbook 
- federal-awards-audit-findings-workbook 
- federal-awards-workbook 
- notes-to-sefa-workbook 
- secondary-auditors-workbook


# Deprecated : Updating the ALN (formerly CFDA) listings
These steps are no longer necessary because the script now calls the API and automatically downloads the required files.

1. Log in to Sam.gov with your GSA account and go to https://sam.gov/search/.
2. Select "Federal Assistance" and then "Assistance Listings" as domain.
3. Under "key word" search, choose simple and "any words" and then "active" listings.
4. Click "Actions" on the upper-right and then "download" to get the CSV file of active listings. Save this as `/schemas/source/data/aln_csvs_to_be_merged/active-alns.csv`.
5. Repeat the process, choosing "inactive" listings to get the CSV file for inactive ALN listings. Save this as `/schemas/source/data/aln_csvs_to_be_merged/inactive-alns.csv`. These have to be done separately due to a limit on the amount of records that can be downloaded into a CSV file.
6. Make sure the headings of first 2 columns match this: "Program Number", "Program Title". If applicable, make sure that trailing zeroes are not dropped (In Excel, select the Program Number column, then format cell as number with 3 numbers after decimal).
7. Perform the "Bumping workbook template version" steps below.
    * Note: Part of this process will merge the CSVs into `/schemas/source/data/cfda-lookup.csv`.