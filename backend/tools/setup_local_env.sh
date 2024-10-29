source tools/util_startup.sh

function setup_local_env {

    if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
        startup_log "LOCAL_ENV" "We are in a local envirnoment."

        # Load a fake VCAP_SERVICES file into the environment variable,
        # so we can mimic the cloud.gov setup.
        export VCAP_SERVICES=$(cat config/vcap_services_for_containers.json)
        check_env_var_not_empty "VCAP_SERVICES"

        # export AWS_PUBLIC_ACCESS_KEY_ID="singleauditclearinghouse"
        # export AWS_PUBLIC_SECRET_ACCESS_KEY="singleauditclearinghouse"
        # export AWS_S3_PUBLIC_ENDPOINT="http://minio:9000"


        # https://stackoverflow.com/questions/48712545/break-jq-query-string-into-lines
        # jq is fine with line breaks in strings. Just don't escape them.
        # Makes long queries more readable. Maybe.

        # export AWS_PUBLIC_BUCKET_NAME="fac-public-s3"
        # export AWS_PRIVATE_BUCKET_NAME="fac-private-s3"

        export AWS_PRIVATE_BUCKET_NAME=$(echo $VCAP_SERVICES \
            | jq --raw-output '.s3
                | map(select(.instance_name
                            | contains("fac-private-s3")))
                | .[] .credentials.bucket')
        check_env_var_not_empty "AWS_PRIVATE_BUCKET_NAME"

        export AWS_PUBLIC_BUCKET_NAME=$(echo $VCAP_SERVICES \
            | jq --raw-output '.s3
                | map(select(.instance_name
                            | contains("fac-public-s3")))
                | .[] .credentials.bucket')


        # export AWS_PRIVATE_ACCESS_KEY_ID="singleauditclearinghouse"
        # export AWS_PRIVATE_SECRET_ACCESS_KEY="singleauditclearinghouse"
        # export AWS_S3_PRIVATE_ENDPOINT="http://minio:9000"

        get_aws_s3 "fac-private-s3" "access_key_id"
        export AWS_PRIVATE_ACCESS_KEY_ID=$_GET_AWS_RESULT
        check_env_var_not_empty "AWS_PRIVATE_ACCESS_KEY_ID"

        get_aws_s3 "fac-private-s3" "secret_access_key"
        export AWS_PRIVATE_SECRET_ACCESS_KEY=$_GET_AWS_RESULT
        check_env_var_not_empty "AWS_PRIVATE_SECRET_ACCESS_KEY"

        get_aws_s3 "fac-private-s3" "endpoint"
        export AWS_S3_PRIVATE_ENDPOINT=$_GET_AWS_RESULT
        check_env_var_not_empty "AWS_S3_PRIVATE_ENDPOINT"

        get_aws_s3 "fac-public-s3" "access_key_id"
        export AWS_PUBLIC_ACCESS_KEY_ID=$_GET_AWS_RESULT
        check_env_var_not_empty "AWS_PUBLIC_ACCESS_KEY_ID"

        get_aws_s3 "fac-public-s3" "secret_access_key"
        export AWS_PUBLIC_SECRET_ACCESS_KEY=$_GET_AWS_RESULT
        check_env_var_not_empty "AWS_PUBLIC_SECRET_ACCESS_KEY"

        get_aws_s3 "fac-public-s3" "endpoint"
        export AWS_S3_PUBLIC_ENDPOINT=$_GET_AWS_RESULT
        check_env_var_not_empty "AWS_S3_PUBLIC_ENDPOINT"

        #export MC_HOST_<alias>=https://<Access Key>:<Secret Key>:<Session Token>@<YOUR-S3-ENDPOINT>
        export MC_HOST_myminio="http://${AWS_PRIVATE_ACCESS_KEY_ID}:${AWS_PRIVATE_SECRET_ACCESS_KEY}@minio:9000"
        # mc alias set myminio ${AWS_S3_PRIVATE_ENDPOINT} ${AWS_PRIVATE_ACCESS_KEY_ID} ${AWS_PRIVATE_ACCESS_KEY_ID}
        # until (mc config host add myminio $AWS_PRIVATE_ENDPOINT singleauditclearinghouse singleauditclearinghouse) do echo '...waiting...' && sleep 1; done;
        # Do nothing if the bucket already exists.
        # https://min.io/docs/minio/linux/reference/minio-mc/mc-mb.html
        mc mb --ignore-existing myminio/${AWS_PUBLIC_BUCKET_NAME}
        mc mb --ignore-existing myminio/${AWS_PRIVATE_BUCKET_NAME}

        # MCJ 20241016 FIXME: Is this even needed locally? I don't think so.
        # mc admin user svcacct add \
        #     --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" \
        #     --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" \
        #     myminio minioadmin

        # For database work
        export FAC_DB_URI=${DATABASE_URL} #?sslmode=disable
        export FAC_SNAPSHOT_URI=${SNAPSHOT_URL}
        export PSQL_EXE='psql --single-transaction -v ON_ERROR_STOP=on'
        export PSQL_EXE_NO_TXN='psql -v ON_ERROR_STOP=on'


        # Locally, we need to pull in sling.
        # In production, it gets pulled in via the build/deploy process.
        pushd /tmp
            curl -LO 'https://github.com/slingdata-io/sling-cli/releases/latest/download/sling_linux_amd64.tar.gz'
            tar xf sling_linux_amd64.tar.gz
            rm -f sling_linux_amd64.tar.gz
            chmod +x sling
            mv sling /bin/sling
        popd

        # And we need cgov-util
        pushd /tmp
            local CGOV_VERSION=v0.1.9
            curl -L -O https://github.com/GSA-TTS/fac-backup-utility/releases/download/${CGOV_VERSION}/gov.gsa.fac.cgov-util-${CGOV_VERSION}-linux-amd64.tar.gz
            tar xvzf gov.gsa.fac.cgov-util-${CGOV_VERSION}-linux-amd64.tar.gz gov.gsa.fac.cgov-util
            chmod 755 gov.gsa.fac.cgov-util
            mv gov.gsa.fac.cgov-util /bin/cgov-util
        popd

        export SLING_EXE='/bin/sling'
        export CGOV_UTIL_EXE='/bin/cgov-util'

        show_env_var "AWS_S3_PRIVATE_ENDPOINT"

        $SLING_EXE conns set \
            BULK_DATA_EXPORT \
            type=s3 \
            bucket="${AWS_PRIVATE_BUCKET_NAME}" \
            access_key_id="${AWS_PRIVATE_ACCESS_KEY_ID}" \
            secret_access_key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" \
            endpoint="${AWS_S3_PRIVATE_ENDPOINT}"
        $SLING_EXE conns test BULK_DATA_EXPORT
        gonogo "local_minio_conns_test"

        # We need a config.json in the directory we are running
        # things from (or PWD).
        cp util/load_public_dissem_data/data/config.json .
        gonogo "local copy of config for cgov-util"
        return 0
    fi;
}
