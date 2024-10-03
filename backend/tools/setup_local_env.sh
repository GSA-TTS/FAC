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
        
        # For database work
        export FAC_DB_URI=${DATABASE_URL}?sslmode=disable
        export FAC_SNAPSHOT_URI=${SNAPSHOT_URL}?sslmode=disable
        export PSQL_EXE='psql -v ON_ERROR_STOP=on'
        export SLING_EXE='/bin/sling'
        export CGOV_UTIL_EXE='/bin/cgov-util'
        
        # Locally, we need to pull in sling.
        # In production, it gets pulled in via the build/deploy process.
        curl -LO 'https://github.com/slingdata-io/sling-cli/releases/latest/download/sling_linux_amd64.tar.gz'
        tar xf sling_linux_amd64.tar.gz
        rm -f sling_linux_amd64.tar.gz
        chmod +x sling
        mv sling /bin/sling
        # And we need cgov-util
        curl -L -O https://github.com/GSA-TTS/fac-backup-utility/releases/download/v0.1.8/gov.gsa.fac.cgov-util-v0.1.8-linux-amd64.tar.gz
        tar xvzf gov.gsa.fac.cgov-util-v0.1.8-linux-amd64.tar.gz gov.gsa.fac.cgov-util
        chmod 755 gov.gsa.fac.cgov-util
        mv gov.gsa.fac.cgov-util /bin/cgov-util
        # We need a config.json in the directory we are running
        # things from (or PWD).
        cp util/load_public_dissem_data/data/config.json .
        gonogo "local copy of config for cgov-util"
        return 0
    fi;
}
