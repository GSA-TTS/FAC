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

https://drive.google.com/drive/folders/1gUsqD31Pkd17CruE4PWwwPKJVUssYNnI

Grab the file `internal-and-external-20250320.zip` (~1GB). Decompress it to `internal-and-external-20250320.dump` (~8GB).

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

Put it in util/load_public_dissem_data/data (a child of this directory).

We use a subdirectory to make the .gitignore work easier/safer.

# truncate and load

Use the menu script in this folder.

```
./menu.bash
```

This will give you three options:

```
1) Truncate tables
2) Load data
3) Check row counts
3) Quit
```

## truncate tables

This runs the following SQL:

```
  truncate audit_access,
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
    dissemination_secondaryauditor
    cascade;
```

This effectively cleans all data that we might be working and testing with. 

## load data

This will reload:

* audit_access
* audit_singleauditchecklist
* auth_user
* dissemination_*

## check counts

This verifies the row counts in every table we loaded. 

```
1) Truncate tables
2) Load data
3) Check row counts
4) Quit
Please enter your choice: 3
Checking counts
[PASS] audit_singleauditchecklist has 354222 rows
[PASS] audit_access has 1195595 rows
[PASS] auth_user has 75461 rows
[PASS] dissemination_additionalein has 59251 rows
[PASS] dissemination_additionaluei has 15101 rows
[PASS] dissemination_captext has 116694 rows
[PASS] dissemination_federalaward has 5811948 rows
[PASS] dissemination_finding has 507895 rows
[PASS] dissemination_findingtext has 120290 rows
[PASS] dissemination_general has 343114 rows
[PASS] dissemination_note has 530405 rows
[PASS] dissemination_passthrough has 4025800 rows
[PASS] dissemination_secondaryauditor has 1803 rows
```

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
  -t dissemination_secondaryauditor
```