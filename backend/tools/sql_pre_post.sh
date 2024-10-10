source tools/util_startup.sh

function run_sql_files {
  local db="$1"
  local tag="$2"
  local pre_post="$3"
  local which_db="NO_DB_SELECTED"

  if [ $db == $FAC_DB_URI ]; then
    which_db="fac-db"
  fi;
  if [ $db == $FAC_SNAPSHOT_URI ]; then
    which_db="fac-snapshot-db"
  fi;
  
  startup_log $tag "BEGIN"
  # Loop by index.
  for file in `ls dissemination/sql/$which_db/$pre_post/*.sql`; 
  do
    # run_sql has an explicit go/no-go built-in.
    run_sql $db $file
  done
  startup_log $tag "END"
  return 0
}


function sql_pre {
  run_sql_files $FAC_SNAPSHOT_URI "SQL_PRE" "pre"
}

function sql_post {
  run_sql_files $FAC_SNAPSHOT_URI "SQL_POST" "post"
  # Vacuum things when we're done.
  # Cannot run inside a transaction.
  $PSQL_EXE_NO_TXN $FAC_SNAPSHOT_URI -c "VACUUM (FULL, VERBOSE, ANALYZE);"
}
