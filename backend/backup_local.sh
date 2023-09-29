#!/bin/bash
BUCKET=gsa-fac-private-s3
ENVIRONMENT=LOCAL
#echo "Environment set as: $1"
#export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
DATE=$(date '+%Y-%m-%d-%H%M')
LOG_FILE="$DATE"_backup_log.txt 
DB_BACKUP_FILE="$DATE"-"$ENVIRONMENT"-db-backup.psql.bin
MEDIA_BACKUP_FILE="$DATE"-"$ENVIRONMENT"-media-backup.tar
echo "Backup date: $DATE" > $LOG_FILE
python manage.py collect_metrics >> $LOG_FILE

echo "DB Backup File: $DB_BACKUP_FILE" >> $LOG_FILE
python manage.py dbbackup -o $DB_BACKUP_FILE >&1 >> $LOG_FILE
# need to upload as my config backs up to local backup folder
python manage.py fac_s3 $BUCKET --upload --src backup/$DB_BACKUP_FILE --tgt $DB_BACKUP_FILE

echo "Media Backup File: $MEDIA_BACKUP_FILE" >> $LOG_FILE
python manage.py mediabackup -o $MEDIA_BACKUP_FILE >&1 >> $LOG_FILE
# need to upload as my config backs up to local backup folder
python manage.py fac_s3 $BUCKET --upload --src backup/$MEDIA_BACKUP_FILE --tgt $MEDIA_BACKUP_FILE

python manage.py fac_s3 $BUCKET --ls --tgt $DATE >> $LOG_FILE
python manage.py fac_s3 $BUCKET --upload --src $LOG_FILE --tgt logs/$LOG_FILE
cat $LOG_FILE
rm $LOG_FILE
