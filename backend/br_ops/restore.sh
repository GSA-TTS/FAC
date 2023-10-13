#!/bin/bash

# Set basic runtime settings
echo "Restoring to env: $1"
echo "Restoring backup named: $2"
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
date=$(date '+%Y-%m-%d-%H%M')
prefix="$date"_"$1"
log_file="$prefix"_restore_log.txt

# Restore the database
echo "Database Backup File: "$2"-db-backup.psql.bin" >> "$log_file"
python manage.py dbrestore -i "$2"-db-backup.psql.bin --noinput >&1 >> "$log_file"

# Restore the media contents
echo "Media Backup File: "$2"-media-backup.tar >> "$log_file"
python manage.py mediarestore -i "$2"-media-backup.tar --noinput >&1 >> "$log_file"

# Collect metrics about what is currently in the db after restore
python manage.py collect_metrics >> "$log_file"

# Upload logfile to s3://backups/logs
python manage.py fac_s3 backups --upload --src "$log_file" --tgt logs/"$log_file"

# Cleanup on disk log file
cat "$log_file"
rm "$log_file"
