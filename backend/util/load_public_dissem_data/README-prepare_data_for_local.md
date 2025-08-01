# prepare_prod_data_for_local.bash

The `prepare_prod_data_for_local` bash script is a menu-driven tool for repeatbly downloading data dumps from `production` and sanitizing them for local use. 

## goal

The goal is for devs to have the same data in their local stacks. This makes feature testing easier, and allows us to communicate about issues consistently (e.g. performance, bugs).

## driving principle

We want to load the same starting data and then modify it to meet our needs. This eliminates a proliferation of different dumps and subsequent confusion (e.g. "What dump are you using?"). Instead, we start with one file/database state, and modify it to match the needs of the moment.

## requirements

* `psql`, `pg_dump`, and `pg_restore` need to be v15 (or higher?)
* `jq` must be installed
* `cf` must be installed

This script requires you to intentionally set your environment with `cf`.

In order to download `production` data, you must

```
cf t -s production
```

This can work on lower environments for testing. The script automatically sets `cf t -s preview` after downloading data as a precaution.

## cleanup locally, at least once

Before using this for the first time, the local stack will need to be cleaned up.

```
docker compose down
docker rm -f $(docker ps -a -q)
docker volume rm $(docker volume ls -q)
docker system prune -f
docker volume prune -f
```

Then, `docker compose up`. This only needs to be done once, but it is necessary to bring the stack up with v17 Postges containers.

## BLUF

Log in to the `cf` API.

Run the script. Pass a path to a directory where you want to download `.dump` files from the `production` bucket.

```
./prepare_data_for_local.bash <path> <email>
```

The `<email>` is your GSA email address.

Run steps 2, 3, 4, 5, 6, and 7 in order.

If you are feeling bold, select the option for running everything straight through. This runs steps 2-7.

Upload the resulting file (e.g. `sanitized-20250731.dump`) to GDrive for sharing with the team. It is now ready for load via `manage_local_data.bash`.

This file will contain 100% public data (disseminated and in-progress). To make sure no in-progress audits are Tribal submissions for which an attestation has not yet been made, we delete all `tribal` audits that do not yet have an attestation. This should guarantee that 100% of all in-progress is *also* public data.

## the menu

The menu is roughly in order of use.

### select_target_backup_for_download

This is an optional step.

When we download a backup from `production`, we need to choose which dump we want to work with. These are named `MM-DD-HH` in the scheduled folder.

The script sets a dump path:

```
DESIRED_BACKUP="07-27-12"
```

Generally, this should be updated and committed if a new dump is going to be worked with. However, for temporary/local testing, it is possible to specify the path. Be careful: no checking is performed when this value is entered. Better to verify the path exists and set it in the script.

### download_dumpfiles

When the script was launched, a path had to be provided.

This command creates a service key, downloads dumpfiles to our local path, and then removes the service key.

The files targeted are in the file `tables.source`. This file is sourced in. Note that this file drives several processes in the script; it also serves as a list of table names. This file should be modified carefully, and it should always indicate names of files in the backup bucket at the keypath hard-coded into the script.

### load_raw_prod_dump

Once the dumpfiles have been downloaded to the local path, they now need to be loaded one-by-one into the database.

For each table, we truncate any data locally in that table, and then load the dump via `pg_restore`. Note that this is *not* the same as the later test/load, because this assumes *many* dumpfiles, whereas the end state is a *single* dumpfile for sharing via GDrive.

After this step, the local database has data in it.

### remove_suppressed_tribal_audits

We do not want to work with Tribal data locally. This is not because we cannot or should not, but out of an abundance of caution.

This step does the following:

1. Search the `singleauditchecklist` table for the report_ids of all audits where no consent to disseminate was given.
2. Search the `singleauditchecklist` table for the sac_ids of all audits where no consent to disseminate was given.
3. Delete that data from all of the tables

This is encoded as a single SQL file (`remove_tribal_audits.sql`), as we cannot do this iteratively. Specifically, `DELETE` cannot `CASCADE`; therefore, we have to delete from the tables in a specific order to avoid foreign key constraints. It is possible that the table list could be re-ordered so that it could be used *in reverse* to do this in a loop. However, the initial `SELECT` statements would still need to be used and somehow passed via `bash`. 

In short: the SQL file is a script that, if maintained/used properly, deletes *all* suppressed Tribal data from the database.

It should never be run in `production`.

### export_sanitized_dump_for_reuse

Once the table is sanitized, we can export it.

This is one of the steps that require `pg_dump` version 17 or higher. It uses the `--filter` flag. This step does two things:

1. Generate a `dump_filters.pg` file, containing filter rules
2. Dump the entire database according to those rules

Normally, `pg_dump` dumps all tables, or takes command-line parameters to control which tables are exported. This is hard, given the nature of our script. Instead of trying to build up a command list, we first dump a list of filters that specify exactly which tables we want to include in the dump. This is generated using the array in `tables.source`. Each line has the form

```
include table <tablename>
```

Then, `pg_dump` is called `--data-only` on that filtered set of tables. This produces a single file called `sanitized-${DATE}.dump`. E.g. `sanitized-20250731.dump`. This file can then be uploaded into GDrive.

### truncate_all_local_tables

This runs a `TRUNCATE CASCADE` on every single table in the `tables.source` array. 

Removing all local data is a necessary step for testing a local re-load of the local data that was just dumped.

Before truncating, a `COUNT(*)` of every table is gathered. This is used for the next step.

### test_sanitized_production_dump

The dumpfile that was just created wants to be tested, at least minimally.

This command loads the file that was just dumped, and then gathers a count on every table that was loaded. Afterwards, the counts are compared against the values stored from the `truncate_all_local_tables` step. If all the counts are the same, it means all the tables in the array were reloaded and had the expected counts.

This only works if the truncate/test happen on the same day, as it is hard-coded against the current date. 
