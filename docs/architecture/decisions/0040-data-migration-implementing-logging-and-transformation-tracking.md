# 40. Data Migration: Implementing Strategic Logging and Transformation Tracking

Date: 2024-09-24

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

[ADR for migrating data from Census to GSA](https://github.com/GSA-TTS/FAC/issues/2789)
[ADR for Census Data Migration: Iterative Approach](https://github.com/GSA-TTS/FAC/issues/2919)
[#2816](https://github.com/GSA-TTS/FAC/issues/2816)
[#2815](https://github.com/GSA-TTS/FAC/issues/2815) 

## Context
The FAC data migration from Census to GSA follows an iterative approach summarized as follows: The migration algorithm is executed, logging details of both successful and unsuccessful migrations. The team then examines these logs, updates the algorithm to address failures, and re-runs the migration for the failed reports. If data transformation is needed for these reports to pass, the algorithm is updated accordingly, and the process is repeated until the migration is complete. This ADR focuses primarily on logging (successful/failed migrations and transformations). For a broader view of the migration process, refer to ADR linked in the previous section.

## Decision
There are three key logging aspects in the historical data migration process:

1. **General Logging:**
   This includes standard logs such as info and debug logs, which are common in most algorithms to provide useful insights during execution. Given the critical nature of this migration task, it's essential to ensure these logs are well-placed and written to aid debugging when needed.

2. **Logging Migration Attempts (Success/Failure):**
   Each migration run will result in some reports successfully migrating and others failing. It's important to record adequate details of both to filter out successfully migrated reports in subsequent iterations. To track this, we'll use a Django model similar to the following:

   ```python
   class ReportMigrationStatus(models.Model):
       audit_year = models.TextField(blank=True, null=True)
       dbkey = models.TextField(blank=True, null=True)
       run_datetime = models.DateTimeField(default=timezone.now)
       migration_status = models.TextField(blank=True, null=True)
   ```
   `audit_year` and `dbkey` will store the AUDITYEAR and DBKEY, respectively. `run_datetime` will record the migration attempt's timestamp, and `migration_status` will indicate whether the report was successfully migrated.

   **MigrationErrorDetail Model:**
   This model will link to `ReportMigrationStatus` via a foreign key relationship, enabling a direct association between a migration attempt and its corresponding error details. 
   ```python
   class MigrationErrorDetail(models.Model):
       report_migration_status_id = models.ForeignKey(ReportMigrationStatus, on_delete=models.CASCADE)
       tag = models.TextField(blank=True, null=True)
       exception_class = models.TextField(blank=True, null=True)
       detail = models.TextField(blank=True, null=True)
   ```
   `tag` will provide a tag for the error, `exception_class` will provide the class of the error, 'detail' will contain the full description of the error.

3. **Logging Data Transformations (Change Logs):**
   This logging is crucial for documenting any modifications to the data throughout the migration process. It is vital to record the state of the data both before and after transformation, along with any other pertinent details for auditing purposes. The following Django model is utilized to track these changes:
   ```python
   class MigrationInspectionRecord(models.Model):
      audit_year = models.TextField(blank=True, null=True)
      dbkey = models.TextField(blank=True, null=True)
      report_id = models.TextField(blank=True, null=True)
      run_datetime = models.DateTimeField(default=timezone.now)
      finding_text = JSONField(blank=True, null=True)
      additional_uei  = JSONField(blank=True, null=True)
      additional_ein  = JSONField(blank=True, null=True)
      finding  = JSONField(blank=True, null=True)
      federal_award  = JSONField(blank=True, null=True)
      cap_text  = JSONField(blank=True, null=True)
      note  = JSONField(blank=True, null=True)
      passthrough  = JSONField(blank=True, null=True)
      general  = JSONField(blank=True, null=True)
      secondary_auditor  = JSONField(blank=True, null=True)
   ```
   The team has opted for this model as it appears more flexible and allows the use of nested JSON objects within `census_data` to represent the relationships between tables, columns, and data values. Below is a sample:

   ```json
    {
        "census_data": [
            {
                "column": "sample_col1",
                "value": "sample_data1"
            },
            {
                "column": "sample_col2",
                "value": "sample_data2"
            }
        ],
        "gsa_fac_data": {
            "field": "sample_gsa_fac_field",
            "value":  "sample_value"
        },
        "transformation_functions": "function_name"
    }
   ```

**Database Tables Strategy**
The GSA/FAC application relies on a default database for all its data persistence requirements. During the migration process, there was a consideration to integrate an additional database into the application's infrastructure. This new database was intended to host tables that might not stay active post-migration. However, anticipating scenarios where re-running the data migration could become necessary, the decision was made to maintain all data in a live state for the time being. Consequently, the plan to introduce a second database was set aside.

## Consequences
- The `ReportMigrationStatus` model tracks migration status and makes it possible to compute the success-to-failure ratio after each iteration. Ideally, the failure rate should be 0% after all iterations for a given audit year.
- The `MigrationInspectionRecord` model provides a comprehensive record of data changes for audit purposes.
