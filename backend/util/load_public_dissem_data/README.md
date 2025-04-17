# loading public data

This provides a containerized data loading process that sets up your local FAC in a manner that duplicates the live/production app.

The data we are using is public, historic data. It can be replaced, at a later point, with data that is more current.

## Full clean

You might want a completely clean local stack to start. It is not strictly necessary. If you get key conflicts, it means you already have some of this historic data loaded.

### Wipe the stack

From the backend folder

```
make -i docker-full-clean
```

Note the `-i` flag. This means `make` should ignore errors. You want it to, so it will keep going and wipe everything.

```
make docker-first-run
```

and then

```
docker compose up
```

We need the stack running for this whole process.

## Grab the data

From GDrive, grab the data.

https://drive.google.com/file/d/1_EmykQamgw9VhjhFAPzgjQdk7pMzHgJW/view?usp=drive_link

Grab the file `sac-user-access-valwaiver-pdf-xlsx-event-data-03-28-25.dump` (~6GB).
Put it in util/load_public_dissem_data/data (a child of this directory).

This will yield a dataset with the following counts:


| table | count |
| --- | --- |
| audit_singleauditchecklist | 354,222 |
| audit_access | 1,195,595|
| auth_user | 75,461 |
| dissemination_additionalein | 59,251 |
| dissemination_additionaluei | 15,101 |
| dissemination_captext | 116,694 |
| dissemination_federalaward | 5,811,948 |
| dissemination_finding | 507,895 |
| dissemination_findingtext | 120,290 |
| dissemination_general | 343,114 |
| dissemination_note | 530,405 |
| dissemination_passthrough | 4,025,800 |
| dissemination_secondaryauditor | 1,803 |
| audit_ueivalidationwaiver | 0 |
| audit_sacvalidationwaiver | 1 |
| audit_singleauditreportfile | 362229 |
| audit_excelfile | 339149 |
| audit_submissionevent | 1591563 |

We use a subdirectory to make the .gitignore work easier/safer.

# truncate and load

Use the menu script in this folder.

```
./menu.bash
```

This will give you several options:

```
1) Truncate tables                   6) Check row counts
2) Load finished data                7) Dump tables for reuse
3) Load raw data                     8) Reset migrated_to_audit
4) Generate fake suppressed reports  9) Truncate audit_audit
5) Re-disseminate SAC records	       10) Quit
```

## 1) Truncate tables

This runs the following SQL:

```
		truncate
      audit_access,
      audit_singleauditchecklist,
      auth_user,
      dissemination_additionalein,
      dissemination_additionaluei,
      dissemination_captext,
      dissemination_federalaward,
      dissemination_finding,
      dissemination_findingtext,
      dissemination_general,
      dissemination_note,
      dissemination_passthrough,
      dissemination_secondaryauditor,
      audit_ueivalidationwaiver,
      audit_sacvalidationwaiver,
      audit_singleauditreportfile,
      audit_excelfile,
      audit_submissionevent
    cascade;
```

This effectively cleans all data that we might be working and testing with.

## 2) Load finished data
This will reload:

* audit_access
* audit_singleauditchecklist
* auth_user
* dissemination_*

This also runs `reset_migrated_to_audit`, so that the data is ready for migration to SOT.

## 3) Load raw data

This option allows you to load the data from production. That data then must be processed (e.g. fake tribal audits created + all data disseminated) before you have finished data.

This requires `data/internal-and-external-20250402.dump`, which can be found [here](https://drive.google.com/file/d/1qocTTvgg-uyrz3bzJaKqNuROTyKeHWJ9/view?usp=sharing)

## 4) Generate fake suppressed reports

The data as loaded is 100% public data. This modifies 500 records per audit year so that they appear to be suppressed/Tribal audits. It inserts a tribal attestation record saying that the record should be suppressed, and then updates the organization type so that it is `tribal`.

When done, it should report 4000 records updated.

## 5) Re-disseminate SAC records

This truncates all of the `dissemination_` tables, and then re-disseminates every record in the SAC. This populates the dissemination tables, which is necessary for API testing.

This takes a long time. Think at least an hour. Go make coffee. Hand grind it. Meaning "with your bare hands." You have time.

## 6) Check row counts

This verifies the row counts in every table we loaded.

```
Checking counts
[PASS] audit_singleauditchecklist has 354222 rows
[PASS] audit_access has 1195595 rows
[PASS] auth_user has 75461 rows
[PASS] dissemination_additionalein has 59251 rows
[PASS] dissemination_additionaluei has 15101 rows
[PASS] dissemination_captext has 116694 rows
[PASS] dissemination_federalaward has 5811960 rows
[PASS] dissemination_finding has 507895 rows
[PASS] dissemination_findingtext has 120290 rows
[PASS] dissemination_general has 343116 rows
[FAIL] dissemination_note should have 530405 rows; it has  530407
[PASS] dissemination_passthrough has 4025800 rows
[PASS] dissemination_secondaryauditor has 1803 rows
[PASS] audit_ueivalidationwaiver has 0 rows
[PASS] audit_sacvalidationwaiver has 1 rows
[PASS] audit_singleauditreportfile has 362229 rows
[PASS] audit_excelfile has 339149 rows
[PASS] audit_submissionevent has 1591563 rows
```

## 7) Dump tables for reuse

Need desc for this

## 8) Reset migrated_to_audit

This option will set `migrated_to_audit` to `false` for all rows in the `singleauditchecklist`.

This is run after data load, but is included in the menu as an option.

## 9) Truncate audit_audit

This truncates the audit_audit table with `CASCADE`, and then runs the `migrated_to_audit` reset.

## overriding the data filename

You can run

```
FILENAME=data/some-other-dumpfile.dump ./menu.bash
```

to chose the name of the file you want to load. Use plain-text dumpfiles.


# how the data was prepared

We began with a dump of `production`, and removed all tribal audits that were set to be suppressed. That is, we only kept audits that the auditee said were `tribal` and where they gave the Clearinghouse approval to disseminate all of the data publicly.

This left us with a 100% public dataset.

Then, existing *public* audits were made to look like they were suppressed Tribal audits.

```
update audit_singleauditchecklist
set tribal_data_consent = '{"is_tribal_information_authorized_to_be_public": false, "tribal_authorization_certifying_official_name": "GSA Name", "tribal_authorization_certifying_official_title": "GSA Title"}'
where report_id in (
	SELECT report_id FROM audit_singleauditchecklist
	TABLESAMPLE BERNOULLI(70)
	where general_information->>'auditee_fiscal_period_end' like '%2023%'
	limit 500
)
```

This was done to every audit year from 2016 -> 2023, yielding 4000 "fake" suppressed Tribal audits. This way, in our testing, we have suppressed audits to work with, but the dataset remains 100% public.

The organization type then needed to be updated for those audits.

```
-- Make sure we also set the organization type
-- Should update 4000 rows
update audit_singleauditchecklist
set general_information = jsonb_set(general_information, '{user_provided_organization_type}', '"tribal"', false)
where tribal_data_consent->>'is_tribal_information_authorized_to_be_public' = 'false'
```

We can confirm that we have 4000 Tribal audits:

```
-- Count how many are now tribal; should be 4000
select count(*) from audit_singleauditchecklist
where tribal_data_consent->>'is_tribal_information_authorized_to_be_public' = 'false'
and general_information->>'user_provided_organization_type' = 'tribal'
```

Next, we now empty our dissemination tables and run

```
fac delete_and_regenerate_dissemination_from_intake
```

which

1. Deletes the `dissemination_*` tables
2. Loads all of the `audit_singleauditchecklist` records
3. Runs `sac.disseminate()` on every single record

This is also in the script menu as "Re-disseminate SAC records".

When we are done, we need to confirm that everything migrated correctly.

```
select
	(
		(select count(*) from audit_singleauditchecklist where submission_status = 'disseminated')
		- (select count(*) from dissemination_general)
	) as diff
```

should yield 0. That is, every `sac` that is `disseminated` should also appear in `general`. Hence, the subtraction of those two counts should be zero.

```
select count(*) from audit_singleauditchecklist
	where tribal_data_consent->>'is_tribal_information_authorized_to_be_public' = 'false'
	and submission_status = 'disseminated'
```

will be less than 4000, because some audits that were marked as tribal are actually not complete. In the data in this dump, we get 3909.

Next, we can check that all of the audits that we flagged as fake suppressed audits were disseminated as `is_public=false`.

```
select
	(
		(select count(*) from audit_singleauditchecklist where tribal_data_consent->>'is_tribal_information_authorized_to_be_public' = 'false' and submission_status = 'disseminated')
		- (select count(*) from dissemination_general where is_public = false)
	)  as diff
```

This should difference to zero. There are 91 audits that were faked as suppressed that were not in a disseminated state; hence, we need to be specific about comparing `general` with the number of audits that were complete and presented as "fake" suppressed Tribal audits.

11108 SAC records are in progress, and not disseminated. This is proved out by

```
-- This should be zero
select
	(select (
		(select count(*) from audit_singleauditchecklist)
		- (select count(*) from dissemination_general))
	- (select count(*) from audit_singleauditchecklist where submission_status != 'disseminated')) as diff
```

This means there are 11K records in the SAC table that were *not* disseminated, and therefore not in `dissemination_general`.

At this point, we can dump

* audit_access
* audit_singleauditchecklist
* auth_user
* dissemination_*

and end up with a dataset that is consistent front-to-back. As we complete our "source of truth" migration, we should be able to (for example) implement an API on SOT that produces *exactly* the same data as the existing API. This will be testable locally as well as in lower environments, and ultimately in production.

```
pg_dump \
  -a \
  -F p \
  -f internal-and-external-20250320.dump \
  -d postgres \
  -h localhost \
  -p 5432 \
  -U postgres \
  -w \
  -t audit_singleauditchecklist \
  -t audit_access \
  -t auth_user \
  -t dissemination_additionalein \
  -t dissemination_additionaluei \
  -t dissemination_captext \
  -t dissemination_federalaward \
  -t dissemination_finding \
  -t dissemination_findingtext \
  -t dissemination_general \
  -t dissemination_note \
  -t dissemination_passthrough \
  -t dissemination_secondaryauditor \
  -t audit_ueivalidationwaiver \
  -t audit_sacvalidationwaiver \
  -t audit_singleauditreportfile \
  -t audit_excelfile \
  -t audit_submissionevent
```

### counting records

```
select
	(select count(*) from audit_singleauditchecklist) as sac,
	(select count(*) from audit_access) as access,
	(select count(*) from auth_user) as auth,
	(select count(*) from dissemination_additionalein) as ein,
	(select count(*) from dissemination_additionaluei) as uei,
	(select count(*) from dissemination_captext) as captext,
	(select count(*) from dissemination_federalaward) as fedaward,
	(select count(*) from dissemination_finding) as finding,
	(select count(*) from dissemination_findingtext) as findingtext,
	(select count(*) from dissemination_general) as gen,
	(select count(*) from dissemination_note) as note,
	(select count(*) from dissemination_passthrough) as pass,
	(select count(*) from dissemination_secondaryauditor) as secaud,
  (select count(*) from audit_ueivalidationwaiver) as ueival,
  (select count(*) from audit_sacvalidationwaiver) as sacval,
  (select count(*) from audit_singleauditreportfile) as sarf,
  (select count(*) from audit_excelfile) as excelf,
  (select count(*) from audit_submissionevent) as subevent
```
