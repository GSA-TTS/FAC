source tools/variables.sh

function startup_log {
    local tag="$1"
    local msg="$2"
    echo "STARTUP" "$tag" "$msg"
}

# gonogo
# helps determine if we should continue or quit
function gonogo {
  if [ $? -eq 0 ]; then
    startup_log "STARTUP_CHECK" "$1 PASS"
    return 0
  else
    startup_log "STARTUP_CHECK" "$1 FAIL"
    exit 1
  fi
}

# 2024-10-10T12:28:29.61-0400 [APP/PROC/WEB/0] OUT CHECK_TABLE_EXISTS START: public.dissemination_general
# 2024-10-10T12:28:29.65-0400 [APP/PROC/WEB/0] OUT CHECK_TABLE_EXISTS END: public.dissemination_general = t
# 2024-10-10T12:28:29.65-0400 [APP/PROC/WEB/0] OUT CHECK_TABLE_EXISTS: public_data_v1_0_0.metadata
# 2024-10-10T12:28:29.68-0400 [APP/PROC/WEB/0] OUT CHECK_TABLE_EXISTS public_data_v1_0_0.metadata: f
# 2024-10-10T12:28:29.68-0400 [APP/PROC/WEB/0] OUT Exit status 1
# 2024-10-10T12:28:29.68-0400 [CELL/SSHD/0] OUT Exit status 0

function check_table_exists() {
  local db_uri="$1"
  local schema="$2"
  local table="$3"

  echo "CHECK_TABLE_EXISTS START: $schema.$table"
  # >/dev/null 2>&1
  # The qtAX incantation lets us pass the PSQL result value back to bash.
  result=`$PSQL_EXE "$db_uri" -qtAX -c "SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = '$schema' AND tablename = '$table');"`
  # Flip TRUE to a 0, because UNIX considers a 0 exit code to be good. 
  if [ "$result" = "t" ]; then
    echo "CHECK_TABLE_EXISTS END: $schema.$table = 0"
    FUNCTION_RESULT=0
  else
    echo "CHECK_TABLE_EXISTS END: $schema.$table = 1"
    FUNCTION_RESULT=1
  fi
  return 0
}

function check_schema_exists () {
  local db_uri="$1"
  local schema_name="$2"
  echo "CHECK_SCHEMA_EXISTS START: $schema_name"
  result=`$PSQL_EXE $db_uri -qtAX -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = '$schema_name');"`
  # Flip TRUE to a 0, because UNIX considers a 0 exit code to be good. 
  if [ "$result" = "t" ]; then
    echo "CHECK_SCHEMA_EXISTS END: $schema_name = 0"
    FUNCTION_RESULT=0
  else
    echo "CHECK_SCHEMA_EXISTS END: $schema_name = 1"
    FUNCTION_RESULT=1
  fi
  return 0
}

function run_sql () {
    local db_uri="$1"
    local path="$2"
    echo "BEGIN run_sql < $path"
    $PSQL_EXE $db_uri < $path
    gonogo "GONOGO run_sql < $path"
}
