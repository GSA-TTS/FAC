### Preperation steps
```sh
cf t -o <org> -s <env>
```

Bind the backups bucket to the application
```sh
cf bind-service gsa-fac backups
```

Restart the app so changes occur and wait for the instance to come back up
```sh
cf restart gsa-fac --strategy rolling
```

Unbind the existing fac-private-s3 bucket from the app
```sh
cf unbind-service gsa-fac fac-private-s3
```

Rebind the fac-private-s3 bucket with the backups bucket as an additional instance
```sh
cf bind-service gsa-fac fac-private-s3 -c '{"additional_instances": ["backups"]}'
```

Restart the app so changes occur and wait for the instance to come back up
```sh
cf restart gsa-fac --strategy rolling
```

### Database Backups

Information regarding the fac-backup-utility can be found [at the repository](https://github.com/GSA-TTS/fac-backup-utility).
Database backups occur in the following ways:
1. An initial backup, where a backup has not been run in the target environment. This input of `initial_backup` is important, as when it does a the `db_to_db` command, it will not truncate the target table, as the table does not exist in the destination database.
```bash
./fac-backup-util.sh v0.1.3 initial_backup
# Curl the utility
# Install AWS
# DB to S3 table dump (backups)
# DB to DB table dump (fac-db -> fac-snapshot-db) [No Truncate, as tables dont exist]
# AWS S3 sync (fac-private-s3 -> backups)
```

2. A deploy backup, where the `db_to_db` function is not called. This is a standard backup strategy before the application deploys, to ensure the s3 contents of the primary s3 are sync'd to the backups bucket, and a table dump is stored in the backups bucket.
```bash
./fac-backup-util.sh v0.1.3 deploy_backup
# Curl the utility
# Install AWS
# DB to S3 table dump (backups)
# AWS S3 sync (fac-private-s3 -> backups)
```

3. A scheduled backup is run every two hours, across each environment, ensuring that we have a clean backup in s3, rds, and the bucket contents are in sync.
```bash
./fac-backup-util.sh v0.1.3 scheduled_backup
# Curl the utility
# Install AWS
# DB to S3 table dump (fac-db -> backups)
# DB to DB table dump (fac-db -> fac-snapshot-db) [Truncate target table before dump]
# AWS S3 sync (fac-private-s3 -> backups)
```

### Restoring
Restoring from backups can be run via workflow, from designated individuals. There are two paths that we can restore from.

1. S3 Restore takes a `operation-mm-DD-HH` input (ex `scheduled-06-04-10`), and is required for the backups to be restored. The utility looks in `s3://${bucket}/backups/operation-mm-DD-HH/` for its table dumps, and without supplying the target backups, it will not restore. Once it does a `--data-only` restoration, it will then sync the files from the backups bucket to the application bucket. We do this to ensure the contents of the application bucket are up to date, relative to the data in the database. We know that if we use the latest folder in `/backups/` then the contents of the s3 are the latest available, from the prior backup.
```bash
./fac-restore-util.sh v0.1.3 s3_restore scheduled-06-04-10
# Curl the utility
# Install AWS
# DB to S3 table dump (backups -> fac-db) [Truncate target table before --data-only pg_restore]
# AWS S3 sync (backups -> fac-private-s3)
```

2. Database to database restoration also can occur as well, using `psql` to dump the tables from the cold store database to the live database.
```bash
./fac-restore-util.sh v0.1.3 db_restore
# Curl the utility
# Install AWS
# DB to DB table dump (fac-snapshot-db -> fac-db) [Truncate target table before dump]
# AWS S3 sync (fac-private-s3 -> backups)
```
