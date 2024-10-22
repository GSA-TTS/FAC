# sql folder

From the perspective of the application, there are both managed and unamanged tables.

However, we have data and processes that are outside of the application, but inside the databases.

The SQL folder provides a mechanism for:

1. Running SQL against the databases *before* we run migrations.
2. Running SQL against the databases *afetr* we run migrations.

We have two databases.

1. **fac-db** is the production database. The app talks to this database for all live operations.
2. **fac-snapshot-db**, which began life (and continutes to be used for) snapshots of the production database right before a deploy. Because it wasn't doing anything else, we have co-opted this database to also serve as a "read replica" of the dissemination tables, and host the API.

## folder organization

* `fac-db` holds code that operates **on** fac-db before/after migrations.
* `fac-snapshot-db` holds code that operates **on** `fac-snapshot-db` before/after migrations.
* `sling` holds files used by the `sling` application (for moving data between the databases).

# pre/post

The `pre` and `post` folders contain SQL files in execution order. That means that the way the files are named matters.

If the following files are in the `pre` folder:

`000_first.sql`
`010_nope.SKIP`
`020_second.sql`

then they will execute in the lexigraphical order as shown. *However*, only files ending in `.sql` will be executed. This means that `000_first.sql` will be executed, `010_nope.SKIP` will be skipped, and `020_second.sql` will be run second. (Although it encourages a dirty tree, we *might* want to keep a file in the tree, but not have it execute.)

## in practice

The API is torn down every time we deploy (`pre`). This is because the API has `VIEW`s on the database tables that interfere with migrations. Then, everything in `post` is run, which stands up the API and performs operations that optimize or otherwise improve upon the DB's health/performance.

# in case it isn't confusing

* The basic search (in the application) talks to fac-db.
* The advanced search (in the application) talks to fac-snapshot-db.
* The public/read API talks to fac-snapshot-db.
* The *write* portion of tribal access (adding/removing keys) talks to fac-db.
* The *read* portion of tribal access (reading files) talks to fac-snapshot-db.
* The admin API only talks to fac-db.



