# Database Backups

Information regarding the django utility can be found [on the documentation page](https://django-dbbackup.readthedocs.io/en/master/commands.html)
Database backups occur in the following ways:
1. Django backups
```bash
python manage.py dbbbackup
```
2. Django restores
```bash
python manage.py dbrestore
```
3. Backups in the prod environment occur every deployment, [before the most recent code is applied](https://github.com/GSA-TTS/FAC/blob/fd3a59287d58aec06a78d6da3b42a5def8fc9c98/.github/workflows/deploy-application.yml#L72-L100)
4. Manual steps are listed in the following document for where to catalog backups
    * [Deploying](./deploying.md)
    * Login via CF and tail the logs during a deployment (before it gets to deploy application stage)
    * Post the most recent dbbackup and mediabackup file names in https://github.com/GSA-TTS/FAC/issues/2221
```bash
cf login -a api.fr.cloud.gov --sso
Select an org:
1. gsa-tts-oros-fac
Select a space:
5. production
cf logs gsa-fac
```

# Media Backups
```sh
cf t -s <env>
```

Bind the backups bucket to the application
```sh
cf bind-service gsa-fac backups
```

Restart the app so changes occur and wait for the instance to come back up
```sh
cf restart gsa-fac --strategy rolling
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
cf restart gsa-fac --strategy rolling
```

Running things by hand:
[s3-sync](../backend/s3-sync.sh)
[s3-tar-snapshot](../backend/s3-tar-snapshot.sh)

Tail the logs on the app
```sh
cf logs gsa-fac | grep "APP/TASK/media_backup"
```

Run the media backups via cf-tasks
```sh
cf run-task gsa-fac -k 2G -m 2G --name media_backup --command "./s3-sync.sh"
```
