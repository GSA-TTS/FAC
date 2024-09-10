# Updating the CFDA listings

The current CFDA assistance listings are in the CSV found [here](https://sam.gov/data-services/Assistance%20Listings/datagov?privacy=Public). When downloading the file, save it in the format `cfda-lookup-YYYYMMDD.csv` in the `/schemas/source/data` directory. Running `make all` should be sufficent to regenerate the lookup schemas and the Excel templates.

More specifically, `make all` executes `make source_data`, which, calls `generate_lookup_schemas.py`. This script can generate either cluster names or CFDA listings or agencies, depending on the args given (see docstring in the script.) The script will automatically used the latest-dated CSV file for processing. This way, the Makefile doesn't have to be repeatedly changed and we can retain the historic files. The format of the CSVs can change (and have), so changes to `generate_lookup_schemas.py` may be necessary may be necessary in the future and non-current files may no longer be processable.

If you get a `UnicodeDecodeError`, you may have to manually save it with UTF-8 encoding (in VSCode, click UTF-8 in the bottom right and select "Save with encoding".)
