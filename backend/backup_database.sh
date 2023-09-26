#!/bin/bash

echo "Environment set as: $1"
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
date=$(date '+%Y-%m-%d-%H%M')
python manage.py dbbackup -o "$1-db-backup-$date.psql.bin"
python manage.py mediabackup -o "$1-media-backup-$date.tar"
