source tools/util_startup.sh

function setup_local_env {

    if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
        startup_log "LOCAL_ENV" "We are in a local envirnoment."
        export AWS_PRIVATE_ACCESS_KEY_ID=localdevkey
        export AWS_PRIVATE_SECRET_ACCESS_KEY=localdevsecret
        export AWS_S3_PRIVATE_ENDPOINT="http://rustfs:9001"
        rc alias set local "${AWS_S3_PRIVATE_ENDPOINT}" rustfsadmin rustfsadmin
        # Do nothing if the bucket already exists.
        rc mb --ignore-existing local/gsa-fac-private-s3
        rc admin service-account create local $AWS_PRIVATE_ACCESS_KEY_ID $AWS_PRIVATE_SECRET_ACCESS_KEY
        return 0
    fi;
}
