source tools/setup_local_env.sh
source tools/setup_cgov_env.sh

function setup_env {
    if [[ -n "${ENV}" ]]; then
        startup_log "LOCAL_ENV" "Environment set as: ${ENV}"
    else
        startup_log "LOCAL_ENV" "No environment variable ${ENV} is set!"
        return -1
    fi;

    local result=0
    if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
        setup_local_env
        result=$?
    else
        setup_cgov_env
        result=$?
    fi;
    return $result
}
