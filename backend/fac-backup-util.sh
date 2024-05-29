#!/bin/bash
set -e
source tools/util_startup.sh
base_environment=$1
run_option=$2
export ENV="${base_environment}"
date=$(date +%Y%m%d%H%M)
mkdir tmp && cd tmp || return

function GetUtil() {
    local version="v0.1.0"
    curl -x "$https_proxy" -L "https://github.com/GSA-TTS/fac-backup-utility/releases/download/$version/gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz" -O
    tar -xvf gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz && rm gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz
}
function InstallAWS() {
    ./gov.gsa.fac.cgov-util install_aws
}
function AWSS3Sync() {
    ./gov.gsa.fac.cgov-util s3_sync --source_s3 s3://fac-private-s3/ --dest_s3 s3://backups/
}
function RDSToS3Dump() {
    ./gov.gsa.fac.cgov-util db_to_s3 --db fac-db --s3path s3://backups/"$date"/
}
function RDSToRDS() {
    ./gov.gsa.fac.cgov-util db_to_db --src_db fac-db --dest_db fac-snapshot-db
}
# S3ToRDSTableRestore() {
#     ./gov.gsa.fac.cgov-util s3_to_db --db fac-db --s3path s3://backups/"$date"/
# }

if [ "$run_option" == "deploy_backup" ]; then
    GetUtil
    gonogo "curl_util"
    InstallAWS
    gonogo "install_aws"
    RDSToS3Dump
    gonogo "db_to_s3"
    AWSS3Sync
    gonogo "s3_sync"
elif [ "$run_option" == "scheduled_backup" ]; then
    GetUtil
    gonogo "curl_util"
    InstallAWS
    gonogo "install_aws"
    RDSToS3Dump
    gonogo "db_to_s3"
    RDSToRDS
    gonogo "db_to_db"
    AWSS3Sync
    gonogo "s3_sync"
fi
