#!/bin/bash

export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
date=$(date '+%Y-%m-%d-%H%M')
python manage.py dbbackup -o "prod-db-backup-$date.dump"
python manage.py mediabackup -o "prod-media-backup-$date.tar"
