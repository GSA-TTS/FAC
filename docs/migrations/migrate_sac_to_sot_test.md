## Steps taken to test the migration of intake and disseminated data to the Audit model on staging

### Authenticate with Cloud Foundry
```bash
cf login -a api.fr.cloud.gov --sso
Select an org:
1. gsa-tts-oros-fac
Select a space:
5. staging
```

### Clear out existing audit data (without tampering with pre-migration data)
Tunnel into the staging database:
```bash
cf connect-to-service -no-client gsa-fac fac-db
```

Execute the following scripts to clear out audit data:
```sql
DELETE FROM public.audit_history;
UPDATE public.audit_access SET audit_id=null WHERE audit_id IS NOT NULL;
UPDATE public.audit_deletedaccess SET audit_id=null WHERE audit_id IS NOT NULL;
UPDATE public.audit_submissionevent SET audit_id=null WHERE audit_id IS NOT NULL;
UPDATE public.audit_singleauditchecklist SET migrated_to_audit=false WHERE migrated_to_audit = true;
UPDATE public.audit_excelfile SET audit_id=null WHERE audit_id IS NOT NULL;
UPDATE public.audit_singleauditreportfile SET audit_id=null WHERE audit_id IS NOT NULL;
DELETE FROM public.audit_auditvalidationwaiver;
DELETE FROM public.audit_audit;
```

### SSH into the staging instance
Execute the following:
```bash
cf ssh gsa-fac
/tmp/lifecycle/shell
source tools/setup_env.sh
setup_env
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
```

Then, you can run the management command.
```bash
python manage.py migrate_audits
```
