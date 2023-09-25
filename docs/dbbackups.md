# Database Backups

Information regarding the django utility can be found [on the documentation page](https://django-dbbackup.readthedocs.io/en/master/commands.html)
Database backups occur in the following ways:
1. Django backups
```bash
python manage.py dbbbackup
python manage.py mediabackup
```
2. Django restores
```bash
python manage.py dbrestore
python manage.py mediarestore
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
