# Steps taken
```sh
cf t -s <env>
```

Bind the backups bucket to the application
```sh
cf bind-service gsa-fac backups
```

Restart the app so changes occur and wait for the instance to come back up
```sh
cf restart gsa-fac
```

Unbind the existing fac-private-s3 bucket from the app
```sh
cf unbind-service gsa-fac fac-private-s3
```

Rebind the fac-private-s3 bucket with the backups bucket as an additional instance
```sh
cf bind-service gsa-fac fac-private-s3 -c '{"additional_instances": ["backups"]}'
```

Restart the app so changes occur and wait for the instance to come back up
```sh
cf restart gsa-fac
```

Running things by hand:
```sh
cf ssh gsa-fac
/tmp/lifecycle/shell
source .profile
set +e

curl -x $https_proxy -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && rm awscliv2.zip
./aws/install -i ~/usr -b ~/bin
/home/vcap/app/bin/aws --version

export S3CREDS="$(echo $VCAP_SERVICES|jq -r '.s3')"
export FACPRIVS3="$(echo $S3CREDS|jq '.[]|select(.name=="fac-private-s3")'|jq '.credentials')"
export AWS_ACCESS_KEY_ID="$(echo "$FACPRIVS3"|jq -r '.access_key_id')"
export AWS_SECRET_ACCESS_KEY="$(echo "$FACPRIVS3"|jq -r '.secret_access_key')"
export FAC_MEDIA_BUCKET="$(echo "$FACPRIVS3"|jq -r '.bucket')"
export AWS_DEFAULT_REGION='us-gov-west-1'
export FACBACKUPS="$(echo $S3CREDS|jq '.[]|select(.name=="backups")'|jq '.credentials')"
export BACKUPS_BUCKET="$(echo "$FACBACKUPS"|jq -r '.bucket')"
date=$(date +%Y%m%d%H%M)

curl -x $https_proxy -L "https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-amd64.zip" -o "s3tar-linux-amd64.zip"
unzip s3tar-linux-amd64.zip && rm s3tar-linux-amd64.zip

unset https_proxy

./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -cvf s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/archive.tar s3://${FAC_MEDIA_BUCKET} --storage-class INTELLIGENT_TIERING

/home/vcap/app/bin/aws s3 ls s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/

/home/vcap/app/bin/aws s3 sync s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/ s3://${BACKUPS_BUCKET}/mediabackups/$date/ --storage-class INTELLIGENT_TIERING
/home/vcap/app/bin/aws s3 ls s3://${BACKUPS_BUCKET}/mediabackups/$date/


# Cleanup the source bucket so older backups don't get added to the tar
/home/vcap/app/bin/aws s3 rm s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/archive.tar
/home/vcap/app/bin/aws s3 rm s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/
/home/vcap/app/bin/aws s3 rm s3://${FAC_MEDIA_BUCKET}/mediabackups/

# List contents of source bucket to ensure everything was deleted properly
/home/vcap/app/bin/aws s3 ls s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/
/home/vcap/app/bin/aws s3 ls s3://${FAC_MEDIA_BUCKET}/

```

Tail the logs on the app
```sh
cf logs gsa-fac | grep "APP/TASK/media_backup"
```

Run the media backups via cf-tasks
```sh
cf run-task gsa-fac -k 2G -m 2G --name media_backup --command "./s3-sync.sh"
```
