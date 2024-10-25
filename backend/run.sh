#!/bin/bash

# Source everything; everything is now a function.
# Remember: bash has no idea if a function exists. Similarly,
# bash has horrible scoping, so use of `local` in functions is 
# critical for cleanliness in the startup script.
source tools/util_startup.sh
# This will choose the correct environment
# for local envs (LOCAL or TESTING) and cloud.gov
source tools/setup_env.sh
source tools/cgov_util_local_only.sh
source tools/curation_audit_tracking_disable.sh
source tools/sling_bulk_export.sh
source tools/migrate_app_tables.sh
source tools/seed_cog_baseline.sh
source tools/setup_env.sh
source tools/sql_pre_post.sh
source tools/util_startup.sh

#####
# SETUP THE LOCAL ENVIRONMENT
setup_env
gonogo "setup_env"

#####
# SIMULATE DEPLOY BACKUP
# Before we deploy, we always get a copy of dissemination_*
# tables into fac-snapshot-db. We need to simulate this locally
# so that we can run SQL pre/post operations on fac-snapshot-db.
cgov_util_local_only
gonogo "cgov_util_local_only"

#####
# SQL PRE
# We have SQL that we want to run before the migrations and sling are run.
# This tears down things that would conflict with migrations, etc.
sql_pre
gonogo "sql_pre"
curation_audit_tracking_disable
gonogo "curation_audit_tracking_disable"

#####
# MIGRATE APP TABLES
migrate_app_tables
gonogo "migrate_app_tables"

#####
# SQL POST
# Rebuild the API and prepare the system for execution.
# Runs after migrations.
sql_post
gonogo "sql_post"

#####
# BULK EXPORT
# Creates CSV exports of all of the public data,
# placing it in the fac-private-s3 bucket.
sling_bulk_export
gonogo "sling_bulk_export"

#####
# SEED COG/OVER TABLES
# Setup tables for cog/over assignments
seed_cog_baseline
gonogo "seed_cog_baseline"

#####
# CREATE STAFF USERS
# Prepares staff users for Django admin
python manage.py create_staffusers

#####
# LAUNCH THE APP
# We will have died long ago if things didn't work.
npm run dev & python manage.py runserver 0.0.0.0:8000
