#!/bin/bash

# Source everything; everything is now a function.
# Remember: bash has no idea if a function exists, 
# so a typo in a function name will fail silently. Similarly,
# bash has horrible scoping, so use of `local` in functions is 
# critical for cleanliness in the startup script.
source tools/util_startup.sh
# This will choose the correct environment
# for local envs (LOCAL or TESTING) and cloud.gov
source tools/setup_env.sh
source tools/api_teardown.sh
source tools/sling_public_tables.sh
source tools/migrate_app_tables.sh
source tools/api_standup.sh
source tools/seed_cog_baseline.sh

#####
# SETUP THE LOCAL ENVIRONMENT
setup_env
gonogo "setup_env"

#####
# API TEARDOWN
# API has to be deprecated/removed before migration, because
# of tight coupling between schema/views and the dissemination tables
api_teardown
gonogo "api_teardown"

#####
# PUBLIC TABLES
# We only want to do this if the sling tables don't exist.
# Because they should run nightly, we'll generally skip this
# during startup.
check_table_exists $FAC_DB_URI 'public_data_v1_0_0.general'
if [ $? -ne 0 ]; 
then
    # This takes time. We'll need to watch our deploy timeout.
    # And, it will interrupt search/API while the tables are being
    # recreated. So, we generally don't want to do this on deploy, only
    # as part of nightly batch jobs.
    sling_public_tables
    gonogo "sling_public_tables"
else
    startup_log "RUN" "Skipping sling"
fi

#####
# MIGRATE APP TABLES
migrate_app_tables
gonogo "migrate_app_tables"

#####
# API STANDUP
# Standup the API, which may depend on migration changes
api_standup
gonogo "api_standup"

#####
# SEED COG/OVER TABLES
# Setup tables for cog/over assignments
seed_cog_baseline
gonogo "seed_cog_baseline"

#####
# LAUNCH THE APP
# We will have died long ago if things didn't work.
npm run dev & python manage.py runserver 0.0.0.0:8000
