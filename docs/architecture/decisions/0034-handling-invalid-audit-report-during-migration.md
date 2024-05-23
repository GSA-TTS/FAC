# 34. Handling Incorrect Audit Reports During Migration

Date: 2024-05-17

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
- [Django models] (https://github.com/GSA-TTS/FAC/issues/3681)
- Other related tickets include: #3856, #3709, #3694, #3688, #3686, #3696 

## Context

As we migrate audit reports from Census table files to GSA/FAC database, we encounter a subset of reports with data validation issues that prevent their easy curation during the migration process. The complexity and nature of these data issues necessitate a strategy where these reports are migrated "as is", without undergoing validation or correction initially. This approach is deemed necessary to ensure all records are preserved intact for subsequent analysis and possible rectification.

## Decision

We propose to introduce two new Django models to handle these specific cases effectively:

1. *InvalidAuditRecord**:
   - This model acts similarly to the existing `MigrationInspectionRecord`, but instead of holding change records, it holds records that have been migrated as is, without validation or changes.
   - The model will record the basic metadata of each report and the specific reasons it was migrated without validation.

2. **IssueDescriptionRecord**:
   - This model will capture detailed descriptions of the issues associated with each record, explaining why the reports could not be validated or corrected during the initial migration.
   - Each `InvalidAuditRecord` can have one or more associated `IssueDescriptionRecord` entries, establishing a parent-child relationship.

### Proposed Model Structures

#### InvalidAuditRecord
```python
class InvalidAuditRecord(models.Model):
    audit_year = models.TextField(blank=True, null=True)
    dbkey = models.TextField(blank=True, null=True)
    report_id = models.TextField(blank=True, null=True)
    run_datetime = models.DateTimeField(default=timezone.now)
    finding_text = models.JSONField(blank=True, null=True)  # Described below
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

#### IssueDescriptionRecord
```python
class IssueDescriptionRecord(models.Model):
    issue_detail = models.TextField()
    issue_tag = models.TextField()
    skipped_validation_method = models.TextField()

```

### JSONField Content Structure for `InvalidAuditRecord`
```json
{
    "census_data": [{
            "value": "some value",
            "column": "some column name"
        }
    ],
    "issue_tag": "some_tag_name"
}
```

## Consequences

By adopting this two-model approach:

- We ensure that all audit reports, regardless of their initial data quality, are migrated and stored within the new system.
- The detailed logging and description of issues provide a robust foundation for future efforts aimed at correcting or understanding the compromised data.
- This approach also allows for greater flexibility and clarity in handling complex data issues, as each problematic record's specifics are documented thoroughly and can be addressed individually when resources or solutions become available.

This ADR provides a structured and transparent method for managing the migration of problematic audit reports, ensuring accountability and traceability throughout the process.
