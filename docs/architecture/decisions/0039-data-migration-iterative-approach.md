# 38. Data migration: iterative approach

Date: 2024-06-25

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
- [x]   Process
- [ ]   UX

## Related documents/links
[Migrating data from Census to GSA](https://github.com/GSA-TTS/FAC/issues/2789)

[A guide to workbook migration code](https://docs.google.com/document/d/12jcupPwqTc1muIaCsMxKgC33cOPOQQ6V4EoH9OmZGo0/edit)

[Census to GSA Data Migration](https://docs.google.com/document/d/1RK-G8CgR3s3gK2kk9POGo4uMl7NcJnyeyZjlQIfgP_w/edit#heading=h.atn7x8os6xf3)

[Data Transformation Tracking ADR](https://github.com/GSA-TTS/FAC/issues/2913)

## Context
The data migration operation is designed to be a repetitive process, targeting audit reports from the year 2022 and moving backward to 2016. The process starts with Census exporting all relevant FAC data from its database in the form of CSV/SQL files, which are then forwarded to the GSA/FAC team. These files are uploaded to an S3 bucket, from where the data is subsequently downloaded and imported into PostgreSQL tables without undergoing any transformations.  At this point, the core migration algorithm is set to begin the ETL (Extract, Transform, Load) process. During this phase, data is extracted from the PostgreSQL tables, transformed as necessary, and finally loaded into the GSA/FAC dissemination tables. Should there be any failures during migration, the transformation process is updated as necessary and the ETL cycle is iterated upon until all issues are resolved. 
This Architectural Decision Record highlights key aspects of the migration's iterative process.

## Decision

1. **Transferring CSV Files to S3 Bucket**:
   - In local environment, a Django command will transfer the CSV files to minio bucket. This command takes a source location `src` as parameter and `--src` can be set to any accessible path on the disk.
   - In the cloud (cloud.gov), the approach is to directly transfer the files to S3 using 'aws cp' or 'aws sync' since this is a one-time operation.

2. **Data Loading from CSV File to Postgres Table**:
   - CSV files are sequentially loaded into corresponding PostgreSQL tables in small chunks to limit memory usage.
   - This is managed by a Django command with two parameters: `folder` and `chunksize`, where `folder` specifies the S3 bucket path, and `chunksize` the size of data chunks.

3. **Core Migration Process Initiation**:
   - A Django command triggers the migration algorithm with the following parameters `year`, `page_size`, and `pages`.
   - `year` defines the migration scope.
   - `page_size` and `pages` define the size of a data chunk and the number of chunks in a migration iteration.

4. **Data Migration Workflow**:
   - The audit report migration process mirrors the 2023 report submission process, involving:
     * Setting up a SingleAuditChecklist (SAC) object.
     * Retrieving and validating audit report data from Postgres tables.
     * Constructing the general information section of the report in JSON format and loading it into the SAC object upon validation.
     * Creating a workbook object for any other sections of the submission and loading the data from this object into the corresponding sections of the SAC object upon validation.
     * Processing the state machine for certifications.
     * Running cross-validation.
     * Running dissemination logic.
   - Because workbook objects are constructed and used in memory without being saved, security scan is not necessary.
   - If an error (validation error or other error) occurs at any stage of the process, the entire migration process for the audit report being migrated fails. 
   
5. **User Access Consideration**:
   - A default user account (`fac-census-migration-auditee-official` with email `fac-census-migration-auditee-official@fac.gsa.gov`) is dedicated to the migration process.
   - Each ETL cycle checks for this account's existence, using it for submissions or creating it if absent.
   - The default user account is assigned both the `editor` access role and the `certifying_auditee_contact` access role. 
   - The default user account is also assigned the `certifying_auditor_contact` access role with the updated email `fac-census-migration-auditor-official@fac.gsa.gov`

6. **Iterative Process for Data Transformation**:
   - The initial migration attempts will involve minimal data transformation. The goal is to apply only enough data transformation to enable a reasonable percentage of audit reports to migrate successfully.
   - Subsequent iterations will include necessary transformations based on error analysis from previous attempts.
   - Data transformation functions will be specific and modular, designed to avoid altering previously successful migrations.
   - Data transformations become necessary in either of these two scenarios:
	 * When data was optional or not collected in previous audit years but is required for the audit year 2023. This applies, for example, to the audit `UEI`. In such cases, the transformation should first attempt to infer the missing data if there is sufficient data for accurate inference. Otherwise, the goal should be to replace the missing data with a default keyword, such as replacing a missing auditee `UEI` with `GSA_MIGRATION`. Only one of these approaches should be used throughout the entire migration for a given data (for simplicity).
     * When the data format is inconsistent, as is the case with auditee/auditor zip codes, or with Notes to SEFA where a field expected to be of type `Y/N` in 2023 submissions was filled with a sentence in previous years. This also applies to some fields with option lists (like `sp_framework`) where the options in previous years do not always match the 2023 options. In these cases, the transformation will aim to modify the data to meet the 2023 validation requirements.
   - Data transformation must be recorded (see #2913 for more details on recording data changes) .

7. **Management of SAC Records**:
   - The SAC object is required for the dissemination logic and can be removed once dissemination complete. However, if there is a need to rerun dissemination in the future, recreating the SAC object becomes necessary. To avoid redoing the entire process, including recreating the workbook objects and reloading these objects into SAC sections, it might be more efficient to store the SAC objects in a secondary database for future use.
   - Re-running migration for failed attempts does not require the deletion of previously created SAC objects; new attempts automatically overwrite existing records when the `report_id` matches. The same principle applies to dissemination records.
		
8. **Handling Migration Failures**:
   - Analyze failures to determine necessary data transformations.
   - Focus subsequent migrations on previously failed attempts for efficiency.
   
## Consequences

1. Having the ability to run the migration process in chunks of audit reports using a pagination approach makes it possible to parallel process the migration job and save time.
2. It is necessary to record data transformations. However, instead of creating a new database record for each transformation (which will result into a very large table), all transformations related to the same report is aggregated into a single record called InspectionRecord (see #2848). This record is organized by section, similar to the SAC object. 