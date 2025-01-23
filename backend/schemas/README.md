# Bumping workbook template version

Follow these steps to version bump the workbook templates:
- `backend/schemas/source/excel/libs/Sheets.libsonnet`: Update the `WORKBOOKS_VERSION` variable
- `backend/audit/intakelib/checks/check_version_number.py`: Update the `AUTHORIZED_VERSIONS` variable
- Run `make all` to generate new schemas and tempaltes
- Once your PR is merged, don't forget to copy the new templates, found in `backend/schemas/output/excel/xlsx/`, into `assets/workbooks/` of the [static site repo](https://github.com/GSA-TTS/FAC-transition-site).

# Updating the ALN (formerly CFDA) listings


To download ALN listings:

1. Log in to Sam.gov with your GSA account and go to https://sam.gov/search/.
2. Select "Assistance Listings" as domain.
3. Under "key word" search, choose simple and "any words" and then "active" listings.
4. Click "Actions" on the upper-right and then "download" to get the CSV file of active listings. Save this as `/schemas/source/data/alns_to_be_merged/active-alns.csv`.
5. Repeat the process, choosing "inactive" listings to get the CSV file for inactive ALN listings. Save this as `/schemas/source/data/alns_to_be_merged/inactive-alns.csv`. These have to be done separately due to a limit on the amount of records that can be downloaded into a CSV file.
7. Finally, run `make all`. This will merge the CSVs and generate the lookup schemas and the Excel templates. To verify that the "make all" command has run correctly, check to see that the`backend/schemas/source/base/FederalProgramNames.json` file has been updated.

More specifically, `make all` executes `make source_data`, which, calls `generate_lookup_schemas.py`. This script can generate either cluster names or CFDA listings or agencies, depending on the args given (see docstring in the script.) The script will automatically used the latest-dated CSV file for processing. This way, the Makefile doesn't have to be repeatedly changed and we can retain the historic files. The format of the CSVs can change (and have), so changes to `generate_lookup_schemas.py` may be necessary may be necessary in the future and non-current files may no longer be processable.

If you get a `UnicodeDecodeError`, you may have to manually save it with UTF-8 encoding (in VSCode, click UTF-8 in the bottom right and select "Save with encoding".)
