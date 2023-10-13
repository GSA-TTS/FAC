#!/usr/bin/env bash
set -e


echo "This script works only in dev amd production spaces as we take backups only in these spaces"
echo "It assumes that the S3 bucket named 'backups' has been bound"

cfspace=$(cf target |tail -1|cut -d':' -f2|xargs)
echo "Space: ${cfspace}"

if [[ "$cfspace" != "dev" && "$cfspace" != "prodiction" ]]; then
  echo "Error: Backups are only avaiable in dev or production"
  exit 1
fi

export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
python manage.py fac_s3 backups --ls
