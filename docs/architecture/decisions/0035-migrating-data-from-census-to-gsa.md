# 35. Migrating Data from Census to GSA

Date: 2024-05-24

## Status

Accepted

## Areas of impact

- [ ]   Compliance
- [ ]   Content
- [ ]   CX
- [ ]   Design
- [x]   Engineering
- [ ]   Policy
- [ ]   Product
- [ ]   Process
- [ ]   UX

## Related documents/links
The following documents serve as sources for the thinking in this ADR.
* [Initial migration principles thoughts](https://docs.google.com/document/d/1pBUBLD2MGt-zEMwaaHIcLJT8ZqV0iPRnhiSkL3TIlu4/edit#heading=h.4f7j3ydfccdm)
* [E2E migration code](https://docs.google.com/document/d/12jcupPwqTc1muIaCsMxKgC33cOPOQQ6V4EoH9OmZGo0/edit#heading=h.wn0o8brht5dv)
* [Migration plan evolution](https://docs.google.com/document/d/1qrCn5jjTnBV831_cZswPrIgbjbQoECLSD0TEAW1PFeg/edit) 

## Context

GSA is migrating FAC data from Census. GSA is charged with improving the quality of the data in the FAC, as it plays a critical role in financial oversight across Federal government. Since October 2, 2023 (just over one month), the GSA FAC has collected approximately 2700 audits covering over $29B (billion) dollars.

The data at Census covers *many trillions* of dollars. The migration of that data must be carried out with the same care and attention to detail that was brought to bear on the new data intake. As we migrate and (as we can) improve the quality of data being migrated, we will maintain a complete record of any and all changes made, such that the original data could, if needed, be reconstructed from the records we maintain. 

## Decision

There are two "algorithms" we want to follow in our migration. These algorithms will guide our implementation work.

### Migrating Census data

The data migration from Census will be enacted *submission-by-submission* not *row-by-row*. To do this, we will use the current FAC not just as a system to collect new audits, but also as a system to migrate the old data. We will do this by:

**ALGORITHM**: Census data migration pass (**MIGRATIONPASS**)

1. For a given AUDITYEAR, beginning with 2022 and counting backwards to 2016
   1. Select a DBKEY and AUDITYEAR combination.
   2. Use data from Census to populate GSA submission forms and workbooks.
   3. Pass that data through our validations into the GSA's internal data representation.
   4. Run cross-validations on the data.
   5. Disseminate the data from our internal representation to our dissemination tables.
   6. If the validation and dissemination is successful, 
      1. Verify the data we took in was properly disseminated via the API.
      2. In the event of failure at any step, log the DBKEY and AUDITYEAR for future processing.
   7. GOTO step 1.1 until no more DBKEYs exist for the given AUDITYEAR
2. Go to step 1 until we have migrated all UG data.

In this regard, every data migration will either 1) succeed, and we will verify that the migration of data was succsesfull by checking results in the API, or 2) fail, in which case no data will be migrated for that particular DBKEY/AUDITYEAR.

The above algorithm will be run more than once. In the first instance, we will run with as few changes to the data as possible. The changes we will make will be those that are **strictly necessary**. By this, we mean those changes that do not alter semantics, but are necessary for syntactic reasons to transform data from Census to GSA tables.

### Changing data in the migration

If we name the above algorithm `MIGRATIONPASS`, then our full migration will look like this:

**ALGORITHM**: An iterative migration strategy (**ITERATIVEMIGRATION**)

1. Run `MIGRATIONPASS`
   1. Log records that did not migrate.
2. Update data transformation functions to enact more inclusive/aggressive data transformations.
3. GOTO step 1.

The first time we run `MIGRATIONPASS`, we might migrate 10% of the data, or we might migrate 80% of the data. When we are done, we will know exactly what DBKEY/AUDITYEAR combinations failed to migrate.

In the first time through, some data will need to be changed. We will only implement those functions that are strictly necessary to migrate data. Mapping `Y&N` to `Both` is a good example of a strictly necessary change: it does not introduce a change in meaning, but it is strictly necessary in order to correctly populate GSA workbooks.

#### Example: transforming `Y&N` to `Both`

There is a field in the `Notes to SEFA` that is either `Y`, `N` or `Y&N`. GSA instead chose to collect this as `Y`, `N`, or `Both`. 

When we map Census to GSA, we might write a transformation function that looks like this:

```
def is_deminimus_to_is_deminimus_rate_used(source_column, destination_column, original_value):
    if original_value == 'Y':
        return UnchangedRecord(source_column, destination_column, original_value)
    elif original_value == 'N':
        return UnchangedRecord(source_column, destination_column, original_value)
    elif original_value == 'Y&N':
        return ChangedRecord(source_column, destination_column, original_value, 'Both')
    else:
        return MigrationException(...)
```

This function would be executed as the cell in the GSA workbook is populated. If an `UnchangedRecord` structure is returned, then we would insert the value into the workbook and continue. If a `ChangedRecord` is returned, we would need to do two things:

1. Log the change in a `ChangedRecords` table with a `report_id`, the source column, destination column, original value, and destination value.
2. Insert the new value into the workbook.

Additional data may want to be logged: a timestamp, and possibly a [Github SHA hash to the version of the code that carried out the transformation](https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script). 

##### Why?

We are migrating data that is in *active use* by GAO, IGs, and resolution officials across Federal government, as well as many public entities who consume this data for their own work. We will work to improve the quality of the data, and in doing so, we will be fastidious in tracking *exactly* how we enacted transformations as we proceed.

It should be possible, given the `ChangeRecords` table and a disseminated record, to reconstruct the original Census data faithfully. It may not be *easy* to enact that reconstruction, but it should be the case that anyone looking at the migrated record and the collection of change records associated with it that the transformations enacted are obvious to the reader, and make completely clear how we enacted any changes to the source data as part of our migration work.

#### Repetition of ITERATIVEMIGRATION

After a full run of MIGRATIONPASS, we will evaluate the records that failed to migrate. We will then write the next set of mapping functions necessary to transfer more data from Census to GSA. More aggressive transformations may become necessary; for example, ALNs may need to be rewritten, and changes logged, as some ALNs are very, very far from reasonable/accurate.

With each successive pass, fewer records should fail to migrate.

We will evaluate after each pass of ITERATIVEMIGRATION, and decide when and where we have done due dilligence. There will come a point of diminishing returns, where the Census data remaining may be of such low quality that all we can do is publish the remaining records as a collection outside of the system. Or, another solution may present itself; either way, that is the subject of a future ADR.

## Consequences

1. Data will not necessarily make the migration without transformation. We will work to improve the data quality through the migration process while logging what we change in the name of quality.
2. We will migrate data of the highest quality first. This means some percentage of the data will migrate in the first pass, but not all. Then, we will iterate on our migration functions, accepting more data through. This means the migration is a process.

