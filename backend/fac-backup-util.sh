#!/bin/bash
set -e
source tools/util_startup.sh
run_option=$1
s3_name="fac-private-s3"
backup_s3_name="backups"
db_name="fac-db"
backup_db_name="fac-snapshot-db"
date=$(date +%Y%m%d%H%M)
mkdir tmp && cd tmp || return

GetUtil() {
    local version="v0.1.0"
    curl -x "$https_proxy" -L "https://github.com/GSA-TTS/fac-backup-utility/releases/download/$version/gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz" -O
    tar -xvf gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz && rm gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz
}
InstallAWS() {
    ./gov.gsa.fac.cgov-util install_aws
}
AWSS3Sync() {
    ./gov.gsa.fac.cgov-util s3_sync --source_s3 s3://"$1"/ --dest_s3 s3://"$2"/
}
RDSToS3Dump() {
    ./gov.gsa.fac.cgov-util db_to_s3 --db "$1" --s3path s3://"$2"/"$date"/
}
RDSToRDS() {
    ./gov.gsa.fac.cgov-util db_to_db --src_db "$1" --dest_db "$2"
}

if [ "$run_option" == "deploy_backup" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    RDSToS3Dump "$db_name" "$backup_s3_name"
    gonogo "db_to_s3"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "scheduled_backup" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    RDSToS3Dump "$db_name" "$backup_s3_name"
    gonogo "db_to_s3"
    RDSToRDS "$db_name" "$backup_db_name"
    gonogo "db_to_db"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "media_sync" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
fi
