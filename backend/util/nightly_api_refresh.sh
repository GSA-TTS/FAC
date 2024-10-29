#!/bin/bash
set -e

source tools/util_startup.sh
source tools/setup_env.sh
source tools/sql_pre_post.sh
setup_env

# Run an RDS backup, to refresh dissemination_* in FAC_SNAPSHOT from FAC_DB
#./../fac-backup-util.sh "v0.1.9" "rds_backup"
# Deploy test
./fac-backup-util.sh "$1" "$2"
gonogo "fac-backup-util"


# Run the pre/post.
sql_pre_fac_snapshot_db
gonogo "sql_pre_fac_snapshot_db"

sql_post_fac_snapshot_db
gonogo "sql_post_fac_snapshot_db"
