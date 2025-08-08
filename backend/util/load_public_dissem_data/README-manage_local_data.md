# manage_local_data.bash

The `manage_local_data` bash script is a menu-driven tool for taking sanitized public data and loading/manipulating it in the local stack.

Here, "sanitized" means "all Tribal data removed." This script allows devs to "reintroduce" suppressed Tribal audits by creating fake ones.

## goal

The goal is for devs to have the same data in their local stacks. This makes feature testing easier, and allows us to communicate about issues consistently (e.g. performance, bugs).

## driving principle

We want to load the same starting data and then modify it to meet our needs. This eliminates a proliferation of different dumps and subsequent confusion (e.g. "What dump are you using?"). Instead, we start with one file/database state, and modify it to match the needs of the moment.

## requirements

* `docker`
* a current sanitized dumpfile

## cleanup locally, at least once

Before using this for the first time, the local stack will need to be cleaned up.

```
docker compose down
docker rm -f $(docker ps -a -q)
docker volume rm $(docker volume ls -q)
docker system prune -f
docker volume prune -f
```

Then, `docker compose up`. This only needs to be done once. Probably.


## building the script container

These scripts are Dockerized. Therefore, you must have Docker installed. (This is a FAC dev requirement, so FAC devs should be good to go.)

Before using the `manage` script, you must build the container for it.

```
docker build -t manage:latest -f Dockerfile.manage .
```

## BLUF

Fetch a santizied dumpfile from GDrive:

https://drive.google.com/drive/folders/1WymwJtdQ287SdgrOx__aEraoVTx7ig9D

These are approximately 2GB. Put it in the `data` folder.

```
docker run -i --rm --env DUMPFILE=data/sanitized-<DATE>.dump --env EMAIL_ADDRESS="YOUR_EMAIL" -v .:/app --network backend_default prepare
```

The path is to a `sanitized-<DATE>.dump` dumpfile (relative to the container root), and you need to provide a staff user email address. It could be yours or someone else's. (Because this is from a prod dump, using your prod email address should "just work.")

Note that you need to be running on the same Docker network as the app stack. `docker network ls` will let you see where things are running if you need to change that parameter.

Run 1, 2, 3, 4, 5, 6, and 7.

If you're feeling bold, run 9. (It runs 1-7.)

## the menu

The menu is roughly in order of use.

### load_sanitized_data_dump

This truncates all tables and loads the dump passed on the command line.

### shrink_to_20k_records

If you want a small set of data to work with, run this. 

You do not *have* to run this. The other commands will work with the larger dataset. However, some of them will take longer. For example, it takes longer to redisseminate all, or generate the `MATERIALIZED VIEW` if you have 350K records vs. 20K records.

### generate_fake_suppressed_reports

This runs SQL that flips ~500 audits randomly from being public to having tribal data attestations that say they are suppressed/is_public=false. 

Note that this *only* modifies the `singleauditchecklist`. It is not a management command. Therefore, you would need to redisseminate all of the records to see this in `dissemination_general` and other tables.

### generate_resubmissions

This generates a handful of faked resubmissions. They are redisseminated automatically, so metadata should appear in `dissemination_` tables (when that is implemented).

### generate_materialized_view

Runs the management command for generating the MV `dissemination_combined`.

### truncate_dissemination_tables

If you want to eliminate the dissemination tables, run this command. The `singleauditchecklist` and other internal tables are left untouched.

### redisseminate_all_sac_records

This redisseminates all records one-by-one. 

Note that it does *not* wipe out the disseminated data first. This management command is meant to be safe to use in production, and therefore does records one-by-one. 

### truncate_all_local_tables

This wipes all the tables. Used by `load_sanitized_data_dump`. 

### Run all

This runs the following in order:

1. load_sanitized_data_dump
1. shrink_to_20k_records
1. generate_fake_suppressed_reports
1. generate_resubmissions
1. truncate_dissemination_tables
1. redisseminate_all_sac_records
1. generate_materialized_view

(The README may get out of sync with the command; it runs a sequence that loads the data and applies all preparation steps in order to leave you with a set of internal and external tables aready for dev and test.)
