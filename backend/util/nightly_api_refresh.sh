#!/bin/bash
set -e

source tools/util_startup.sh
source tools/setup_env.sh
source tools/sql_pre_post.sh
setup_env

# Run an RDS backup, to refresh dissemination_* in FAC_SNAPSHOT from FAC_DB
#./../fac-backup-util.sh "v0.1.9" "rds_backup"
./fac-backup-util.sh "$1" "$2"
gonogo "fac-backup-util"

# Run the pre/post.
sql_pre_fac_snapshot_db
gonogo "sql_pre_fac_snapshot_db"

sql_post_fac_snapshot_db
gonogo "sql_post_fac_snapshot_db"

# We might, at some point, 
# consider running a vacuum on DB1
# as part of a nightly or weekly job.
# Below is *representative* code. 
# run_sql $FAC_DB_URI -c "VACUUM(FULL, ANALYZE)"
