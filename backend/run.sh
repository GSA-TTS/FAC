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
source tools/curation_audit_tracking_init.sh
source tools/api_teardown.sh
source tools/migrate_app_tables.sh
source tools/api_standup.sh
source tools/create_staffusers.sh

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
# MIGRATE APP TABLES
migrate_app_tables
gonogo "migrate_app_tables"

#####
# API STANDUP
# Standup the API, which may depend on migration changes
api_standup
gonogo "api_standup"

#####
# CURATION AUDIT TRACKING
curation_audit_tracking_init
gonogo "curation_audit_tracking_init"

#####
# CREATE STAFF USERS
# Prepares staff users for Django admin
create_staffusers
gonogo "create_staffusers"

#####
# LAUNCH THE APP
# We will have died long ago if things didn't work.
npm run dev & python manage.py runserver 0.0.0.0:8000
