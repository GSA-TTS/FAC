# Backup and Restore

## Description

Data persisted using the cloud.gov RDS service is backed up daily as part of the service offering, as described in the [official documentation](https://docs.cloud.gov/platform/services/relational-database/#backups-and-recovery). These backups can be used to restore the service to a previous state upon request to the cloud.gov team.

However, the FAC team has additional processes in place to recover from data loss or corruption faster and more efficiently than the request-based mechanism offered by cloud.gov. To that end, the team maintains a custom backup and restore tool that takes scheduled and on-demand database backups which allows the team to restore the database to a known state directly, without opening a support request or waiting on an external team.

## Backups

Information regarding the fac-backup-utility can be found [at the repository](https://github.com/GSA-TTS/fac-backup-utility).

Database backups are facilitated via the [`fac-backup-util.sh`](../backend/fac-backup-util.sh) script, which supports the following backup types:

1. **`initial_backup`** - used when a backup has not yet been run in the target environment. This input of `initial_backup` is important because when it runs the `db_to_db` command, it will not truncate the target table, as the table does not exist in the destination database.
```bash
./fac-backup-util.sh v0.1.11 initial_backup
# Curl the utility
# Install AWS
# DB to S3 table dump (backups)
# DB to DB table dump (fac-db -> fac-snapshot-db) [No Truncate, as tables dont exist]
# AWS S3 sync (fac-private-s3 -> backups)
```

2. **`deploy_backup`** - runs before a production deployment to ensure S3 contents are synced to the backups bucket and a fresh table dump is stored there.
```bash
./fac-backup-util.sh v0.1.11 deploy_backup
# Curl the utility
# Install AWS
# DB to S3 table dump (backups)
# AWS S3 sync (fac-private-s3 -> backups)
```

3. **`scheduled_backup`** - runs automatically via GH Actions scheduled workflow every two hours in the production environment to ensure that a clean backup exists in S3 and the bucket contents are in sync.

```bash
./fac-backup-util.sh v0.1.11 scheduled_backup
# Curl the utility
# Install AWS
# DB to S3 table dump (fac-db -> backups)
# AWS S3 sync (fac-private-s3 -> backups)
```

4. **`on_demand_backup`** - can be triggered manually via GH Actions workflow at any time on any environment.
```bash
./fac-backup-util.sh v0.1.11 on_demand_backup
# Curl the utility
# Install AWS
# DB to S3 table dump (fac-db -> backups)
# DB to DB  table dump (fac-db -> fac-snapshot-db)
# AWS S3 sync (fac-private-s3 -> backups)
```

### Restoring
Restoring from backups can be run via workflow, from designated individuals. There are two paths that we can restore from.

1. S3 Restore takes a `operation-mm-DD-HH` input (ex `scheduled-06-04-10`), and is required for the backups to be restored. The utility looks in `s3://${bucket}/backups/operation-mm-DD-HH/` for its table dumps, and without supplying the target backups, it will not restore. Once it does a `--data-only` restoration, it will then sync the files from the backups bucket to the application bucket. We do this to ensure the contents of the application bucket are up to date, relative to the data in the database. We know that if we use the latest folder in `/backups/` then the contents of the s3 are the latest available, from the prior backup.
```bash
./fac-restore-util.sh v0.1.11 s3_restore scheduled-06-04-10
# Curl the utility
# Install AWS
# DB to S3 table dump (backups -> fac-db) [Truncate target table before --data-only pg_restore]
# AWS S3 sync (backups -> fac-private-s3)
```
Potential Options for restoration:
```bash
initial-YYYYmmddHHMM
scheduled-mm-dd-HH
daily-mm-dd
```

2. Database to database restoration also can occur as well, using `psql` to dump the tables from the cold store database to the live database.
```bash
./fac-restore-util.sh v0.1.11 db_restore
# Curl the utility
# Install AWS
# DB to DB table dump (fac-snapshot-db -> fac-db) [Truncate target table before dump]
# AWS S3 sync (fac-private-s3 -> backups)
```

### Retention
To optimize on cost, the S3 buckets where backups are stored have a lifecycle policy that deletes objects older than 60 days.

You can verify this policy is in place by running:

```bash
aws s3api get-bucket-lifecycle-configuration --bucket <bucket-name>
```

We do not have sufficient IAM permissions to add, update, or remove lifecycle policies on these buckets ourselves since they are provisioned through the cloud.gov service broker. Any changes to the retention policy must be requested from the cloud.gov team.
