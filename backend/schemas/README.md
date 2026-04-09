
# Updating the Cluster Names

1. Review the latest [OMB Compliance Supplement](https://www.fac.gov/compliance/) cluster listings usually in a table/matrix.
2. Compare dataset with [existing Cluster Names](`backend/schemas/source/data/cluster-names.csv`)
3. Add any new cluster names
4. See below to regenerate schemas and templates.

# Updating the ALN (formerly CFDA) listings

1. Log in to Sam.gov with your GSA account and go to https://sam.gov/search/.
2. Select "Federal Assistance" and then "Assistance Listings" as domain.
3. Under "key word" search, choose simple and "any words" and then "active" listings.
4. Click "Actions" on the upper-right and then "download" to get the CSV file of active listings. Save this as `/schemas/source/data/aln_csvs_to_be_merged/active-alns.csv`.
5. Repeat the process, choosing "inactive" listings to get the CSV file for inactive ALN listings. Save this as `/schemas/source/data/aln_csvs_to_be_merged/inactive-alns.csv`. These have to be done separately due to a limit on the amount of records that can be downloaded into a CSV file.
6. Make sure the headings of first 2 columns match this: "Program Number", "Program Title". If applicable, make sure that trailing zeroes are not dropped (In Excel, select the Program Number column, then format cell as number with 3 numbers after decimal).
7. Perform the "Bumping workbook template version" steps below.
    * Note: Part of this process will merge the CSVs into `/schemas/source/data/cfda-lookup.csv`.

# Bumping workbook template version

Follow these steps to version bump the workbook templates:
1. `backend/schemas/source/excel/libs/Sheets.libsonnet`: Update the `WORKBOOKS_VERSION` variable.
2. `backend/audit/intakelib/checks/check_version_number.py`: Update the `AUTHORIZED_VERSIONS` variable.
3. The JSON files in `backend/schemas/source/sections/` require some modification. For each file, locate the version enum found in `Meta.properties.version.enum`. Append the PREVIOUS version to the end of this list, followed by `Sheets.WORKBOOKS_VERSION`.
3. The `.jsonnet` files in `backend/schemas/source/sections/` require some modification. For each file, locate the version enum found in `Meta.properties.version.enum`. Append the PREVIOUS version to the end of this list, followed by `Sheets.WORKBOOKS_VERSION`. The files to modify are:
* `AdditionalEINs.schema.jsonnet`
* `AdditionalUEIs.schema.jsonnet`
* `AuditFindingsText.schema.jsonnet`
* `CorrectiveActionPlan.schema.jsonnet`
* `FederalAwards.schema.jsonnet`
* `FederalAwardsAuditFindings.schema.jsonnet`
* `NotesToSefa.schema.jsonnet`
* `SecondaryAuditors.schema.jsonnet`
4. Activate your virtual env inside `backend/schemas` and run `make all`. This will generate new schemas and templates in `/schemas/output/`.
5. Update the workbook template fixtures used in the Cypress tests, found in `backend/cypress/fixtures/test_workbooks`.
    * An easy (but tedious) way to do this is to modify the templates with the data used in the existing fixtures, then copy/overwrite all of those XLSXes into `test_workbooks`.
        * If a cell has a selector, use that instead of copy-pasting.
        * Don't forget to revert the templates afterwards!
6. Once your PR is merged, don't forget to copy the new templates, found in `backend/schemas/output/excel/xlsx/`, into `assets/workbooks/` of the [static site repo](https://github.com/GSA-TTS/FAC-transition-site).

## A note about generate_lookup_schemas.py
`make all` executes `make source_data`, which, calls `generate_lookup_schemas.py`. This script can generate either cluster names or CFDA listings or agencies, depending on the args given (see docstring in the script). The format of the CSVs can change (and have), so changes to `generate_lookup_schemas.py` may be necessary in the future.
