vcap_services='{
  "aws-rds": [
    {
      "label": "aws-rds",
      "provider": null,
      "plan": "medium-gp-psql",
      "name": "db",
      "tags": ["database", "RDS"],
      "instance_guid": "UUIDINDIA1",
      "instance_name": "db",
      "binding_guid": "UUIDINDIA2",
      "binding_name": null,
      "credentials": {
        "db_name": "DBNAMEINDIA",
        "host": "host.us-gov-india-1.rds.amazonaws.com",
        "name": "DBNAMEINDIA",
        "password": "PASSWORDINDIA",
        "port": "5432",
        "uri": "postgres://USERNAMEINDIA:PASSWORDINDIA@host.us-gov-india-1.rds.amazonaws.com:5432/DBNAMEINDIA",
        "username": "USERNAMEINDIA"
      },
      "syslog_drain_url": null,
      "volume_mounts": []
    }
  ]
}'

# Sets up a fake VCAP_SERVICES environment variable when testing locally
function setup_fake_vcap_services {
    if [[ -n "${ENV}" ]]; then
        startup_log "LOCAL_ENV" "Environment set as: ${ENV}"
    else
        startup_log "LOCAL_ENV" "No environment variable ${ENV} is set!"
        return -1
    fi;

    local result=0
    if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
        export VCAP_SERVICES="${vcap_services}"
        result=$?
        startup_log "${result}"
    else
        startup_log "setup_fake_vcap_services should not be used in the ${ENV} environment!"
        return -1
    fi;
    return $result
}
