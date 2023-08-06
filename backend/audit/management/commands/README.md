# csv_to_pg

This tool takes a public collection of Census CSVs (pipe-delimited) and loads them into the Postgres database. 

It requires Pandas, which to interact with Postgres requires SqlAlchemy.

It takes a zipfile as an argument. One has been checked in as a test fixture (`data_fixtures/allfac22.zip`). By checking it in, we have it available for use when the code is pulled to the cloud.gov environment.

This command, when run, will expand the zipfile into a temporary directory, read in each of the TXT files, and then load them into a set of tables named `census_<name>22` (e.g. `census_cfda22`). **The command always does a `DROP TABLE IF EXISTS` before loading the data.**

These files have nothing done to them; they are intended for further procsesing. In this case, we envision them being processed into workbooks for driving automated testing processes.
