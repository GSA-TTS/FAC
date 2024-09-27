source tools/util_startup.sh

function install_local_sling {
    curl -LO 'https://github.com/slingdata-io/sling-cli/releases/latest/download/sling_linux_amd64.tar.gz' 
    gonogo "curl sling"
    tar xf sling_linux_amd64.tar.gz 
    gonogo "tar xf sling"
    rm -f sling_linux_amd64.tar.gz 
    gonogo "rm sling.tar"
    chmod +x sling
    gonogo "chmod sling"
    mv sling /usr/local/bin/sling
    gonogo "mv sling"
    export SLING_EXE='/usr/local/bin/sling'
    return 0
}

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
        
        # For database work
        export FAC_DB_URI=${DATABASE_URL}?sslmode=disable
        export FAC_SNAPSHOT_URI=${SNAPSHOT_URL}?sslmode=disable
        export PSQL_EXE='psql -v ON_ERROR_STOP=on'
        install_local_sling
        
        return 0
    fi;
}
