source tools/util_startup.sh

function setup_local_env {

    if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
        startup_log "LOCAL_ENV" "We are in a local envirnoment."
        export AWS_PRIVATE_ACCESS_KEY_ID=longtest
        export AWS_PRIVATE_SECRET_ACCESS_KEY=longtest
        export AWS_S3_PRIVATE_ENDPOINT="http://minio:9000"
        mc alias set myminio "${AWS_S3_PRIVATE_ENDPOINT}" minioadmin minioadmin
        # Do nothing if the bucket already exists.
        # https://min.io/docs/minio/linux/reference/minio-mc/mc-mb.html
        mc mb --ignore-existing myminio/gsa-fac-private-s3
        mc admin user svcacct add --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" myminio minioadmin
        return 0
    fi;
}
