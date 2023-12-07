function startup_log {
    local tag="$1"
    local msg="$2"
    echo STARTUP $tag $msg
}

# gonogo
# helps determine if we should continue or quit
function gonogo {
  if [ $? -eq 0 ]; then
    startup_log "STARTUP_CHECK" "$1 PASS"
  else
    startup_log "STARTUP_CHECK" "$1 FAIL"
    exit -1
  fi
}
