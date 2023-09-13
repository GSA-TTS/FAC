#!/bin/bash

export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
python manage.py dbbackup
