#!/bin/bash

echo "dbbackup name: $1"
echo "mediabackup name: $2"
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
python manage.py dbrestore -i "$1" --noinput
python manage.py mediarestore -i "$2" --noinput
