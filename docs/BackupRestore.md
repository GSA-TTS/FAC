# Backup and Restore Procedures

## Background

The application, developed using the django framework, persists data in two places. These are:

The FAC applocation is deployed in cloud.gov spaces.

The codebase is maintained in Github.com repositories, and is out of the scope of this document.

The application, developed using the django framework, persists data in two places. These are:

- PostgresSQL RDBMS for structured content.
- S3 buckets for uploaded documents.

Cloud.gov offers both PostgreSQL and S3 as managed services that FAC uses.

## Motivation

Data persisted using services from coud.gov are backed up everyday as part of the service offering. These backups cam be used to restore the service to a previous state using tools and processs defined by cloud.gov .
However, the FAC team would like to have additional processes in place to cover inadevertent or malicious corruption of the data that may happen intra-day or from which there may be a need to recover faster and more efficiently than the mechansims offered by cloud.gov.

## Tooling

The FAC team has opted to use `django-dbbackup`, an open-source backup and restore library.
Backups will be stored in a cloud.gov S3 bucket. This bucket is different from the buckets used by the application for its normal operations. Two buckets are being used by FAC for backups:

- `production` S3 bucket named `backups`
- `dev` Se bucket named `backups`

These S3 buckets are bound to the application prior to a backup or restore process, and unbound once the process is complete. This is to ensure that these buckets remain safe even when the buckets containing the application's data are somehow compromised.

The FAC application includes Github workflows, shell scripts and Python modules to use the above tools in an efficient and controlled manner.

## Backup Restore paths

The following table summarizes the allowed pathe for backup and restore operations.

|Source Space| Target Space| Purpose |
|---|---|---|
|`peoduction`|`production`|Recovery|
|`peoduction`|`staging`|Keep  `staging` in sync|
|`dev`|`dev`|Testing|
|`dev`|`preview`|Testing|

## Backup Procedures

These are completely automated procedures. They are triggerred:

- before every deployment of the FAC application to `production`, as well as
- every day after close of normal business hours

Daily backups are done both in `production` and `dev` spaces.

## Restore Procedure

Data may be restored to an allowed space using a backup taken from a space as specified earlier in this document.

Data is restored to `staging` from `production` , and to `dev` from `dev` on a daily basis without manual involvement.

Restoring to other spaces is triggerred by manually invoking a Github workflow. The speific backup that needs to be restored must be specified as an argument to the process.

Restore is a destructive process in that it completely wipes out the data in the target environment befor populating it with data from the backup.

Consequently, the ability to do a manual restore is restricted to members of the FACAdmin team.

*TODO* An `admin` tool to list the backups that are currently available to restore.

## Retention

Backups are periodically purged from the S3 buckets since we no longer need old backups when we have more recent ones. Purging happens on a daily basis to implement the follwing retention policy:

- Retain the *two* most recent backups taken prior to deployment of the FAC application to `production`
- Retain a rolling *seven* days worth of daily `peoduction` backups
- Retain a rolling *one* day worth of daily `dev` backups
