# sql folder

If you are reading this, it is assumed you are FAC developer who is about to touch the SQL in this folder.

This document describes

1. The database layout of the FAC
2. What is in this folder
3. How and when it executes
4. Things you should do
5. Things to watch out for

## the database layout of the FAC

The FAC has two databases.

**DB1** is the **production** database. The app talks to this database for all live operations. 

1. When a user updates their submission, they are updating a `singleauditchecklist` record in DB1.
2. When a user does a *basic* search, they are searching `dissemination_general` in DB1.
3. When you update user roles in `/admin`, you are editing a table in DB1.

**DB2** began life as a place to do a database snapshot before deploy. We are now using this as a *read replica* for DB1. It hosts a *data pipeline* that is implemented entirely as a sequence of actions in SQL.

**DB2 updates nightly.** It is *completely* destroyed every night, and completely rebuilt. No data is persisted. In this regard, DB2 is serves a *stateless data pipeline*. More on this later.

1. The PostgREST API uses DB2 to resolve *all* API queries.
2. When a user does an *advanced search*, they are using DB2.

## what is in this folder

The SQL folder contains one folder for each database: `fac-db` and `fac-snapshot-db`. These names align with our Terraform configuration.

Inside of each folder are two sub-folders: `pre` and `post`.

1. `pre` contains SQL we run against the databases *before* migrations.
2. `post` contains SQL we run against the databases *after* migrations.

In the case of `fac-db` (DB1), we run all of the scripts in the `pre` folder, we run migrations, and then we run everything in the `post` folder.

In the case of `fac-snapshot-db` (DB2), it is slightly different. We tear things down, then run everything in the `pre` folder, and then we run everything in the `post` folder. There are no migrations in DB2, because it is a stateless copy of DB1. The structure is parallel/preserved/kept-the-same-as DB1 for consistency, but it is worth noting that DB2 does not have any migrations.

There is one other folder, `sling`. More on this later.

## pre/post

The `pre` and `post` folders contain SQL files in execution order. That means that the way the files are named matters.

If the following files are in the `pre` folder:

`000_first.sql`
`010_nope.SKIP`
`020_second.sql`

then they will execute in the lexigraphical order as shown. *However*, only files ending in `.sql` will be executed. This means that `000_first.sql` will be executed, `010_nope.SKIP` will be skipped, and `020_second.sql` will be run second. (Although it encourages a dirty tree, we *might* want to keep a file in the tree, but not have it execute.)

### the pre/post sequence, generally

On each DB, in broad strokes (at time of this being written):

#### DB1 (fac-db)

On DB1, we do not do much.

##### pre

1. Drop the API schemas.
2. Initialize audit curation code

The first step is because we will no longer serve the API from DB1. Therefore, all of the API schemas can go away.

The second is because we now have SQL triggers to support *data curation*. These triggers are defined here. Finally, we *disable* audit curation as a "just-in-case" measure. Because it is a state in the DB, the app could crash, and we would be in a condition of recording all changes to the SAC table. This would be *bad*. So, we do a "disable" as part of startup.

##### post

We tear out the old, old, OLD, Census data (used for the cog/over work in early days).

In the case of DB1, all of the actions could *probably* be `pre` actions. It does not particularly matter.

#### DB2 (fac-snapshot-db)

We do a lot on DB2.

##### pre

1. Set up roles (for PostgREST). Without these, PostgREST cannot authenticate/operate.
2. Tear down *all* schemas associated with the data pipeline.
3. Tear down and rebuild sequences used in constructing the new `public_data` tables.

##### post

1. Copy the `dissemination_*` tables to a `dissem_copy` schema.

We do this because the API is going to attach to `dissem_copy.dissemination_*` tables. We do this instead of using `public.dissemination_*` for the simple reason that those tables are overwritten with each deploy. If we attached the API `VIEW`s to the `public` tables, it would interrupt/disrupt/break the pre-deploy backups. So, the first thing we do is make a copy.

2. Create `public_data` tables.

These tables are a copy of the `dissem_copy` tables, with some changes.

1. We create a `combined` table that does a 4x `JOIN` across `general`, `federal_awards`, `passthrough`, and `findings`. This is all 100% public data.
2. We apply a `general.is_public=true` filter to all tables containing suppressed data, therefore guaranteeing that `notes_to_sefa`, `corrective_action_plans`, and `finding_text` (for example) contain *only* public data.
3. Sequences are inserted in all tables, and a `batch_number`. This is indexed for fast downloading of bulk data.

This is the "data pipeline." It is copying and modifying data to put it in the "right" shape for our API. This way, our API becomes a simple `SELECT *` in a `VIEW`.

1. Create `suppressed_data` tables.

These are "the same" as the above, but they are filtered to contain only suppressed/Tribal data.

4. Create `metadata` table.

A `metadata` table containing counts of rows in all tables is created.

5. Create the `api_v1_1_0`.

This is the same code as previously existed, flaws and all. It points at `dissem_copy` tables, because they are 1:1 with what used to be in DB1. Hence, it "just works" "as-was."

A good refactoring would be to point these tables at `public_data` tables instead. The views would no longer require `JOIN` statements, and access control could be handled more gracefully.


6. Create `api_v2_0_0`.

This points at the `public_data` and `suppressed_data` tables. 

7. Setup permissions

All of the API access permissions are set in one place after the tables/views are created.

8. Bring up the API

We issue a `NOTIFY` to PostgREST which tells it to re-read the schemas and provide an API.

9. Indexing

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
