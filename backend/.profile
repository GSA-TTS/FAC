#!/bin/bash

set +e

source tools/util_startup.sh
source tools/setup_env.sh
source tools/curation_audit_tracking_disable.sh
source tools/sling_bulk_export.sh
source tools/migrate_app_tables.sh
source tools/seed_cog_baseline.sh
source tools/sql_pre_post.sh

#####
# SETUP THE CGOV ENVIRONMENT
setup_env
gonogo "setup_env"

if [[ "$CF_INSTANCE_INDEX" == 0 ]]; then

    #####
    # SQL PRE
    # We have SQL that we want to run before the migrations and sling are run.
    # This tears down things that would conflict with migrations, etc.
    sql_pre_fac_db
    gonogo "sql_pre_fac_db"
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
    sql_post_fac_db
    gonogo "sql_post_fac_db"

    #####
    # SEED COG/OVER TABLES
    # Setup tables for cog/over assignments
    seed_cog_baseline
    gonogo "seed_cog_baseline"

    #####
    # CREATE STAFF USERS
    # Prepares staff users for Django admin
    python manage.py create_staffusers
    gonogo "create_staffusers"
fi

# Make psql usable by scripts, for debugging, etc.
alias psql='/home/vcap/deps/0/apt/usr/lib/postgresql/*/bin/psql'
