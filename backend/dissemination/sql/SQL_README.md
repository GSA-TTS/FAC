# sql folder

If you are reading this, it is assumed you are FAC developer who is about to touch the SQL in this folder.

This document describes

1. The database layout of the FAC
2. What is in this folder
3. How and when it executes
4. Things you should do
5. Things to watch out for

## the database layout of the FAC

*This is high-level background for reference.*

The FAC has two databases.

**DB1** is `fac-db`. The app talks to this database for all live operations.

When a user updates their submission, they are updating a `singleauditchecklist` record in DB1. When a user does a *basic* search, they are searching `dissemination_general` in DB1. And, finally, when you update user roles in `/admin`, you are editing a table in DB1.

**DB2** is `fac-snapshot-db`. began life as a place to do a database snapshot before deploy. It still serves this purpos. However, we are now using it as a place to build a *data pipeline* that is implemented entirely as a sequence of actions in SQL. In this regard, it becomes a *read replica* of sorts where we can serve both *advanced search* and the API.

**DB2 updates nightly.** The tables described below are *completely* destroyed and rebuilt every night. No data is persisted: DB2 is serves as a *stateless data pipeline*.

## what is in this folder

The SQL folder contains one folder for each database: `fac-db` and `fac-snapshot-db`. These names align with the "friendly names" of our database services in our system configuration.

Inside of each folder are two sub-folders: `pre` and `post`.

1. `pre` contains SQL we run against the databases *before* migrations.
2. `post` contains SQL we run against the databases *after* migrations.

In the case of `fac-db` (DB1), we run all of the scripts in the `pre` folder when we deploy, we run migrations, and then we run everything in the `post` folder. This is consistent with what took place previously.

In the case of `fac-snapshot-db` (DB2), it is slightly different. We run everything in the `pre` folder, and then we run everything in the `post` folder. There are no migrations in DB2, because it is a stateless copy of DB1.

## pre/post

The `pre` and `post` folders contain SQL files in execution order. That means that the ordering of the files matters.

If the following files are in the `pre` folder:

1. `000_first.sql`
2. `010_nope.SKIP`
3. `020_second.sql`

then they will execute in the lexigraphical order as shown. *However*, only files ending in `.sql` will be executed. This means that `000_first.sql` will be executed, `010_nope.SKIP` will be skipped, and `020_second.sql` will be run second. (Although it encourages a dirty tree, we *might* want to keep a file in the tree, but not have it execute.)

### what happens on DB1 (fac-db)

On DB1, we remove old schemas and tables (if they exist). If they don't exist, we essentially do nothing.

#### pre

1. Drop the API schemas.
2. Initialize audit curation code

The first step is because we will no longer serve the API from DB1. Therefore, all of the API schemas can go away.

The second is because we now have SQL triggers to support *data curation*. These triggers are defined here. Finally, we *disable* audit curation as a "just-in-case" measure. Because it is a state in the DB, the app could crash, and we would be in a condition of recording all changes to the SAC table. This would be *bad*. So, we do a "disable" as part of startup.

#### post

We tear out the old, old, OLD, Census data (used for the cog/over work in early days).

In the case of DB1, all of the actions could *probably* be `pre` actions. It does not particularly matter.

### what happens on DB2 (fac-snapshot-db)

Every night, on DB2, we first back up DB1. Then, we tear down our data pipeline and API, and rebuild it all from the backup we just made. This means that the data pipeline---including the backup---is essentially stateless.

#### pre

1. Set up roles (for PostgREST). Without these, PostgREST cannot authenticate/operate.
2. Tear down *all* schemas associated with the data pipeline.
3. Tear down and rebuild sequences used in constructing the new `public_data` tables.

#### post

##### Copy the `dissemination_*` tables to a `dissem_copy` schema.

We do this because the API is going to attach to `dissem_copy.dissemination_*` tables. We do this instead of using `public.dissemination_*` for the simple reason that those tables are overwritten with each deploy. If we attached the API `VIEW`s to the `public` tables, it would interrupt/disrupt/break the pre-deploy backups. So, the first thing we do is make a copy.

##### Create `public_data` tables.

These tables are a copy of the `dissem_copy` tables, with some changes.

1. We create a `combined` table that does a 4x `JOIN` across `general`, `federal_awards`, `passthrough`, and `findings`. This is all 100% public data. (It was previously our `MATERIALIZED VIEW`.)
2. We apply a `general.is_public=true` filter to all tables containing suppressed data, therefore guaranteeing that `notes_to_sefa`, `corrective_action_plans`, and `finding_text` (for example) contain *only* public data.
3. Sequences are inserted in all tables, and a `batch_number`. This is indexed for fast downloading of bulk data.

This is the "data pipeline." It is copying and modifying data to put it in the "right" shape for our API. This way, our API becomes a simple `SELECT *` in a `VIEW`.

As new data needs are discovered, it is assumed that the `post` operations on DB2 will implement additional copies/table creations/etc. to extend our data pipeline in order to address customer/user needs.

##### Create `suppressed_data` tables.

These are "the same" as the above, but they are filtered to contain only suppressed/Tribal data.

These tables are only accessible via API if you have gone through our Tribal API attestation/access process. Only Federal agencies are able to obtain API access to this data in order to support their oversight operations. Non-privileged keys will find empty result sets (`[]`) if they attempt to query these tables.

##### Create `metadata` table.

A `metadata` table containing counts of rows in all tables create above.

This also is exposed to `api_v2_0_0`. This allows users to quickly find 1) which tables are present, and 2) how much data is in those tables. This meets customer needs in an important way: when they are downloading data, they want to know "did I get everything?" This lets them do a bulk download via API and then answer that question in a programmatic manner.

It also serves as  a demonstration for one kind of data manipulation that can be used to create new tables and, therefore, new functionality for users via the API.

##### Create the `api_v1_1_0`.

This is the same code as previously existed, flaws and all. It points at `dissem_copy` tables, because they are 1:1 with what used to be in DB1. Hence, it "just works" "as-was."

A good refactoring would be to point these tables at `public_data` tables instead. The views would no longer require `JOIN` statements, and access control could be handled more gracefully.

##### Create `api_v2_0_0`.

This points at the `public_data` and `suppressed_data` tables. 

##### Setup permissions

All of the API access permissions are set in one place after the tables/views are created.

##### Bring up the API

We issue a `NOTIFY` to PostgREST which tells it to re-read the schemas and provide an API.

##### Indexing

Now, we index *everything*. If something is not performant, *add more indexes*.


## possible improvements

These are largely ticketed. However, there is a Python script floating around to generate `PARTITION` tables. (It is very repetative code, hence having a script to spit out the SQL makes sense. It is assumed it would be run once, manually, and the output added to the sequence.) However, this will multiply the number of tables we have by, like, Nx, where `N` is the number of partitions on each table. Performance testing suggests there is some improvement, but we should see significant improvements with `api_v2_0_0` that are "good enough" for a start without adding the complexity of `PARTITION`s at this point.

## `sling`

[sling](https://slingdata.io/) is a very cool tool. It takes a YAML config, and can copy data:

* From a DB to a different DB
* DB to CSV (locally or direct to an S3 bucket)
* DB to JSON (same)
* ...

basically, it "slings data around."

The `sling` folder contains an example that, if wired into the nightly sequence, will generate compressed CSVs of all of the public data.

In rough pseudocode:

```
for each year in the range 2016 - 2030
  for each table in the `public_data` space
    sling a CSV to S3 called `<year>-<table>.csv.zip`
```

The sling YAML config is auto-generated from a short (manual) Python script. Why? Because I wanted to loop over the years, and wanted to loop over the table names. Also, you can't have more than 1M rows in a CSV, or Excel will choke when you try and open it. Hence, our tables *must* be split, somehow, for it to be useful to our customers.

This is 95% of the way to providing downloads of bulk data. If we wire it in to the nightly data pipeline (as a last step), it will copy the `public_data` tables out to `/bulk_export/...` in our `private` S3 bucket, and the Django app can provide a page/links for authenticated users to grab those files (single-use URLs). This will 1) slow users down from getting them *all the time*, and give us better logging/tracking of who is accessing the bulk data.

# running tests

```
pytest -s --env local test_api.py
```

where the env can be `local`, `preview`, `dev`, `staging`, or `production` to run queries against the API in any of those environments.

* When running against local, `CYPRESS_API_GOV_JWT` needs to be set in your environment for this to work. And, it needs to match the `Authorization: Bearer` value in the Docker stack.
*  `FAC_API_KEY` needs to be set when testing against the production environments.

These tests are not (yet) integrated with any repeatable framework. They were developed as a way to quickly be confident that access controls were being implemented correctly. It is a ticket to integrate API testing.
