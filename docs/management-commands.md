# Django management commands

In order to use a management command, you must be local to the FAC instance executing.

Locally, this means you have the stack up, and have attached to the container.

```
docker exec -it backend-web-1 /bin/bash
```

To run commands in `PREVIEW`, `DEV`, or `STAGING`, you need to connect to the instance via SSH using the `cf` API.

To run commands in `PRODUCTION`, SSH needs to be enabled. It is recommended that you write out your commands in a text file first, and execute them one line at a time using `CTRL-K` in VSCode. This way, the command history can be pasted into the SSH disable ticket.

## curation.curation_audit_tracking

The management command is only of use if there is manual database work happening in production. This should be the exceedingly rare exception. Usually, this will be enabled/disabled in Python via the block `with CurationTracking()`.

To use, first init. Then enable. Do the work. Then disable.

Failure to disable could lead to *significant* database bloat.

* `curation_audit_tracking -i`: Initializes curation tracking code. Required before doing anything else
* `curation_audit_tracking -e`: Enables tracking on the tables that are coded into `enable_curation_tracking.sql`
* `curation_audit_tracking -d`: Disables tracking


## curation.update_uei_or_ein_for_submitted_audit

This command allows us to update the UEI or EIN for an audit that has already been submitted and disseminated. It must be run in `production` in order to update the published record.

```bash
python manage.py update_uei_or_ein_for_submitted_audit \
  --report_id 2023-05-GSAFAC-0000000004 \
  --email team_member@gsa.gov \
  --old_ein 123123123 \
  --new_ein 321321321
```

or

```bash
python manage.py update_uei_or_ein_for_submitted_audit \
  --report_id 2023-05-GSAFAC-0000000004 \
  --email team_member@gsa.gov \
  --old_uei ABC123DEF456 \
  --new_uei 456DEF123ABC
```

This will update the `SingleAuditChecklist` model for the report id passed. It checks that the old EIN or UEI is correct/matches before proceeding. It will then change the record and redisseminate, deleting all records from dissemination for that report ID and then disseminating the `SAC` again. 
