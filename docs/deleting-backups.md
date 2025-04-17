### Informational document regarding Management Command "delete_stale_backups"

The purpose of this document is to highlight examples for when a developer wishes to delete stale backups from the s3 bucket `backups`.

**Warning:** This command is classified as a destructive command, and should only be run after receiving confirmation from members of the team, and after putting a formal annoucement in the developer slack channel. It is advised that after this command is run, to take a formal backup of the environment just for extra precautions.

#### Information:
The management command is located here: [delete_stale_backups.py](../backend/support/management/commands/delete_stale_backups.py). This command accepts two inputs. `--days` & `--delete`.
- The value of `--days` must be greater than or equal to `14` (`--days 14`)
- The value of `--delete` is required to actually perform the delete, and is a boolean (`--delete true`)
- The full command to perform a delete will look like this:
`python manage.py delete_stale_backups --days 14 --delete true`

#### How to perform a delete
1. Login to cloud.gov `cf login -a api.fr.cloud.gov --sso`
2. Select the target environment if you have not done so after successful authentication `cf t -s <env>`
3. Open a new terminal and tail the logs `cf logs gsa-fac | grep "delete_stale_backups"`
4. Run the command via tasks:
`cf run-task gsa-fac -k 2G -m 3G --name delete_stale_backups --command "python manage.py delete_stale_backups --days 14 --delete true" --wait`
5. Wait for the command to finish.
6. Navigate to [The backup environment action](https://github.com/GSA-TTS/FAC/actions/workflows/fac-backup-util.yml) and perform a backup with the following inputs or alternatively, navigate to [the scheduled backup action](https://github.com/GSA-TTS/FAC/actions/workflows/fac-backup-scheduler.yml) and run.
```sh
branch: main
environment: <env where backups were just deleted (dev/staging/prod)>
version: v0.1.11
operation: on_demand_backup
```

#### Operation outputs examples (Fail):
```
~$ python manage.py delete_stale_backups --days 13
Days cannot less than 14 to prevent up-to-date backups from being deleted. Exiting...
~$

~$ python manage.py delete_stale_backups --days 0 --delete true
Days cannot less than 14 to prevent up-to-date backups from being deleted. Exiting...
~$

~$ python manage.py delete_stale_backups --days 14 --delete true
Object backups/on-demand/02-04-13/public-audit_access.dump younger than 2025-01-22 18:44:02.406263+00:00. Not deleting.
Object backups/on-demand/02-04-13/public-audit_deletedaccess.dump younger than 2025-01-22 18:44:02.406263+00:00. Not deleting.
[...]
```

#### Operation outputs example (Pass):
```
~$ python manage.py delete_stale_backups --days 14 --delete true

Deleting backups/on-demand/02-03-19/public-audit_access.dump last modified on 2025-01-22 18:44:02.406263+00:00
Deleting backups/on-demand/02-03-19/public-audit_deletedaccess.dump last modified on 2025-01-22 18:44:02.406263+00:00
[...]
```

