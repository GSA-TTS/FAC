# 38. Data Migration Change Record

Date: 2024-06-25

## Status

Accepted

## Areas of impact

- [ ]   Compliance
- [ ]   Content
- [ ]   CX
- [ ]   Design
- [x]   Engineering
- [x]   Policy
- [ ]   Product
- [ ]   Process
- [ ]   UX

## Related documents/links

- [Migrating data from Census to GSA
](https://github.com/GSA-TTS/FAC/issues/2848)
- [Logging and Transformation Tracking](https://github.com/GSA-TTS/FAC/issues/2909)
- [Data discrepancy compilation](https://github.com/GSA-TTS/FAC/issues/2912)
- [Completion of the ADR closes](https://github.com/GSA-TTS/FAC/issues/2909)

## Context
The Census to GSA migration will require that some data be altered to improve its quality. The aim of this ADR is to establish a strategy for maintaining a complete record of any and all changes made, such that the original data can be reconstructed. In doing so, we are annotating where historical data fails to meet the validations in place with the FAC today.

## Decision

1. **Logging Migration Attempts (Success/Failure):**
   Each migration run will result in some reports successfully migrating and others failing. It's important to record adequate details of both to filter out successfully migrated reports in subsequent iterations. To track this, we'll use a Django model similar to the following:

   ```python
   class ReportMigrationStatus(models.Model):
       audit_year = models.TextField(blank=True, null=True)
       dbkey = models.TextField(blank=True, null=True)
       run_datetime = models.DateTimeField(default=timezone.now)
       migration_status = models.TextField(blank=True, null=True)
   ```
   `audit_year` and `dbkey` will store the AUDITYEAR and DBKEY, respectively. `run_datetime` will record the migration attempt's timestamp, and `migration_status` will indicate whether the report was successfully migrated.

2. **MigrationErrorDetail Model:**
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
   This logging is crucial for documenting any modifications to the data throughout the migration process. It is vital to record the state of the data both before and after transformation, along with any other pertinent details for auditing purposes. The `MigrationInspectionRecord` model is utilized to track these changes:


    ```python
    class MigrationInspectionRecord(models.Model):
        audit_year = models.TextField(blank=True, null=True)
        dbkey = models.TextField(blank=True, null=True)
        report_id = models.TextField(blank=True, null=True)
        run_datetime = models.DateTimeField(default=timezone.now)
        finding_text = models.JSONField(blank=True, null=True)
        additional_uei = models.JSONField(blank=True, null=True)
        additional_ein = models.JSONField(blank=True, null=True)
        finding = models.JSONField(blank=True, null=True)
        federal_award = models.JSONField(blank=True, null=True)
        cap_text = models.JSONField(blank=True, null=True)
        note = models.JSONField(blank=True, null=True)
        passthrough = models.JSONField(blank=True, null=True)
        general = models.JSONField(blank=True, null=True)
        secondary_auditor = models.JSONField(blank=True, null=True)
    ```

    Example `MigrationInspectionRecord`:
    ```json
    {
        "audit_year": "2022",
        "dbkey": "255585",
        "report_id": "2022-02-CENSUS-0000255585",
        "run_datetime": "2008-10-29 14:56:59",
        "general": [
        {
            "census_data": [
            {
                "value": "Non-profit",
                "column": "ENTITY_TYPE"
            }
            ],
            "gsa_fac_data": {
            "field": "entity_type",
            "value": "non-profit"
            },
            "transformation_functions": [
            "xform_entity_type"
            ]
        },
        ... // More general field changes
        ],
    ... // More models from dissemination
    }
    ```
    Here, every report being migrated will yield a single `MigrationInspectionRecord`, where each section field will hold the data transformation details related to that section.

### Census -> GSA changes to be recorded

We have determined it to be safe to ignore some generalized changes, such as upper/lowercasing, or using default keywords, to limit the amount of transformation data stored. Instead, these changes will be available for users to see in our documentation, while more field-specific and involved changes will be recorded in `InspectionRecord`s. Transformations needed for each field is being tracked [here](https://github.com/GSA-TTS/FAC/issues/2912).

## Following the work

The work of the migration takes place largely in `census_historical_migration` in the repository. As of June 2024, that path can be found here:

https://github.com/GSA-TTS/FAC/tree/dda11bdfd31a000601e427379a3fac6ee9e7f1f8

## Consequences
- The `ReportMigrationStatus` model tracks migration status and makes it possible to compute the success-to-failure ratio after each iteration. Ideally, the failure rate should be 0% after all iterations for a given audit year.
- The `MigrationInspectionRecord` model provides a comprehensive record of data changes for audit purposes.
