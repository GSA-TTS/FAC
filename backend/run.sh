#!/bin/bash

if [[ -n "${ENV}" ]]; then
  echo "Environment set as: ${ENV}"
else
  echo "No environment variable ${ENV} is set!"
fi;

sleep 10

if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
    export AWS_PRIVATE_ACCESS_KEY_ID=longtest
    export AWS_PRIVATE_SECRET_ACCESS_KEY=longtest
    export AWS_S3_PRIVATE_ENDPOINT="http://minio:9000"
    mc alias set myminio "${AWS_S3_PRIVATE_ENDPOINT}" minioadmin minioadmin
    mc mb myminio/gsa-fac-private-s3
    mc admin user svcacct add --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" myminio minioadmin
fi;

# Migrate first
python manage.py migrate

python manage.py drop_deprecated_api_schema_and_views &&
python manage.py drop_api_views &&
python manage.py drop_api_schema &&
python manage.py create_api_schema &&
python manage.py create_api_views

if [[ ("${ENV}" == "LOCAL" || "${ENV}" == "STAGING") && "$LOAD_TEST_DATA" == 1 ]];
then
  # 175887 162392
  for dbkey in 91651 147134 175887;
  do
    python manage.py workbooks_e2e --email workbook.generator@test.fac.gov --dbkey $dbkey &
  done
fi

username=workbook.generator
is_user_present=$(psql $DATABASE_URL -AXqtc "select exists(select 1 from public.auth_user where username='${username}')")

echo "${username} exists check: $is_user_present"

if [ $is_user_present == "f" ];
then
    pass=`cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 32; echo;`
    psql $DATABASE_URL -q <<-EOSQL
    INSERT INTO public.auth_user
    ("password", last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
    VALUES('${pass}', '2023-08-12 00:00:00.000', false, '${username}', 'Workbook', 'Generator', 'workbook.generator@test.fac.gov', false, false, '2023-08-12 00:00:00.000');
EOSQL
    echo "Created user ${username}"
fi

# Run the build/watch assets + run server at the same time
npm run dev & python manage.py runserver 0.0.0.0:8000
