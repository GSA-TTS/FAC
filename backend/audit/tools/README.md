
# generate-sqlite-files

The purpose of this tool is to take public, Census-generated pipe-delimited CSV files and turn them into an SQLite database.

This is not intended for robust data work. It is to support rapid development of new tools, or to provide a way to easily explore data using SQL in a tool like `sqlitebrowser`.

## Process

1. Download .zip files from Census (<https://facdissem.census.gov/PublicDataDownloads.aspx>) containing all the tables for a given year. This will yield a single zipfile (e.g. `allfac19.zip`)
2. run `python generate_sqlite_files.py --zip <zipfile> --outdir <dir>`, e.g. `python generate_sqlite_files.py --zip allfac19.zip --outdir ay19`

This creates SQLite3 DB file that can be used for exploration. It will be named the same as the zipfile. E.g. `allfac19.sqlite3`.

It also creates two directories: `ay19` and `clean-ay19`. The second of these is for transferring to an S3 bucket for loading into our PG database.

### Warning

This will overwrite any SQLite file in this directory with that name. We assume that is OK. 

The `.gitignore` in this directory should ignore the `.zip` and `.sqlite3` files.

### Notes

Use this file for workbook generation. The process cleans the Latin1 characters that come in via the CP-1252 character set and re-exports everything as UTF-8, eliminating downstream errors.

Or, I think it does. Point being, Census seems to have had processes that would use the default Windows character set, and this was always CP-1252. Modern systems typically use UTF-8, and we sometimes see "errors" in their data that are linked to character encoding. Hopefully this script works around that.

### Next

Fillow instructions at backend/audit/management/commands/README.md
