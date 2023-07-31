1. Download .zip files from Census containing all the tables for a given year. This will yield a single zipfile (e.g. `allfac22.zip`)
2. run `python main.py --zip <zipfile>`, e.g. `python main.py --zip allfac22.zip`
 
This creates SQLite3 DB file that can be used for exploration. It will be named the same as the zipfile. E.g. `allfac22.sqlite3`.

This will overwrite any SQLite file in this directory with that name. We assume that is OK. 

Use this file for workbook generation. The process cleans the Latin1 characters that come in via the CP-1252 characterset and re-exports everything as UTF-8, eliminating downstream errors.