# preparing to use these tools

First, visit Census Harvester, and get some data.

https://facdissem.census.gov/PublicDataDownloads.aspx

Choose `2022` and download the complete DB (.zip).

Unpack the zip; you'll end up with ~15 .txt files.

# stand up the stack

1. make docker-clean ; make docker-first-run ; docker compose up
2. Log in once
3. fac make_staff <email>
4. fac make_super <email>

# pre-load the .txt files

Visit the Minio admin interface:

http://localhost:9001

minioadmin/minioadmin is your magic.

(This process will only work in the local stack. Live we use S3 brokered through cloud.gov.)

Create a new filepath: `fixture-data` in the private bucket. You can call it what you want, really. 

# upload the .txt files

Drag-and-drop the text files from above into the Minio path you created. 

# csv_to_pg

This tool takes a public collection of Census CSVs (pipe-delimited) and loads them into the Postgres database. 

It requires Pandas, which to interact with Postgres requires SqlAlchemy.

The command takes one argument: `--path`. This is a path *into the private S3 bucket*. So, you will run

```
fac csv_to_pg --path fixture-data
```

if you followed the instructions above.

This command, when run, will read in each of the TXT files in the bucket, and then load them into a set of tables named `census_<name>22` (e.g. `census_cfda22`). **The command always does a `DROP TABLE IF EXISTS` before loading the data.** Given that we will never run this *on prod*, I figure this is... *cough* safe.

The result will be that the publicly-disseminated Census pipe-delimited CSV files are loaded into a set of tables we can use for further testing and development.

# to do

We should patch some of the columns in the Pandas dataframe by pre-pending "TEST TEST TEST". This way, we don't have to do this later, and the validation process E2E "just works." And, the data in the DB is clearly test data.

# generate_workbook_files

```
fac generate_workbook_files --output data_fixtures/historic --dbkey <dbkey>
```

This command takes an output path (in the tree) and a DBKEY and generates a set of workbook files from the data. It uses the exact same process that the in-memory process uses (working from the DB, creating files in memory, and then writes them to disk), so it is good for debugging when a workbook set  fails validation.

# workbooks_e2e

```
fac workbooks_e2e --email <email> --dbkey <key>
```

This currently:

1. Loads data from the DB
2. Creates workbooks in memory
3. Creates a JSON document that can serve as a reference for later validation
4. Uploads them to Django

To do:

1. Improve the JSON doc; it might not sync with what goes in the workbooks 100%? (Ask Matt. Patching the pandas dataframe would eliminate this concern.)
2. Add a PDF upload.
3. Step through the cert steps, perhaps inserting appropriate data.
4. Run the cross-validations.
5. Run the ETL.
6. Validate the JSON doc against the API.


#6 could also be "validate the JSON doc against the dissemination DB," if that is a faster initial path. It would be nice to run against the API. (This could be thousands upon thousands of API calls, which will be slow. We may want to learn to parallelize some of this.)

# run-many.bash

```
#!/bin/bash
set -euo pipefail

fac ()
{
  docker compose run web python manage.py ${@}
}

for key in `cat many_keys`
do
  reset;
  echo $key;
  docker compose run -T web python manage.py workbooks_e2e --email matthew.jadud+fac@gsa.gov --dbkey $key;
done
```

I create a file called `many_keys` that I copy-paste out of the database. Using a local SQLite file, I did

```
select dbkey from gen ORDER BY RANDOM() limit 1000;
```

However, things like

```
select dbkey from gen where COGAGENCY is not null limit 10;
select dbkey from cpas ORDER BY RANDOM() limit 10;
select dbkey from ueis ORDER BY RANDOM() limit 10;
```

are also handy, as they let you get DBKEYs for things that you know will (say) have additional auditosr, or additional UEIs.

# process

I run until it fails. Then, I do one of two things:

1. Patch the data (modify the generator functions)
2. Fix the validations

Ultimately, we may want to leave the data unpatched, and instead augment the gen table (or create a new table) that maps

| dbkey | is_good |
| ----- | ------- |
| 100010 | True |
| 123033 | False |
| ... | ... |

This would then give us a test set where we could try the validations on the workbooks, and *know* when we are going to fail. For known good historical data, we let it go all the way through. In this regard, we know what past data fails our more stringent validations, and what doesn't.

That said, we might have to do that table generation offline, and have it avaialble for online testing. (Or, we can run it, and put the CSV in the S3 bucket, and load it as part of bringup.)

Either way, this would be nice, but for a start, we might run with the patches. They still serve as a regression test, in case we change validations later: with patches, everything makes it through our current validations. 

Anyway: future testing improvements are a topic for conversation shortly. A patched-data regression test is still a good start.
